from django.urls import path
from .views import (
    GeneratePDFView,
    PDFStatusView,
    download_pdf_view,
    health_check_view,
    db_status_view,
    InvoiceListCreateView,
    InvoiceDetailView
)

urlpatterns = [
    path("generate-pdf/", GeneratePDFView.as_view(), name="generate_pdf"),
    path("pdf-status/<task_id>/", PDFStatusView.as_view(), name="pdf_status"),
    path("download-pdf/<int:report_id>/", download_pdf_view, name="download_pdf"),
    path("health/", health_check_view, name="health_check"),
    path("db-status/", db_status_view, name="db_status"),
    path("invoices/", InvoiceListCreateView.as_view(), name="invoice_list_create"),
    path("invoices/<int:pk>/", InvoiceDetailView.as_view(), name="invoice_detail"),
]
