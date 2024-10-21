import os
from celery import Celery

brokerEndpoint = os.getenv("BROKER","redis://:dctestpass@3.142.123.195:6379/0")
app = Celery("worker_ai", broker=brokerEndpoint)

app.conf.task_queues = {
    'queue_task1': {
        'exchange': 'command_task',
        'routing_key': 'task1',
    },
    'queue_task2': {
        'exchange': 'post_execution',
        'routing_key': 'task2',
    }
}

app.conf.task_routes = {
    'tasks.release.release': {'queue': 'command_task'},
    'tasks.tasks.taskRun': {'queue': 'post_execution'}
}

app.autodiscover_tasks(['agentHandeler.tasks'])
