import os
from django.conf import settings
from django.db import models
from django.utils.html import format_html


class Invoice(models.Model):
    company_name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

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
        return "❌ No PDF found"

    pdf_link.short_description = "PDF File"
    pdf_link.allow_tags = True


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
