from django.contrib import admin
from .models import (
    Customer,
    KYCSession,
    KYCDocument,
)


# -------------------------------
# Customer Admin
# -------------------------------
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "phone", "email", "created_at")
    search_fields = ("full_name", "phone", "email")
    ordering = ("-created_at",)


# -------------------------------
# KYC Session Admin
# -------------------------------
@admin.register(KYCSession)
class KYCSessionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "current_stage",
        "progress_percent",
        "completed",
        "created_at",
    )
    list_filter = ("current_stage", "completed", "created_at")
    search_fields = ("id", "customer__phone", "customer__full_name")
    ordering = ("-created_at",)

    readonly_fields = ("id", "created_at")


# -------------------------------
# KYC Document Admin
# -------------------------------
@admin.register(KYCDocument)
class KYCDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "session",
        "doc_type",
        "uploaded_at",
        "status",
    )
    list_filter = ("doc_type", "status", "uploaded_at")
    search_fields = ("session__id", "doc_type")
    ordering = ("-uploaded_at",)

    readonly_fields = ("uploaded_at",)
