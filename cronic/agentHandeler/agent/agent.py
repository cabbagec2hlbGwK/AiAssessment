import subprocess
import datetime
import requests
import os
import json
import base64
from celery import Celery

class workerDivider:
    def __init__(self, brokerHost, brokerPassword, brokerPort= 6379, dbNumber = 0) -> None:
        self.brokerHost = brokerHost
        self.brokerPassword= brokerPassword
        self.brokerPort = brokerPort
        self.dbNumber = dbNumber
        self.brokerCon = self.creatBrokerConnection()

    def creatBrokerConnection(self):
        app = Celery('tasks', broker=f'redis://localhost:{self.brokerPort}/{self.dbNumber}')



class Agent:
    def __init__(self, taskId, packages, commands, envCommands) -> None:
        self.taskId= taskId
        self.packages = packages
        self.envCommands = envCommands
        self.commands = commands

    def callBack(self):
        pass
    def setup(self):
        if not self.packages:
            return
        isUpdate = self.runCommand("apt update")
        if not isUpdate.get('success',""):
            print(f"ther was an issue with the update {isUpdate.get('error')}")
        for aptPackages in self.packages:
            status = self.runCommand(f"apt install {aptPackages} -y")
            if not status.get("success",""):
                print(f"The package {aptPackages} was npt successfully installed because {status.get('erroe', 'Ther is no message in the error')}")
        for command in self.envCommands:
            status = self.runCommand(command)
            if not status.get("success",""):
                print("The commad had some issue running" + command)

    def execute(self):
        self.setup()
        error = []
        output = ""
        for command in self.commands:
            status = self.runCommand(command)
            if status.get('success'):
                output += f"{status.get('output','Null')}"
            else:
                error.append({"command":command,"error":f"the message is {status.get('error','none')}"})
        return {"output":output, "failedCommands":error}

    def runCommand(self, command):
        try:
            print(f"running :{command}")
            process = subprocess.Popen(
                ['/bin/bash', '-c', command],  
                stdout=subprocess.PIPE,       
                stderr=subprocess.PIPE,      
                text=True                   
            )

            stdout, stderr = process.communicate()
            if process.returncode == 0:
                return {
                    "success": True,
                    "output": stdout,
                    "error": stderr
                }
            else:
                return {
                    "success": False,
                    "output": stdout,
                    "error": stderr,
                    "message": f"Command failed with return code {process.returncode}"
                }

        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "message": "An error occurred while executing the command"
            }


def release(results, agentId, callback):
    res = requests.post(url=callback,json=json.dumps({"agentId":agentId, "results":results,"})) 
class agentProbe:
    def __init__(self, endpoint, agentId) -> None:
        self.agentId = agentId
        self.endpoint = endpoint
        self.startTime = datetime.datetime.now()
    def heartBeats(self):
        requests.post(url=self.endpoint+"/heartBeats", json= json.dumps({"agentId":self.agentId,"upTime":str((datetime.datetime.now()-self.startTime).total_seconds()/60)}))


def main(tasks, packages, agentId, masterEndpoint):
    try:
        results = dict()
        for key, values in tasks.items():
            agent = Agent(taskId="",packages=[], envCommands=[], commands=values.get("command"))
            result = agent.execute()
            print(f"key is {key}")
            results[key]={"results":result}
        release(results=results, agentId=agentId, callback=masterEndoint)
        retunr 0
    except Exception as e:
        print(e)


        

if __name__=="__main__":
    main()




