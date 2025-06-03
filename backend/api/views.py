from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from celery.result import AsyncResult
from django.http import FileResponse, Http404
from django.conf import settings
import os

from .tasks import generate_pdf


class GeneratePDFView(APIView):
    def post(self, request):
        report_id = request.data.get("report_id")
        if not report_id:
            return Response({"error": "Missing report_id"}, status=status.HTTP_400_BAD_REQUEST)

        task = generate_pdf.delay(report_id)
        return Response({"task_id": task.id, "status": "started"})


class PDFStatusView(APIView):
    def get(self, request, task_id):
        result = AsyncResult(task_id)
        response = {
            "task_id": task_id,
            "status": result.status,
            "result": result.result if result.ready() else None
        }
        return Response(response)


def download_pdf_view(request, report_id):
    output_dir = getattr(settings, "PDF_OUTPUT_DIR", "/tmp")
    pdf_path = os.path.join(output_dir, f"report_{report_id}.pdf")

    if not os.path.exists(pdf_path):
        raise Http404("PDF not found")

    return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
