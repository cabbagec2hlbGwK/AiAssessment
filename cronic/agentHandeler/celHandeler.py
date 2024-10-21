import os
from celery import Celery

brokerEndpoint = os.getenv("BROKER","redis://:dctestpass@3.142.123.195:6379/0")
app = Celery(__name__, broker=brokerEndpoint)

app.conf.update(
    result_backend='redis://localhost:6379/0',
    task_serializer='json',
    accept_content=['json'],
)
app.autodiscover_tasks(['release', 'tasks'])
