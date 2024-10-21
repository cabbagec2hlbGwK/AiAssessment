import os
from utils.taskHandeler import AgentManager
from utils.endpointHandeler import EndpointHandeler
from celery import Celery
app = Celery('release', broker='redis://:dctestpass@3.142.123.195:6379/0')

secret_name = os.getenv("secret_name")
rds_endpoint = os.getenv("rds_endpoint")
region_name = os.getenv("AWS_DEFAULT_REGION")
hostEndpoint = os.getenv("APIHOST")

@app.task(name='tasks.release')
def release(results, agentId, userId):
    agentManager = AgentManager(secret_name, rds_endpoint, region_name, db_name="aiAssesDB2")
    endpoint = EndpointHandeler(host=hostEndpoint)
    for taskId, value in results.items():
        print(taskId)
        if len(value.get("results",{}).get('failedCommands',[]))>0:
            res = agentManager.setTaskError(taskId, error=" ".join(value.get("results",{}).get('failedCommands',[])))
            print(f"the task: {taskId} was successfully updated with {res}")
        else:
            res = agentManager.setTaskSuccess(taskId," ".join(value.get("results",{}).get('failedCommands',[])))
            print(f"the task: {taskId} was error updated with {res}")


def main():
    pass

if __name__ == "__main__":
    main()
