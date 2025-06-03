import os
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Invoice, InvoiceItem, Customer
from .tasks import generate_pdf
from django.conf import settings


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ["invoice", "name", "quantity", "unit_price"]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "customer_name",
        "company_name",
        "address",
        "created_at",
        "pdf_updated_at",
        "pdf_link"
    ]
    readonly_fields = ["pdf_link", "pdf_task_id", "pdf_updated_at"]
    actions = ["generate_pdf_action"]

    def customer_name(self, obj):
        return obj.customer.name if obj.customer else "—"
    customer_name.short_description = "Customer"

    def pdf_link(self, obj):
        pdf_file_path = obj.get_pdf_path()
        if os.path.exists(pdf_file_path):
            url = reverse("download_pdf", args=[obj.id])
            return format_html('<a href="{}" target="_blank">📄 View PDF</a>', url)
        return format_html('<span style="color:red;">❌ No PDF found</span>')
    pdf_link.short_description = "PDF File"

    def generate_pdf_action(self, request, queryset):
        started = 0
        for invoice in queryset:
            if invoice.items.exists():
                generate_pdf.delay(invoice.id)
                started += 1
        self.message_user(request, f"{started} PDF task(s) started (skipped empty invoices).")
    generate_pdf_action.short_description = "📄 Generate PDF (async via Celery)"


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "phone"]
