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

    # Проверим: есть ли хотя бы одна позиция у инвойса
    if not invoice.items.exists():
        logger.info(f"[signals] ⏳ Invoice #{invoice.id} ещё без позиций.")
        return

    # Проверим, не существует ли уже PDF
    pdf_path = invoice.get_pdf_path()
    pdf_exists = False

    if getattr(settings, "USE_S3", False):
        pdf_exists = bool(invoice.pdf_url)  # Можно улучшить HEAD-запросом, если нужно
    else:
        pdf_exists = os.path.exists(pdf_path)

    if pdf_exists:
        logger.info(f"[signals] ✅ Invoice #{invoice.id}: PDF уже существует. Пропускаем генерацию.")
        return

    try:
        logger.info(f"[signals] 🧾 Invoice #{invoice.id}: добавлена позиция. Генерируем PDF...")

        # Отложенный запуск через Celery
        result = generate_pdf.delay(invoice.id)

        # Создаём или обновляем статус задачи
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
