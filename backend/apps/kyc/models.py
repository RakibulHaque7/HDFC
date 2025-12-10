from django.db import models
from django.utils import timezone
import uuid
import hashlib   # <-- REQUIRED FOR DUPLICATE DETECTION

# ---------------- Document Type Options ----------------

DOC_TYPES = [
    ('AADHAAR', 'Aadhaar'),
    ('PAN', 'PAN'),
    ('PASSPORT', 'Passport'),
    ('VOTER', 'Voter ID'),
]


# ---------------- Customer ----------------

class Customer(models.Model):
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(null=True, blank=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.full_name or self.phone}"


# ---------------- Government Document ----------------

class GovDocument(models.Model):
    doc_type = models.CharField(max_length=20, choices=DOC_TYPES)
    doc_number = models.CharField(max_length=64, unique=True)
    meta = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.doc_type} - {self.doc_number}"


# ---------------- UPDATED KYC Document ----------------

class KYCDocument(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='documents'
    )
    session = models.ForeignKey(
        "KYCSession",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="documents"
    )

    doc_type = models.CharField(max_length=20, choices=DOC_TYPES)

    # NEW FIELD — MANDATORY FOR PAN & AADHAAR
    id_number = models.CharField(max_length=32)

    file = models.FileField(upload_to='kyc_docs/')
    ocr_data = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, default='PENDING')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Only ONE document of each type allowed per session
        unique_together = ('session', 'doc_type')

    def __str__(self):
        return f"{self.customer} - {self.doc_type} ({self.id_number})"


# ---------------- Attempt Logging ----------------

STAGE_CHOICES = [
    ('SELECT_DOC', 'Select Document'),
    ('SCAN_DOC', 'Scan Document'),
    ('UPLOAD_DOC', 'Upload Document'),
    ('SELFIE', 'Selfie Capture'),
    ('VERIFY', 'Verify'),
]

class KYCAttempt(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='attempts'
    )
    stage = models.CharField(max_length=30, choices=STAGE_CHOICES)
    attempt_number = models.IntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)

    class Meta:
        indexes = [models.Index(fields=['customer', 'stage'])]
        ordering = ['-timestamp']


# ---------------- UPDATED KYC Index (Duplicate Detection) ----------------

class KYCIndex(models.Model):
    doc_type = models.CharField(max_length=20, choices=DOC_TYPES)
    id_hash = models.CharField(max_length=64, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.doc_type} index for {self.customer_id}"

    @staticmethod
    def normalize_id(doc_type: str, id_number: str) -> str:
        # Clean formatting: remove spaces, uppercase
        return (id_number or "").upper().replace(" ", "").strip()

    @classmethod
    def make_hash(cls, doc_type: str, id_number: str) -> str:
        normalized = cls.normalize_id(doc_type, id_number)
        key = f"{doc_type}:{normalized}"
        return hashlib.sha256(key.encode("utf-8")).hexdigest()


# ---------------- Verification Results ----------------

class KYCVerificationResult(models.Model):
    document = models.OneToOneField(
        KYCDocument, on_delete=models.CASCADE, related_name='verification'
    )
    duplicate = models.BooleanField(default=False)
    face_match_score = models.FloatField(null=True, blank=True)
    passport_valid = models.BooleanField(null=True, blank=True)
    vendor_response = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, default='PENDING')
    processed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Verification for {self.document} - {self.status}"


# ---------------- KYC Session (Flow Controller) ----------------

SESSION_STAGE_CHOICES = [
    ('SELECT_DOC', 'Select Document'),
    ('SCAN_DOC', 'Scan Document'),
    ('UPLOAD_DOC', 'Upload Document'),
    ('SELFIE', 'Selfie Capture'),
    ('VERIFY', 'Verify'),
    ('COMPLETED', 'Completed'),
    ('FAILED', 'Failed'),
]

class KYCSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='kyc_sessions'
    )

    current_stage = models.CharField(
        max_length=30, choices=SESSION_STAGE_CHOICES, default='SELECT_DOC'
    )

    photo = models.ImageField(upload_to='kyc_photos/', null=True, blank=True)
    live_selfie = models.ImageField(upload_to='kyc_selfies/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_error = models.TextField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    progress_percent = models.IntegerField(default=0)

    def advance_to(self, next_stage):
        self.current_stage = next_stage
        order = {s[0]: i for i, s in enumerate(SESSION_STAGE_CHOICES)}
        max_idx = len(SESSION_STAGE_CHOICES) - 1
        self.progress_percent = int((order.get(next_stage, 0) / max_idx) * 100)

        if next_stage == 'COMPLETED':
            self.completed = True

        self.updated_at = timezone.now()
        self.save()

    def as_dict(self):
        return {
            "session_id": str(self.id),
            "customer_id": self.customer.id,
            "current_stage": self.current_stage,
            "progress_percent": self.progress_percent,
            "last_error": self.last_error,
            "completed": self.completed,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "photo": self.photo.url if self.photo else None,
            "live_selfie": self.live_selfie.url if self.live_selfie else None,
        }

    def __str__(self):
        return f"KYCSession {self.id} ({self.customer}) - {self.current_stage}"
