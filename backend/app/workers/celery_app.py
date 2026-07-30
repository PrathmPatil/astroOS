from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "astrosutra",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(name="reports.generate_pdf")
def generate_pdf_task(birth_payload: dict, report_id: str) -> dict:
    """Placeholder PDF generation task — expand with ReportLab templates."""
    return {
        "report_id": report_id,
        "status": "queued_logic_ready",
        "message": "PDF pipeline scaffold ready for ReportLab templates.",
        "birth": birth_payload.get("name"),
    }
