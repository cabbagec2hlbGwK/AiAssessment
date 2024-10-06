import flask
import requests
import os
import datetime
import uuid
import random

TIMEOUT = 0.5

class Task:
    def __init__(self, taskId, command) -> None:
        self.taskId = taskId
        self.command = command
        self.healthCheck = datetime.datetime.now()
        self.state = "active"

    def updateHealth(self):
        self.healthCheck = datetime.datetime.now()
    def getUpdateInterval(self):
        return (datetime.datetime.now() - self.healthCheck).total_seconds() /60 
    def stateChecker(self):
        if self.getUpdateInterval() >= TIMEOUT:
            self.updateState("error")
            return False
        else:
            return True
    def updateState(self, state):
        if state in  "success" or state in "failed" or state in "active" or "error" in state:
            self.state = state
            return True
        else:
            print("wrong state was passed")
            return False



        
def runManagerEndpoint(manager):
    app = flask.app("MasterNode")
    @app.route("agentHealth", methods=['POST'])
    def updateAgent():
        pass
def runSheduler(master):
    pass

def main():
    master = WorkerManager()
    for a in range(30):
        master.registerTask(Task(taskId=str(uuid.uuid4),command=f"nmap -test {a}"))
    while True:
        os.system('cls')
        print(f"active connection : {len(master.tasks)}")
        task = master.tasks[random.randint(0,len(master.tasks)-2)]
        task.updateHealth()
        master.taskStateUpdator()

if __name__ =="__main__":
    main()
