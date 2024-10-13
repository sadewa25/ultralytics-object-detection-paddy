from celery import Celery

celery_app = Celery(
    "tasks",
    broker="redis://localhost:6380/0",  # Use the correct Redis port
    backend="redis://localhost:6380/0"
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True  # Add this line
)