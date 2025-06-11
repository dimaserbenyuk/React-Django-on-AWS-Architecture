import os
import io
import logging
from typing import Any, Dict
from datetime import timedelta

from celery import shared_task
from django.template.loader import render_to_string
from weasyprint import HTML
from django.conf import settings
from django.utils.timezone import now
from django.core.files.base import ContentFile

from .models import Invoice, TaskStatus
from backend.storage_backends import PDFStorage

logger = logging.getLogger(__name__)


@shared_task(name="celery.ping")
def ping() -> str:
    return "pong"


@shared_task(bind=True, name="generate_pdf")
def generate_pdf(self, report_id: int) -> Dict[str, Any]:
    task_id = self.request.id
    invoice = None
    task_status = None

    try:
        invoice = (
            Invoice.objects.select_related("customer")
            .prefetch_related("items")
            .get(id=report_id)
        )

        task_status = TaskStatus.start_or_update(invoice=invoice, task_id=task_id)
        task_status.mark_started()

        filename = invoice.get_pdf_filename()
        items = []
        total = 0

        for idx, item in enumerate(invoice.items.all(), 1):
            item_total = item.total()
            items.append({
                "name": item.name or "",
                "qty": item.quantity,
                "price": float(item.unit_price),
                "total": float(item_total),
            })
            total += item_total

            if idx % 3 == 0 or idx == len(invoice.items.all()):
                task_status.heartbeat_at = now()
                task_status.save(update_fields=["heartbeat_at"])

        logo_path = invoice.logo.url if invoice.logo and invoice.logo.name else ""

        context = {
            "invoice_id": invoice.id,
            "company": invoice.company_name or "",
            "address": invoice.address or "",
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

        logger.info("📦 Rendering context:\n%s", context)

        # Генерация PDF
        pdf_buffer = io.BytesIO()
        html = render_to_string("report_template.html", context)

        if not html:
            raise ValueError("❌ render_to_string вернул пустую строку")

        # DEBUG: сохранить HTML как файл (при необходимости)
        if settings.DEBUG:
            with open(f"/tmp/invoice_{invoice.id}.html", "w") as f:
                f.write(html)

        HTML(string=html).write_pdf(target=pdf_buffer)
        pdf_buffer.seek(0)

        pdf_url = None

        if getattr(settings, "USE_S3", False):
            storage = PDFStorage()
            storage.save(filename, ContentFile(pdf_buffer.read()))
            pdf_url = f"https://{storage.bucket_name}.s3.amazonaws.com/{storage.location}/{filename}"
            invoice.pdf_url = pdf_url
            invoice.save(update_fields=["pdf_url"])
            pdf_path = f"s3://{storage.bucket_name}/{storage.location}/{filename}"
            logger.info("✅ PDF сохранён в S3: %s", pdf_url)
        else:
            output_dir = getattr(settings, "PDF_OUTPUT_DIR", os.path.join(settings.BASE_DIR, "pdf_output"))
            os.makedirs(output_dir, exist_ok=True)
            pdf_path = os.path.join(output_dir, filename)
            with open(pdf_path, "wb") as f:
                f.write(pdf_buffer.read())
            logger.info("✅ PDF сохранён локально: %s", pdf_path)

        task_status.mark_completed()

        return {
            "report_id": report_id,
            "pdf_path": pdf_url or str(pdf_path),
            "status": "completed",
        }

    except Invoice.DoesNotExist:
        msg = f"❌ Invoice ID {report_id} не найден"
        logger.error(msg)
        TaskStatus.objects.create(
            invoice=None,
            task_id=task_id,
            status=TaskStatus.Status.FAILED,
            error_message=msg,
            finished_at=now()
        )
        return {"report_id": report_id, "status": "failed", "error": msg}

    except Exception as e:
        logger.exception("❌ Ошибка при генерации PDF")
        if task_status:
            task_status.mark_failed(str(e))
        else:
            TaskStatus.objects.create(
                invoice=invoice if invoice else None,
                task_id=task_id,
                status=TaskStatus.Status.FAILED,
                error_message=str(e),
                finished_at=now()
            )
        return {"report_id": report_id, "status": "failed", "error": str(e)}


@shared_task(name="check_stuck_tasks")
def check_stuck_tasks():
    timeout_minutes = 5
    threshold = now() - timedelta(minutes=timeout_minutes)

    stuck_tasks = TaskStatus.objects.filter(
        status=TaskStatus.Status.RUNNING,
        heartbeat_at__lt=threshold
    )

    count = 0
    for task in stuck_tasks:
        task.mark_stale()
        logger.warning(f"📛 Marked as stale: {task.task_id}")
        count += 1

    logger.info(f"✅ check_stuck_tasks finished. {count} stale.")
    return {"stale_tasks": count}
