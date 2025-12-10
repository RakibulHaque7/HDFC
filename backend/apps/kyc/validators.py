# backend/apps/kyc/validators.py

import re
from rest_framework import serializers

# Aadhaar: 12 digits, can be written as "1234 5678 9012" or "123456789012"
AADHAAR_REGEX = re.compile(r'^\d{4}\s?\d{4}\s?\d{4}$')

# PAN: 5 letters, 4 digits, 1 letter: ABCDE1234F
PAN_REGEX = re.compile(r'^[A-Z]{5}[0-9]{4}[A-Z]$')

# Passport: 1 letter, 7 digits => A1234567
PASSPORT_REGEX = re.compile(r'^[A-PR-WYa-pr-wy][1-9][0-9]{6}$')

# Voter ID: 3 letters + 7 digits => ABC1234567
VOTER_REGEX = re.compile(r'^[A-Z]{3}[0-9]{7}$')


def validate_document_number(doc_type: str, id_number: str) -> str:
    """
    Check that id_number matches the expected format for doc_type.
    Raises ValidationError if it doesn't match.
    Returns the cleaned (uppercased, space-trimmed) id_number.
    """
    doc_type = (doc_type or "").upper().strip()
    id_number = (id_number or "").upper().strip()

    if doc_type == "AADHAAR":
        # remove spaces inside Aadhaar for consistency
        raw = id_number.replace(" ", "")
        if not AADHAAR_REGEX.match(id_number) and not AADHAAR_REGEX.match(raw):
            raise serializers.ValidationError("Invalid Aadhaar number format")
        return raw

    elif doc_type == "PAN":
        if not PAN_REGEX.match(id_number):
            raise serializers.ValidationError("Invalid PAN format (ABCDE1234F)")
        return id_number

    elif doc_type == "PASSPORT":
        if not PASSPORT_REGEX.match(id_number):
            raise serializers.ValidationError("Invalid Passport format")
        return id_number

    elif doc_type == "VOTER":
        if not VOTER_REGEX.match(id_number):
            raise serializers.ValidationError("Invalid Voter ID format")
        return id_number

    else:
        raise serializers.ValidationError("Unsupported document type")
