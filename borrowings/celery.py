import os

from celery import Celery


os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "Library_Service_API.settings"
)

app = Celery("checking_overdue_borrowings")

app.config_from_object(
    "django.conf:settings", namespace="CELERY"
)

app.autodiscover_tasks()
