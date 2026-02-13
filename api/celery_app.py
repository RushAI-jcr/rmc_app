"""Celery application for background pipeline tasks."""

from celery import Celery

from api.settings import settings

celery = Celery(
    "rmc_triage",
    broker=settings.broker_url,
    backend=settings.result_backend,
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

celery.autodiscover_tasks(["api.tasks"])
