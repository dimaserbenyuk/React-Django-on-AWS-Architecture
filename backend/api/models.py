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

    class Meta:
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["customer"]),
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


class TaskStatus(models.Model):
    """Tracks Celery task status for a given Invoice."""
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="tasks")
    task_id = models.CharField(max_length=100)  # убрано unique=True
    heartbeat_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED)
    started_at = models.DateTimeField(blank=True, null=True)
    finished_at = models.DateTimeField(blank=True, null=True)
    duration_seconds = models.FloatField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["invoice"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Task {self.task_id} ({self.invoice}) - {self.status}"

    def mark_started(self):
        self.status = self.Status.RUNNING
        self.started_at = now()
        self.save(update_fields=["status", "started_at"])

    def mark_completed(self):
        self.status = self.Status.COMPLETED
        self.finished_at = now()
        self.duration_seconds = self._calculate_duration()
        self.save(update_fields=["status", "finished_at", "duration_seconds"])

    def mark_failed(self, error: str):
        self.status = self.Status.FAILED
        self.finished_at = now()
        self.duration_seconds = self._calculate_duration()
        self.error_message = error
        self.save(update_fields=["status", "finished_at", "duration_seconds", "error_message"])

    def mark_stale(self):
        self.status = self.Status.FAILED
        self.finished_at = now()
        self.duration_seconds = self._calculate_duration()
        self.error_message = "Task marked as stale (no heartbeat)"
        self.save(update_fields=["status", "finished_at", "duration_seconds", "error_message"])

    def _calculate_duration(self) -> Optional[float]:
        if self.started_at and self.finished_at:
            return (self.finished_at - self.started_at).total_seconds()
        return None

    @classmethod
    def start_or_update(cls, invoice: Invoice, task_id: str) -> "TaskStatus":
        obj, _ = cls.objects.update_or_create(
            task_id=task_id,
            defaults={
                "invoice": invoice,
                "status": cls.Status.QUEUED,
                "started_at": now(),
                "heartbeat_at": now(),
            }
        )
        return obj
