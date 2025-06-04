import os
from typing import Optional
from django.conf import settings
from django.db import models
from django.utils.html import format_html
from django.utils.timezone import now
from django.core.validators import FileExtensionValidator


class Customer(models.Model):
    """Represents a customer that can be attached to multiple invoices."""
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name


class Invoice(models.Model):
    """Represents an invoice containing customer, items, and optional logo."""
    class PDFStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        GENERATING = "generating", "Generating"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        related_name='invoices'
    )
    company_name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    logo = models.ImageField(
        upload_to='logos/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "svg"])]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    pdf_task_id = models.CharField(max_length=100, blank=True, null=True)
    pdf_status = models.CharField(max_length=20, choices=PDFStatus.choices, default=PDFStatus.PENDING)
    pdf_updated_at = models.DateTimeField(blank=True, null=True)
    pdf_filename = models.CharField(max_length=255, blank=True, null=True)
    pdf_size = models.IntegerField(blank=True, null=True)
    pdf_generated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["customer"]),
            models.Index(fields=["pdf_generated_at"]),
            models.Index(fields=["pdf_status"]),
        ]

    def __str__(self) -> str:
        return f"Invoice #{self.id} - {self.customer or self.company_name}"

    def get_pdf_filename(self) -> str:
        return f"report_{self.id}.pdf"

    def get_pdf_path(self) -> str:
        return os.path.join(settings.PDF_OUTPUT_DIR, self.get_pdf_filename())

    def get_pdf_url(self) -> str:
        return f"/api/download-pdf/{self.id}/"

    def pdf_link(self) -> str:
        pdf_file = self.get_pdf_path()
        if os.path.exists(pdf_file):
            return format_html(
                '<a href="{}" target="_blank">📄 View PDF</a>',
                self.get_pdf_url()
            )
        return format_html('<span style="color:red;">❌ No PDF found</span>')

    pdf_link.short_description = "PDF File"
    pdf_link.allow_tags = True

    def update_pdf_metadata(self, task_id: str, status: str = PDFStatus.COMPLETED) -> None:
        """Update metadata after Celery task completes."""
        path = self.get_pdf_path()
        self.pdf_task_id = task_id
        self.pdf_generated_at = now()
        self.pdf_filename = os.path.basename(path)
        self.pdf_size = os.path.getsize(path) if os.path.exists(path) else None
        self.pdf_status = status
        self.save(update_fields=[
            "pdf_task_id",
            "pdf_generated_at",
            "pdf_filename",
            "pdf_size",
            "pdf_status"
        ])


class InvoiceItem(models.Model):
    """Represents a single line item in an invoice."""
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='items'
    )
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def total(self) -> float:
        return self.quantity * float(self.unit_price)

    def __str__(self) -> str:
        return f"{self.name} x {self.quantity} ({self.invoice})"
