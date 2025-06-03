from celery import shared_task
import time

@shared_task
def generate_pdf(report_id):
    # Твоя логика генерации PDF
    print(f"Generating PDF for report_id: {report_id}")