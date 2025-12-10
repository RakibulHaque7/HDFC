# backend/apps/kyc/urls.py

from django.urls import path
from .views import (
    StartKYCSessionView,
    SelectDocumentView,
    UploadDocumentView,
    upload_photo_view,        # 👈 updated import (function-based view)
    upload_live_selfie_view,  # 👈 updated import (function-based view)
    KYCSessionDetailView,
)

urlpatterns = [
    # 0. Start session
    path("start-session/", StartKYCSessionView.as_view(), name="kyc-start-session"),

    # 1. Select document type
    path("select-document/", SelectDocumentView.as_view(), name="kyc-select-document"),

    # 2 & 3. Upload document (scan + upload)
    path("upload-document/", UploadDocumentView.as_view(), name="kyc-upload-document"),

    # 4. Upload static photograph (now SAVED to DB)
    path("upload-photo/", upload_photo_view, name="kyc-upload-photo"),

    # 5. Upload live selfie + verify (now SAVED to DB)
    path("upload-live-selfie/", upload_live_selfie_view, name="kyc-upload-live-selfie"),

    # Extra: Check session status
    path("session/<uuid:session_id>/", KYCSessionDetailView.as_view(), name="kyc-session-detail"),
]
