# backend/apps/kyc/serializers.py

from rest_framework import serializers
from .models import (
    Customer,
    KYCSession,
    KYCDocument,
    KYCVerificationResult,
    KYCIndex,
    DOC_TYPES,
)
from .validators import validate_document_number  # used only in KYCDocumentSerializer


# ---------------------------------------------------------
#  Base model serializers (API response)
# ---------------------------------------------------------

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "phone", "email", "full_name", "created_at"]


class KYCSessionSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    session_id = serializers.UUIDField(source="id", read_only=True)

    class Meta:
        model = KYCSession
        fields = [
            "id",
            "session_id",
            "customer",
            "current_stage",
            "progress_percent",
            "last_error",
            "completed",
            "created_at",
            "updated_at",
            "photo",
            "live_selfie",
        ]


# ---------------------------------------------------------
#  KYCDocument Serializer (response only)
# ---------------------------------------------------------

class KYCDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCDocument
        fields = [
            "id",
            "customer",
            "session",
            "doc_type",
            "id_number",
            "file",
            "ocr_data",
            "status",
            "uploaded_at",
        ]
        read_only_fields = ["ocr_data", "status", "uploaded_at"]

    def validate(self, attrs):
        """
        Still supports your old validator. Safe to keep.
        """
        instance = getattr(self, "instance", None)

        doc_type = attrs.get("doc_type") or (instance.doc_type if instance else None)
        id_number = attrs.get("id_number") or (instance.id_number if instance else None)

        if not doc_type:
            raise serializers.ValidationError({"doc_type": "doc_type is required."})

        if not id_number:
            raise serializers.ValidationError({"id_number": "id_number is required."})

        cleaned_id = validate_document_number(doc_type, id_number)
        attrs["id_number"] = cleaned_id
        return attrs


# ---------------------------------------------------------
#  KYC Verification Result Serializer
# ---------------------------------------------------------

class KYCVerificationResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCVerificationResult
        fields = [
            "id",
            "document",
            "duplicate",
            "face_match_score",
            "passport_valid",
            "vendor_response",
            "status",
            "processed_at",
        ]


# ---------------------------------------------------------
#  Simple Request Serializers
# ---------------------------------------------------------

class StartKYCSessionSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    email = serializers.EmailField(required=False, allow_blank=True)
    full_name = serializers.CharField(required=False, allow_blank=True)


class SelectDocumentSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    doc_type = serializers.ChoiceField(choices=DOC_TYPES)


# =========================================================
#  🔥 FINAL UPDATED UploadDocumentSerializer (your request)
# =========================================================

class UploadDocumentSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    doc_type = serializers.ChoiceField(choices=DOC_TYPES)
    id_number = serializers.CharField(max_length=32)
    file = serializers.FileField()

    PAN_REGEX = r"^[A-Z]{5}[0-9]{4}[A-Z]$"
    AADHAAR_REGEX = r"^[0-9]{12}$"

    def validate(self, data):
        doc_type = data["doc_type"]
        raw_id = data["id_number"]

        # ---------- Normalize ----------
        id_number = raw_id.upper().replace(" ", "").strip()

        # ---------- Validate PAN ----------
        if doc_type == "PAN":
            import re
            if not re.match(self.PAN_REGEX, id_number):
                raise serializers.ValidationError(
                    {"id_number": "Invalid PAN format. Expected ABCDE1234F"}
                )

        # ---------- Validate Aadhaar ----------
        if doc_type == "AADHAAR":
            import re
            if not re.match(self.AADHAAR_REGEX, id_number):
                raise serializers.ValidationError(
                    {"id_number": "Invalid Aadhaar format. Must be 12 digits."}
                )

        # ---------- Generate Hash ----------
        id_hash = KYCIndex.make_hash(doc_type, id_number)

        # Add to validated data for use in views.py
        data["id_number"] = id_number
        data["id_hash"] = id_hash

        return data


# ---------------------------------------------------------
#  Photo Upload Serializer
# ---------------------------------------------------------

class UploadPhotoSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    photo = serializers.ImageField()

    def validate(self, attrs):
        session_id = attrs.get("session_id")

        try:
            session = KYCSession.objects.get(id=session_id)
        except KYCSession.DoesNotExist:
            raise serializers.ValidationError({"session_id": "Invalid session ID"})

        if session.completed:
            raise serializers.ValidationError(
                {"session_id": "This KYC session is already completed."}
            )

        attrs["session"] = session
        return attrs

    def save(self):
        session: KYCSession = self.validated_data["session"]
        photo = self.validated_data["photo"]

        session.photo = photo

        if session.current_stage in ["SELECT_DOC", "SCAN_DOC", "UPLOAD_DOC"]:
            session.advance_to("SELFIE")
        else:
            session.save()

        return session


# ---------------------------------------------------------
#  Live Selfie Upload Serializer
# ---------------------------------------------------------

class UploadLiveSelfieSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    live_selfie = serializers.ImageField()

    def validate(self, attrs):
        session_id = attrs.get("session_id")

        try:
            session = KYCSession.objects.get(id=session_id)
        except KYCSession.DoesNotExist:
            raise serializers.ValidationError(
                {"session_id": "Invalid session ID"}
            )

        if session.completed:
            raise serializers.ValidationError(
                {"session_id": "This KYC session is already completed."}
            )

        attrs["session"] = session
        return attrs

    def save(self):
        session: KYCSession = self.validated_data["session"]
        selfie = self.validated_data["live_selfie"]

        session.live_selfie = selfie

        if session.current_stage != "VERIFY":
            session.advance_to("VERIFY")
        else:
            session.save()

        return session
