# backend/apps/kyc/views.py

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from .models import (
    Customer,
    KYCSession,
    KYCDocument,
    KYCVerificationResult,
    KYCAttempt,
    KYCIndex,
    STAGE_CHOICES,
)

from .serializers import (
    CustomerSerializer,
    KYCSessionSerializer,
    KYCDocumentSerializer,
    KYCVerificationResultSerializer,
    StartKYCSessionSerializer,
    SelectDocumentSerializer,
    UploadDocumentSerializer,
    UploadPhotoSerializer,
    UploadLiveSelfieSerializer,
)


# ----------------------------------------------------------------
# Helper: log attempts
# ----------------------------------------------------------------
def log_attempt(customer, stage_key: str, success: bool):
    previous = KYCAttempt.objects.filter(customer=customer, stage=stage_key).count()
    KYCAttempt.objects.create(
        customer=customer,
        stage=stage_key,
        attempt_number=previous + 1,
        success=success,
    )


# ----------------------------------------------------------------
# 0. Start KYC Session
# ----------------------------------------------------------------
class StartKYCSessionView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = StartKYCSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]
        email = serializer.validated_data.get("email")
        full_name = serializer.validated_data.get("full_name")

        customer, created = Customer.objects.get_or_create(
            phone=phone,
            defaults={"email": email, "full_name": full_name},
        )

        if not created:
            changed = False
            if email and customer.email != email:
                customer.email = email
                changed = True
            if full_name and customer.full_name != full_name:
                customer.full_name = full_name
                changed = True
            if changed:
                customer.save()

        session = KYCSession.objects.create(customer=customer)

        return Response(
            {
                "message": "KYC session started",
                "customer": CustomerSerializer(customer).data,
                "session": KYCSessionSerializer(session).data,
            },
            status=status.HTTP_201_CREATED,
        )


# ----------------------------------------------------------------
# 1. Select Document Type
# ----------------------------------------------------------------
class SelectDocumentView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = SelectDocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session_id = serializer.validated_data["session_id"]
        doc_type = serializer.validated_data["doc_type"]

        session = get_object_or_404(KYCSession, id=session_id)

        log_attempt(session.customer, "SELECT_DOC", True)
        session.advance_to("SCAN_DOC")

        return Response(
            {
                "message": "Document type selected successfully",
                "selected_doc_type": doc_type,
                "session": KYCSessionSerializer(session).data,
            },
            status=status.HTTP_200_OK,
        )


# ----------------------------------------------------------------
# 2 & 3. Upload Document (NO ATTEMPT LIMIT)
# ----------------------------------------------------------------
class UploadDocumentView(APIView):
    """
    POST /api/kyc/upload-document/
    fields: session_id, doc_type, id_number, file
    """

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        data["session_id"] = data.get("session_id", "").strip()

        serializer = UploadDocumentSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        session = get_object_or_404(KYCSession, id=serializer.validated_data["session_id"])
        customer = session.customer

        doc_type = serializer.validated_data["doc_type"]
        id_number = serializer.validated_data["id_number"]
        id_hash = serializer.validated_data["id_hash"]
        file = serializer.validated_data["file"]

        # ------------ DUPLICATE CHECK -------------------
        existing = KYCIndex.objects.filter(id_hash=id_hash).exclude(customer=customer).first()
        if existing:
            log_attempt(customer, "UPLOAD_DOC", False)
            return Response(
                {"detail": "This document is already used by another customer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ------------ UPDATE OR CREATE DOCUMENT INDEX -------------
        KYCIndex.objects.update_or_create(
            id_hash=id_hash,
            defaults={
                "doc_type": doc_type,
                "customer": customer,
            }
        )

        # ------------ SAVE KYCDocument -------------------
        try:
            kyc_doc = KYCDocument.objects.create(
                customer=customer,
                session=session,
                doc_type=doc_type,
                id_number=id_number,
                file=file,
                status="UPLOADED",
            )
            success = True
        except Exception as e:
            success = False
            log_attempt(customer, "UPLOAD_DOC", success)
            return Response(
                {"detail": f"Error saving document: {e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Log attempt but DO NOT BLOCK further uploads
        log_attempt(customer, "UPLOAD_DOC", success)

        session.advance_to("UPLOAD_DOC")

        return Response(
            {
                "message": "Document uploaded successfully",
                "document": KYCDocumentSerializer(kyc_doc).data,
                "session": KYCSessionSerializer(session).data,
            },
            status=status.HTTP_201_CREATED,
        )


# ----------------------------------------------------------------
# 4. Upload Photo
# ----------------------------------------------------------------
@api_view(["POST"])
def upload_photo_view(request):
    serializer = UploadPhotoSerializer(data=request.data)
    if serializer.is_valid():
        session = serializer.save()

        log_attempt(session.customer, "SELFIE", True)

        return Response(
            {
                "message": "Photograph received and saved",
                "session": KYCSessionSerializer(session).data,
            },
            status=status.HTTP_200_OK,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ----------------------------------------------------------------
# 5. Upload Live Selfie + PAN + Aadhaar Required
# ----------------------------------------------------------------
@api_view(["POST"])
def upload_live_selfie_view(request):
    serializer = UploadLiveSelfieSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    session = serializer.save()
    customer = session.customer

    # RULE 1: Photo must exist
    if not session.photo:
        return Response(
            {"detail": "Passport-size photograph must be uploaded before live selfie."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # RULE 2: Must have at least one uploaded document
    documents = KYCDocument.objects.filter(session=session)
    if not documents.exists():
        return Response(
            {"detail": "No documents found. Upload PAN and Aadhaar first."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # RULE 3: MUST HAVE BOTH PAN & AADHAAR
    has_pan = documents.filter(doc_type="PAN").exists()
    has_aadhaar = documents.filter(doc_type="AADHAAR").exists()

    if not has_pan or not has_aadhaar:
        missing = []
        if not has_pan:
            missing.append("PAN")
        if not has_aadhaar:
            missing.append("AADHAAR")

        return Response(
            {"detail": f"KYC requires both PAN and Aadhaar. Missing: {', '.join(missing)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ALL GOOD → Simulated verification
    log_attempt(customer, "VERIFY", True)

    last_doc = documents.order_by("-uploaded_at").first()

    verification = KYCVerificationResult.objects.create(
        document=last_doc,
        duplicate=False,
        face_match_score=0.95,
        passport_valid=True if last_doc.doc_type == "PASSPORT" else None,
        vendor_response={
            "info": "Simulated verification. No external vendor call done.",
            "live_selfie_used": True,
        },
        status="SUCCESS",
    )

    session.advance_to("VERIFY")
    session.advance_to("COMPLETED")

    return Response(
        {
            "message": "KYC verification completed (simulated).",
            "session": KYCSessionSerializer(session).data,
            "verification": KYCVerificationResultSerializer(verification).data,
        },
        status=status.HTTP_200_OK,
    )


# ----------------------------------------------------------------
# Extra: Get Session Status
# ----------------------------------------------------------------
class KYCSessionDetailView(APIView):
    def get(self, request, session_id, *args, **kwargs):
        session = get_object_or_404(KYCSession, id=session_id)
        return Response(
            {"session": KYCSessionSerializer(session).data},
            status=status.HTTP_200_OK,
        )
