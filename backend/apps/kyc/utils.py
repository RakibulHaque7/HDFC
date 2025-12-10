# backend/apps/kyc/utils.py
from datetime import date, datetime
from .models import KYCIndex, GovDocument, KYCAttempt
from dateutil.relativedelta import relativedelta

MAX_ATTEMPTS = 3

def register_attempt(customer, stage):
    last = KYCAttempt.objects.filter(customer=customer, stage=stage).order_by('-attempt_number').first()
    last_num = last.attempt_number if last else 0
    next_attempt = last_num + 1
    KYCAttempt.objects.create(customer=customer, stage=stage, attempt_number=next_attempt)
    allowed = next_attempt <= MAX_ATTEMPTS
    return allowed, next_attempt

def check_duplicate_in_index(id_type, id_value):
    return KYCIndex.objects.filter(id_type=id_type, id_value=id_value).exists()

def check_duplicate_in_govdb(id_type, id_value):
    return GovDocument.objects.filter(doc_type=id_type, doc_number__iexact=id_value).first()

def check_passport_validity(expiry_iso):
    if not expiry_iso:
        return False, 0
    try:
        exp = datetime.fromisoformat(expiry_iso).date()
    except Exception:
        try:
            exp = date.fromisoformat(expiry_iso.split('T')[0])
        except Exception:
            return False, 0
    today = date.today()
    months_left = (exp.year - today.year) * 12 + (exp.month - today.month)
    is_valid = exp >= (today + relativedelta(months=+6))
    return is_valid, months_left
