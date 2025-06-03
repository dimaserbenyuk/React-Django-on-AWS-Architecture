from django.contrib import admin
from .models import Invoice, InvoiceItem
from django.utils.html import format_html
from django.urls import reverse
from .tasks import generate_pdf
import os

@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ["invoice", "name", "quantity", "unit_price"]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ["id", "company_name", "address", "created_at", "pdf_link"]
    actions = ["generate_pdf_action"]

    def pdf_link(self, obj):
        pdf_path = os.path.join("pdf_output", f"report_{obj.id}.pdf")
        full_path = os.path.join("backend", pdf_path)
        if os.path.exists(full_path):
            url = reverse("download_pdf", args=[obj.id])
            return format_html('<a href="{}" target="_blank">📄 View PDF</a>', url)
        return format_html('<span style="color:red">❌ No PDF found</span>')
    pdf_link.short_description = "PDF File"

    def generate_pdf_action(self, request, queryset):
        for invoice in queryset:
            generate_pdf.delay(invoice.id)
        self.message_user(request, f"{queryset.count()} PDF generation task(s) started.")
    generate_pdf_action.short_description = "📄 Generate PDF (async via Celery)"
