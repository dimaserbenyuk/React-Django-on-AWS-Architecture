from celery import shared_task
from django.template.loader import render_to_string
from weasyprint import HTML
import logging
import os
from django.conf import settings
from datetime import datetime

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def generate_pdf(self, report_id):
    try:
        output_dir = getattr(settings, "PDF_OUTPUT_DIR", "/tmp")
        os.makedirs(output_dir, exist_ok=True)
        pdf_path = os.path.join(output_dir, f"report_{report_id}.pdf")

        # Данные для шаблона
        context = {
            "company": "OmniSoft",
            "address": "123 Bristol Road, London",
            "date": datetime.now().strftime("%H:%M:%S, %d.%m.%Y"),
            "items": [
                {"name": "Marie", "qty": 1, "price": 1, "total": 1},
                {"name": "Gerty", "qty": 2, "price": 12, "total": 24},
                {"name": "Rosalyn", "qty": 3, "price": 14, "total": 42},
                {"name": "Barbara", "qty": 4, "price": 12, "total": 48},
                {"name": "Rita", "qty": 5, "price": 19, "total": 95},
                {"name": "Gertrude", "qty": 6, "price": 4, "total": 24},
                {"name": "Christiane", "qty": 7, "price": 8, "total": 56},
                {"name": "Linda", "qty": 8, "price": 7, "total": 56},
            ],
            "total": 346
        }

        html = render_to_string("report_template.html", context)
        HTML(string=html).write_pdf(pdf_path)

        logger.warning(f"PDF saved at: {pdf_path}")

        return {
            "report_id": report_id,
            "pdf_path": pdf_path,
            "status": "completed"
        }

    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        return {
            "report_id": report_id,
            "status": "failed",
            "error": str(e)
        }
