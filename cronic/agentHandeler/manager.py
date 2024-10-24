import json
import os
import datetime
import uuid
import random
import time
import base64
from cronic.agentHandeler.utils import endpointHandeler
from cronic.agentHandeler.utils.taskHandeler import AgentManager
from cronic.agentHandeler.utils.endpointHandeler import EndpointHandeler
from cronic.agentHandeler.tasks.tasks import taskRun
from cronic.agentHandeler.utils import taskHandeler
#from utils.taskHandeler import AgentManager as agent
#from utils.endpointHandeler import EndpointHandeler as endpointH
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
    agentManager.setUserActive(userId)

def handelNewRequest(agentManager, endpointManager):
    running = True
    while running:
        time.sleep(3)
        newUsers = agentManager.getWaitingUser()
        print(newUsers)
        input("waiting for res")
        if len(newUsers) <= 0:
            continue
        for user in newUsers:
            userId = user[0]
            target = agentManager.getUserTarger(userId)
            print(f"New User registered {userId}   Endpoint/Website: {target}")
            deployTask(agentManager=agentManager, endpoint=endpointManager, userId=userId, targer=target)


def taskRotator(agentManager, endpointManager):
    running = True
    while running:
        time.sleep(4)
        activeUsers = agentManager.getActiveUser()
        for user in activeUsers:
            userId = user[0]
            agentManager.getUserTaskOutputs(userId)



def main():
    secret_name = os.getenv("secret_name")
    rds_endpoint = os.getenv("rds_endpoint")
    region_name = os.getenv("AWS_DEFAULT_REGION")
    hostEndpoint = os.getenv("APIHOST")
    agentManager = AgentManager(secret_name, rds_endpoint, region_name, db_name="aiAssesDB4")
    endpoint = EndpointHandeler(host=hostEndpoint)
    deployTask(agentManager=agentManager, endpoint=endpoint, userId="347939e5-58d7-4f8c-bcdc-55995e1c2d62", targer="http://localhost:8000")
    taskRotator(agentManager, endpoint)

    #res = agentManager.createUser(name="john",email="john@gmail.com",endpoint="google.com", detailedReport=True)
    



    


if __name__ =="__main__":
    main()
