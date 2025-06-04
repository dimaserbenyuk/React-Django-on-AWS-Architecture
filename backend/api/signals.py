import logging
import os
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now

from .models import Invoice, InvoiceItem, TaskStatus
from .tasks import generate_pdf

logger = logging.getLogger(__name__)


@receiver(post_save, sender=InvoiceItem)
def generate_pdf_when_item_added(sender, instance, created, **kwargs):
    invoice = instance.invoice

    # Проверим: есть ли хотя бы один item и PDF ещё не сгенерирован
    if invoice.items.exists():
        pdf_path = invoice.get_pdf_path()

        if not os.path.exists(pdf_path):
            try:
                logger.info(f"[signals] 🧾 Invoice #{invoice.id}: добавлена позиция. Генерируем PDF...")
                
                # Запускаем задачу на генерацию
                result = generate_pdf.delay(invoice.id)

                # Обновляем статус вручную
                TaskStatus.objects.update_or_create(
                    invoice=invoice,
                    defaults={
                        "task_id": result.id,
                        "status": TaskStatus.Status.QUEUED,
                        "started_at": now(),
                        "heartbeat_at": now()
                    }
                )
            except Exception as e:
                logger.exception(f"[signals] ❌ Ошибка генерации PDF")
