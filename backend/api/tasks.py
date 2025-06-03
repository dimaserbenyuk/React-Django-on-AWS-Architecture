import os
import logging
from typing import Any, Dict
from celery import shared_task
from django.template.loader import render_to_string
from weasyprint import HTML
from django.conf import settings
from datetime import datetime
from .models import Invoice

logger = logging.getLogger(__name__)

@shared_task(name="celery.ping")
def ping() -> str:
    """Healthcheck task for Celery."""
    return "pong"

@shared_task(bind=True)
def generate_pdf(self, report_id: int) -> Dict[str, Any]:
    """
    Generate a PDF for the given Invoice ID.

    Args:
        report_id (int): The ID of the invoice to generate PDF for.

    Returns:
        dict: Result status, path to PDF, or error message.
    """
    try:
        invoice = Invoice.objects.prefetch_related("items").get(id=report_id)

        output_dir = getattr(settings, "PDF_OUTPUT_DIR", os.path.join(settings.BASE_DIR, "pdf_output"))
        os.makedirs(output_dir, exist_ok=True)

        pdf_filename = f"report_{report_id}.pdf"
        pdf_path = os.path.join(output_dir, pdf_filename)

        items = []
        total = 0
        for item in invoice.items.all():
            item_total = item.total()
            items.append({
                "name": item.name,
                "qty": item.quantity,
                "price": float(item.unit_price),
                "total": float(item_total)
            })
            total += item_total

        context = {
            "company": invoice.company_name,
            "address": invoice.address,
            "date": invoice.created_at.strftime("%H:%M:%S, %d.%m.%Y"),
            "items": items,
            "total": float(total)
        }

        html = render_to_string("report_template.html", context)
        HTML(string=html).write_pdf(pdf_path)

        logger.info("✅ PDF успешно сохранён: %s", pdf_path)

        return {
            "report_id": report_id,
            "pdf_path": str(pdf_path),
            "status": "completed"
        }

    except Invoice.DoesNotExist:
        error_msg = f"❌ Invoice ID {report_id} не найден"
        logger.error(error_msg)
        return {"report_id": report_id, "status": "failed", "error": "Invoice not found"}

    except Exception as e:
        logger.exception("❌ Ошибка при генерации PDF")
        return {"report_id": report_id, "status": "failed", "error": str(e)}
