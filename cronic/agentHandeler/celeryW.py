import os
from celery import Celery

brokerEndpoint = os.getenv("BROKER","redis://:dctestpass@3.142.123.195:6379/0")
app = Celery("worker_ai", broker=brokerEndpoint)

app.conf.task_queues = {
    'queue_task1': {
        'exchange': 'queue_task1',
        'routing_key': 'task1',
    },
    'queue_task2': {
        'exchange': 'queue_task2',
        'routing_key': 'task2',
    }
}

app.conf.task_routes = {
    'tasks.release.release': {'queue': 'queue_task1'},
    'tasks.tasks.taskRun': {'queue': 'queue_task2'}
}

app.autodiscover_tasks(['agentHandeler.tasks'])
