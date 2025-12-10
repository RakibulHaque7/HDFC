# backend/apps/kyc/management/commands/seed_gov_data.py
from django.core.management.base import BaseCommand
from apps.kyc.models import GovDocument
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = "Seed GovDocument table with sample Aadhaar, PAN and Passport records (~20 each)."

    def handle(self, *args, **options):
        GovDocument.objects.all().delete()

        for i in range(1,21):
            num = f"{random.randint(10**11, 10**12-1)}"
            GovDocument.objects.create(doc_type='AADHAAR', doc_number=f"AAD{num[-9:]}", meta={"name":f"Person A{i}"})

        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for i in range(1,21):
            pan = ''.join(random.choice(letters) for _ in range(5)) + str(random.randint(1000,9999)) + random.choice(letters)
            GovDocument.objects.create(doc_type='PAN', doc_number=f"{pan}", meta={"name":f"Person P{i}"})

        today = date.today()
        for i in range(1,21):
            passport_no = f"P{random.randint(10**6, 10**7-1)}"
            days = random.randint(-365, 365*5)
            expiry = today + timedelta(days=days)
            GovDocument.objects.create(doc_type='PASSPORT', doc_number=passport_no, meta={"name":f"Person X{i}", "expiry_date": expiry.isoformat()})

        self.stdout.write(self.style.SUCCESS("Seeded GovDocument with 60 records (20 per type)."))
