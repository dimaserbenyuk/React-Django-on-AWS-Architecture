import os
import logging
from typing import Any, Dict
from celery import shared_task
from django.template.loader import render_to_string
from weasyprint import HTML
from django.conf import settings
from .models import Invoice

logger = logging.getLogger(__name__)


@shared_task(name="celery.ping")
def ping() -> str:
    return "pong"


@shared_task(bind=True)
def generate_pdf(self, report_id: int) -> Dict[str, Any]:
    try:
        invoice = (
            Invoice.objects.select_related("customer")
            .prefetch_related("items")
            .get(id=report_id)
        )

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
                "total": float(item_total),
            })
            total += item_total

        logo_path = invoice.logo.path if invoice.logo and invoice.logo.name else None

        context = {
            "invoice_id": invoice.id,
            "company": invoice.company_name,
            "address": invoice.address,
            "date": invoice.created_at.strftime("%H:%M:%S, %d.%m.%Y"),
            "items": items,
            "total": float(total),
            "customer": {
                "name": invoice.customer.name if invoice.customer else "",
                "email": invoice.customer.email if invoice.customer else "",
                "phone": invoice.customer.phone if invoice.customer else "",
                "address": invoice.customer.address if invoice.customer else "",
            },
            "logo_path": logo_path,
        }

        html = render_to_string("report_template.html", context)
        HTML(string=html, base_url=settings.MEDIA_ROOT).write_pdf(target=pdf_path)

        logger.info("✅ PDF сохранён: %s", pdf_path)
        invoice.update_pdf_metadata(task_id=self.request.id)

        return {
            "report_id": report_id,
            "pdf_path": str(pdf_path),
            "status": "completed",
        }

    except Invoice.DoesNotExist:
        msg = f"❌ Invoice ID {report_id} не найден"
        logger.error(msg)
        return {"report_id": report_id, "status": "failed", "error": msg}

    except Exception as e:
        logger.exception("❌ Ошибка при генерации PDF")
        return {"report_id": report_id, "status": "failed", "error": str(e)}
