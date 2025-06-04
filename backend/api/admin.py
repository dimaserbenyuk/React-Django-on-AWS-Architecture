import os
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Invoice, InvoiceItem, Customer, TaskStatus
from .tasks import generate_pdf


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    min_num = 1
    verbose_name = "Invoice Item"
    verbose_name_plural = "Invoice Items"


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "customer_name",
        "company_name",
        "address",
        "created_at",
        "latest_task_status_badge",
        "latest_task_duration",
        "pdf_link",
    ]
    readonly_fields = [
        "pdf_link",
    ]
    inlines = [InvoiceItemInline]
    actions = ["generate_pdf_action"]
    list_filter = ["created_at"]
    search_fields = ["company_name", "customer__name"]

    def customer_name(self, obj):
        return obj.customer.name if obj.customer else "—"
    customer_name.short_description = "Customer"

    def pdf_link(self, obj):
        pdf_file_path = obj.get_pdf_path()
        if os.path.exists(pdf_file_path):
            url = reverse("download_pdf", args=[obj.id])
            return format_html('<a href="{}" target="_blank">📄 View PDF</a>', url)
        return format_html('<span style="color:red;">❌ No PDF found</span>')
    pdf_link.short_description = "PDF File"

    def latest_task_status_badge(self, obj):
        task = obj.tasks.first()
        if not task:
            return format_html('<span style="color:gray;">—</span>')
        color = {
            "queued": "gray",
            "running": "orange",
            "completed": "green",
            "failed": "red"
        }.get(task.status, "black")
        return format_html(
            '<span style="color:{}; font-weight:bold;">{}</span>',
            color,
            task.status.capitalize()
        )
    latest_task_status_badge.short_description = "PDF Status"

    def latest_task_duration(self, obj):
        task = obj.tasks.first()
        if task and task.duration_seconds:
            return f"{task.duration_seconds:.2f} s"
        return "—"
    latest_task_duration.short_description = "Generation Time"

    def generate_pdf_action(self, request, queryset):
        started = []
        for invoice in queryset:
            if invoice.items.exists():
                generate_pdf.delay(invoice.id)
                started.append(str(invoice.id))
        self.message_user(
            request,
            f"{len(started)} PDF task(s) started. Invoices: {', '.join(started)}"
        )
    generate_pdf_action.short_description = "📄 Generate PDF via Celery"


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "phone"]
    search_fields = ["name", "email"]

@admin.register(TaskStatus)
class TaskStatusAdmin(admin.ModelAdmin):
    list_display = [
        "id", "invoice_link", "status", "task_id",
        "started_at", "finished_at", "duration_seconds", "short_error"
    ]
    list_filter = ["status", "created_at"]
    search_fields = ["task_id", "invoice__company_name", "invoice__customer__name"]
    readonly_fields = ["error_message"]

    def invoice_link(self, obj):
        url = reverse("admin:api_invoice_change", args=[obj.invoice.id])
        return format_html('<a href="{}">Invoice #{}</a>', url, obj.invoice.id)
    invoice_link.short_description = "Invoice"

    def short_error(self, obj):
        return (obj.error_message[:75] + "...") if obj.error_message else "—"
    short_error.short_description = "Error"
