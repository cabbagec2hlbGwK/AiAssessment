import os
from celery import Celery
from kombu import Exchange, Queue

# Set up the broker endpoint
brokerEndpoint = os.getenv("BROKER", "redis://:dctestpass@3.142.123.195:6379/0")
app = Celery("worker_ai", broker=brokerEndpoint)

# Define exchanges and queues explicitly
app.conf.task_queues = [
    Queue('queue_task1', Exchange('command_task', type='direct'), routing_key='task1'),
    Queue('queue_task2', Exchange('post_execution', type='direct'), routing_key='task2')
]

# Task routing configuration
app.conf.task_routes = {
    'cronic.agentHandeler.tasks.release.release': {'queue': 'queue_task1'},
    'cronic.agentHandeler.tasks.tasks.taskRun': {'queue': 'queue_task2'}
}

# Automatically discover tasks from the specified module
app.autodiscover_tasks(['cronic.agentHandeler.tasks'])

