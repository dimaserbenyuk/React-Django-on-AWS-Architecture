import logging
import os

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from django.conf import settings

from .models import Invoice, InvoiceItem, TaskStatus
from .tasks import generate_pdf

logger = logging.getLogger(__name__)


@receiver(post_save, sender=InvoiceItem)
def generate_pdf_when_item_added(sender, instance, created, **kwargs):
    invoice = instance.invoice
    if not invoice:
        logger.warning("[signals] 🧾 InvoiceItem сохранён, но не связан с Invoice.")
        return

    if not invoice.items.exists():
        logger.info(f"[signals] ⏳ Invoice #{invoice.id} ещё без позиций.")
        return

    # Проверим: нет ли уже PDF-файла
    pdf_path = invoice.get_pdf_path()
    pdf_exists = False

    if getattr(settings, "USE_S3", False):
        pdf_exists = bool(invoice.pdf_url)
    else:
        pdf_exists = os.path.exists(pdf_path)

    if pdf_exists:
        logger.info(f"[signals] ✅ Invoice #{invoice.id}: PDF уже существует.")
        return

    # Проверим, не запущена ли задача на генерацию
    latest_task = invoice.tasks.first()
    if latest_task and latest_task.status in [
        TaskStatus.Status.QUEUED,
        TaskStatus.Status.RUNNING,
        TaskStatus.Status.COMPLETED
    ]:
        logger.info(f"[signals] ⏩ Invoice #{invoice.id}: уже есть задача со статусом {latest_task.status}. Пропускаем.")
        return

    try:
        logger.info(f"[signals] 🧾 Invoice #{invoice.id}: добавлена позиция. Запускаем генерацию PDF...")

        result = generate_pdf.delay(invoice.id)

        TaskStatus.objects.update_or_create(
            invoice=invoice,
            defaults={
                "task_id": result.id if result else None,
                "status": TaskStatus.Status.QUEUED,
                "started_at": now(),
                "heartbeat_at": now(),
            }
        )
    except Exception as e:
        logger.exception(f"[signals] ❌ Ошибка при запуске генерации PDF для Invoice #{invoice.id}")
