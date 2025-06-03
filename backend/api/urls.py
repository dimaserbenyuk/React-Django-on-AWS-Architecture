from django.urls import path
from .views import GeneratePDFView, PDFStatusView, download_pdf_view, health_check_view

urlpatterns = [
    path("generate-pdf/", GeneratePDFView.as_view(), name="generate_pdf"),
    path("pdf-status/<task_id>/", PDFStatusView.as_view(), name="pdf_status"),
    path("download-pdf/<int:report_id>/", download_pdf_view, name="download_pdf"),
    path("health/", health_check_view, name="health_check"), 
]
