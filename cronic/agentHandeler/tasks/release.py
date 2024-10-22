import os

from requests import get
from cronic.agentHandeler.utils.taskHandeler import AgentManager
from cronic.agentHandeler.utils.endpointHandeler import EndpointHandeler
from cronic.agentHandeler.celeryW import app

secret_name = os.getenv("secret_name")
rds_endpoint = os.getenv("rds_endpoint")
region_name = os.getenv("AWS_DEFAULT_REGION")
hostEndpoint = os.getenv("APIHOST")

@app.task
def release(results, agentId, userId):
    agentManager = AgentManager(secret_name, rds_endpoint, region_name, db_name="aiAssesDB2")
    endpoint = EndpointHandeler(host=hostEndpoint)
    for taskId, value in results.items():
        print("-----------------------------------------------------------------------------")
        print(value)
        print("-----------------------------------------------------------------------------")
        print(len(value.get("results",{}).get('failedCommands',[])))
        if len(value.get("results",{}).get('failedCommands',[]))!=0:
            res = agentManager.setTaskError(taskId, error=str(value.get("results",{}).get('failedCommands',[])))
            print(f"the task: {taskId} was successfully updated with {res}")
        else:
            res = agentManager.setTaskSuccess(taskId,str(value.get("results",{}).get('failedCommands',[])))
            print(f"the task: {taskId} was error updated with {res}")


def main():
    pass

if __name__ == "__main__":
    main()
