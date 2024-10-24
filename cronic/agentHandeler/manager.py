import json
import os
import datetime
import uuid
import random
import time
import base64
import multiprocessing
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
    for commands in rawCommands:
        for command in commands.get("commands",[]):
            taskId = agentManager.createTask(userId=userId, agentId=agentId,command=str(command))
            tasks[taskId]={"command":[command]}
            taskRun.delay(agentId=agentId, tasks=tasks, packages=[], userId=userId)
            tasks = dict()
    agentManager.setUserActive(userId)

def handelNewRequest(agentManager, endpointManager):
    running = True
    print("New user watcher is running")
    while running:
        time.sleep(3)
        newUsers = agentManager.getWaitingUser()
        print(f"New users : {newUsers}")
        if len(newUsers) <= 0:
            continue
        for user in newUsers:
            userId = user[0]
            target = agentManager.getUserTarger(userId)
            print(f"New User registered {userId}   Endpoint/Website: {target}")
            deployTask(agentManager=agentManager, endpoint=endpointManager, userId=userId, targer=target)


def taskWatcher(agentManager):
    running = True
    print("Task Watcher is running")
    while running:
        time.sleep(90)
        activeUsers = agentManager.getActiveUser()
        for user in activeUsers:
            userId = user[0]
            for task in agentManager.getActiveTask(userId):
                taskId = task[0]
                if agentManager.getTaskUpTime(taskId) >= 10:
                    print(f"Task {taskId} is timeout")
                    agentManager.setTaskTimeout(taskId)
    
def processData(agentManager, endpointManager, userId):
    if agentManager.getUserCounter(userId) >= 3:
        data = agentManager.getUserSuccessTaskOutput(userId)
        information = agentManager.gerUserInfo(userId)
        res = endpointManager.getReport(f"# Key information: \n {information} \n# Additionnal information \n {data}")
        print(res)
        status = agentManager.setUserReport(userId, json.dumps(res))
        print(f"the report was {status}")
        print(f"User: {userId} is successfull completed {agentManager.setUserJobSuccess(userId)}")
        return
    data = agentManager.getUserTaskOutputs(userId)
    res = endpointManager.extInformation(str(data))
    print(f"The results is {res}")
    task = dict()
    print(f"Included additional innformation {agentManager.appendUserInformation(userId,res.get('information'))}")
    for command in res.get('next_steps'):
        taskId = agentManager.createTask(userId=userId, agentId="Null-12",command=str(command))
        task[taskId]={"command":[command]}
        taskRun.delay(agentId="Null-12", tasks=task, packages=[], userId=userId)
        task = dict()
    agentManager.incUserCounter(userId)
    agentManager.setUserTaskComplete(userId)

def taskRotator(agentManager, endpointManager):
    running = True
    print("Task Rotator us running")
    while running:
        time.sleep(10)
        activeUsers= agentManager.getActiveUser()
        for user in activeUsers:
            print("-"*80)
            userId = user[0]
            agentManager.userTaskStatus(userId)
            #agentManager.getUserTaskOutputs(userId)
            session = agentManager.isSessionCompleted(userId)
            print(f"User : {userId} sessionStatus: {session}")
            if session=="none":
                pass
            if session:
                processData(agentManager, endpointManager, userId)



def main():
    secret_name = os.getenv("secret_name")
    rds_endpoint = os.getenv("rds_endpoint")
    region_name = os.getenv("AWS_DEFAULT_REGION")
    hostEndpoint = os.getenv("APIHOST")
    agentManager = AgentManager(secret_name, rds_endpoint, region_name, db_name="aiAssesDB4")
    agentManagerTaskWatcher = AgentManager(secret_name, rds_endpoint, region_name, db_name="aiAssesDB4")
    agentManagerTaskRot = AgentManager(secret_name, rds_endpoint, region_name, db_name="aiAssesDB4")
    endpoint = EndpointHandeler(host=hostEndpoint)
    #deployTask(agentManager=agentManager, endpoint=endpoint, userId="347939e5-58d7-4f8c-bcdc-55995e1c2d62", targer="http://localhost:8000")
    #taskWatcher(agentManager)
    #taskRotator(agentManager, endpoint)
    agentNewRequestProcess = multiprocessing.Process(target=handelNewRequest, args=(agentManager, endpoint))
    agentTaskRotProcess = multiprocessing.Process(target=taskRotator, args=(agentManagerTaskRot, endpoint))
    agentWatcherProcess = multiprocessing.Process(target=taskWatcher, args=(agentManagerTaskWatcher,))

    agentNewRequestProcess.start()
    agentTaskRotProcess.start()
    agentWatcherProcess.start()
    #res = agentManager.createUser(name="john",email="john@gmail.com",endpoint="google.com", detailedReport=True)
    



    


if __name__ =="__main__":
    main()
