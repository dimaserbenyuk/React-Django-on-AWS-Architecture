from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.exceptions import ValidationError
from celery.result import AsyncResult

from django.http import FileResponse, Http404, JsonResponse
from django.conf import settings
import redis
import os

from backend.celery import app as celery_app
from .models import Invoice
from .tasks import generate_pdf
from .serializers import InvoiceSerializer


class GeneratePDFView(APIView):
    def post(self, request):
        report_id = request.data.get("report_id")
        if not report_id:
            return Response({"error": "Missing report_id"}, status=status.HTTP_400_BAD_REQUEST)

        task = generate_pdf.delay(report_id)
        return Response({"task_id": task.id, "status": "started"}, status=status.HTTP_202_ACCEPTED)


class PDFStatusView(APIView):
    def get(self, request, task_id):
        result = AsyncResult(task_id)
        response = {
            "task_id": task_id,
            "status": result.status,
            "result": result.result if result.ready() else None
        }
        return Response(response, status=status.HTTP_200_OK)


def download_pdf_view(request, report_id):
    output_dir = getattr(settings, "PDF_OUTPUT_DIR", "/tmp")
    pdf_path = os.path.join(output_dir, f"report_{report_id}.pdf")

    if not os.path.exists(pdf_path):
        raise Http404("PDF not found")

    return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')


def health_check_view(request):
    status_flags = {
        "redis": False,
        "celery": False,
    }

    try:
        redis_url = settings.CELERY_BROKER_URL
        r = redis.Redis.from_url(redis_url)
        r.ping()
        status_flags["redis"] = True
    except Exception as e:
        status_flags["redis_error"] = str(e)

    try:
        result = celery_app.send_task("celery.ping")
        result.get(timeout=5)
        status_flags["celery"] = True
    except Exception as e:
        status_flags["celery_error"] = str(e)

    overall = status_flags["redis"] and status_flags["celery"]
    return JsonResponse({"ok": overall, **status_flags})


class InvoiceListCreateView(generics.ListCreateAPIView):
    queryset = Invoice.objects.all().order_by("-id")
    serializer_class = InvoiceSerializer

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class InvoiceDetailView(generics.RetrieveAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    lookup_field = "pk"