import os
from cronic.agentHandeler.utils.taskHandeler import AgentManager
from cronic.agentHandeler.utils.endpointHandeler import EndpointHandeler
from celery import shared_task

secret_name = os.getenv("secret_name")
rds_endpoint = os.getenv("rds_endpoint")
region_name = os.getenv("AWS_DEFAULT_REGION")
hostEndpoint = os.getenv("APIHOST")

@shared_task
def release(results, agentId, userId):
    agentManager = AgentManager(secret_name, rds_endpoint, region_name, db_name="aiAssesDB2")
    endpoint = EndpointHandeler(host=hostEndpoint)
    for taskId, value in results.items():
        print(taskId)
        if len(value.get("results",{}).get('failedCommands',[]))>0:
            print(value.get("results",{}).get('failedCommands',[]))
            res = agentManager.setTaskError(taskId, error=" ".join(value.get("results",{}).get('failedCommands',[])))
            print(f"the task: {taskId} was successfully updated with {res}")
        else:
            res = agentManager.setTaskSuccess(taskId," ".join(value.get("results",{}).get('failedCommands',[])))
            print(f"the task: {taskId} was error updated with {res}")


def main():
    pass

if __name__ == "__main__":
    main()
