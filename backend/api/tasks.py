import os
import logging
from typing import Any, Dict
from datetime import timedelta

from celery import shared_task
from django.template.loader import render_to_string
from weasyprint import HTML
from django.conf import settings
from django.utils.timezone import now

from .models import Invoice, TaskStatus

logger = logging.getLogger(__name__)


@shared_task(name="celery.ping")
def ping() -> str:
    return "pong"


@shared_task(bind=True, name="generate_pdf")
def generate_pdf(self, report_id: int) -> Dict[str, Any]:
    task_id = self.request.id
    task_status = None

    try:
        invoice = (
            Invoice.objects.select_related("customer")
            .prefetch_related("items")
            .get(id=report_id)
        )

        # Создаём задачу
        task_status = TaskStatus.objects.create(
            invoice=invoice,
            task_id=task_id,
            status=TaskStatus.Status.RUNNING,
            started_at=now(),
            heartbeat_at=now(),
        )

        output_dir = getattr(settings, "PDF_OUTPUT_DIR", os.path.join(settings.BASE_DIR, "pdf_output"))
        os.makedirs(output_dir, exist_ok=True)

        pdf_filename = f"report_{report_id}.pdf"
        pdf_path = os.path.join(output_dir, pdf_filename)

        items = []
        total = 0
        all_items = list(invoice.items.all())

        for idx, item in enumerate(all_items, 1):
            item_total = item.total()
            items.append({
                "name": item.name,
                "qty": item.quantity,
                "price": float(item.unit_price),
                "total": float(item_total),
            })
            total += item_total

            if idx % 3 == 0 or idx == len(all_items):
                task_status.heartbeat_at = now()
                task_status.save(update_fields=["heartbeat_at"])

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
        task_status.mark_completed()

        return {
            "report_id": report_id,
            "pdf_path": str(pdf_path),
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
                invoice=invoice if 'invoice' in locals() else None,
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
