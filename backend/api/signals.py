import logging
import os
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Invoice, InvoiceItem
from .tasks import generate_pdf

logger = logging.getLogger(__name__)


@receiver(post_save, sender=InvoiceItem)
def generate_pdf_when_item_added(sender, instance, created, **kwargs):
    invoice = instance.invoice

    # Проверим, есть ли хотя бы одна позиция и нет PDF файла
    if invoice.items.exists():
        pdf_path = invoice.get_pdf_path()
        if not os.path.exists(pdf_path):
            try:
                logger.info(f"[signals] 🧾 Invoice #{invoice.id}: добавлена позиция. Генерируем PDF...")
                result = generate_pdf.delay(invoice.id)
                invoice.update_pdf_metadata(task_id=result.id)
            except Exception as e:
                logger.error(f"[signals] ❌ Ошибка генерации PDF: {e}")
