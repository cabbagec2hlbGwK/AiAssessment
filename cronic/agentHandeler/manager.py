import json
import os
import datetime
import uuid
import random
import base64
from cronic.agentHandeler.utils import endpointHandeler
from cronic.agentHandeler.utils.taskHandeler import AgentManager
from cronic.agentHandeler.utils.endpointHandeler import EndpointHandeler
from cronic.agentHandeler.tasks.tasks import taskRun
from cronic.agentHandeler.utils import taskHandeler
TIMEOUT = 0.6

def deployTask(endpoint:EndpointHandeler, agentManager:AgentManager, targer, userId):
    agentId = str(uuid.uuid4())
    rawCommands = endpoint.getCommand(targer)
    tasks = dict()
    agentManager.incUserCounter(userId)
    input("it was successs")
    for commands in rawCommands:
        for command in commands.get("commands",[]):
            taskId = agentManager.createTask(userId=userId, agentId=agentId,command=str(command))
            tasks[taskId]={"command":[command]}
            taskRun.delay(agentId=agentId, tasks=tasks, packages=[], userId=userId)
            tasks = dict()
        print(tasks)




def main():
    secret_name = os.getenv("secret_name")
    rds_endpoint = os.getenv("rds_endpoint")
    region_name = os.getenv("AWS_DEFAULT_REGION")
    hostEndpoint = os.getenv("APIHOST")
    agentManager = AgentManager(secret_name, rds_endpoint, region_name, db_name="aiAssesDB2")
    endpoint = EndpointHandeler(host=hostEndpoint)

    #res = agentManager.createUser(name="john",email="john@gmail.com",endpoint="google.com", detailedReport=True)
    

    deployTask(agentManager=agentManager, endpoint=endpoint, userId="d57a5441-0d7f-46a4-a02a-726d747f7bb2", targer="http://localhost:8000")


    


if __name__ =="__main__":
    main()
