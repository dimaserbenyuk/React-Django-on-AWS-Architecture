import os
from django.conf import settings
from django.db import models
from django.utils.html import format_html
from django.utils.timezone import now


class Invoice(models.Model):
    company_name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    pdf_task_id = models.CharField(max_length=100, blank=True, null=True)
    pdf_updated_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Invoice #{self.id} - {self.company_name}"

    def get_pdf_filename(self):
        return f"report_{self.id}.pdf"

    def get_pdf_path(self):
        return os.path.join(settings.PDF_OUTPUT_DIR, self.get_pdf_filename())

    def get_pdf_url(self):
        return f"/api/download-pdf/{self.id}/"

    def pdf_link(self):
        pdf_file = self.get_pdf_path()
        if os.path.exists(pdf_file):
            return format_html('<a href="{}" target="_blank">📄 View PDF</a>', self.get_pdf_url())
        return format_html('<span style="color:red;">❌ No PDF found</span>')

    pdf_link.short_description = "PDF File"
    pdf_link.allow_tags = True

    def update_pdf_metadata(self, task_id: str):
        """Update fields after PDF generation task."""
        self.pdf_task_id = task_id
        self.pdf_updated_at = now()
        self.save(update_fields=["pdf_task_id", "pdf_updated_at"])


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='items'
    )
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def total(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.name} x {self.quantity}"
