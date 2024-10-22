import subprocess
import requests
import json
from cronic.agentHandeler.tasks.release import release
from cronic.agentHandeler.celeryW import app

class Agent:
    def __init__(self, taskId, packages, commands, envCommands) -> None:
        self.taskId = taskId
        self.packages = packages
        self.envCommands = envCommands
        self.commands = commands

    def callBack(self):
        pass

    def setup(self):
        if not self.packages:
            return
        isUpdate = self.runCommand("apt update")
        if not isUpdate.get('success', ""):
            print(f"There was an issue with the update {isUpdate.get('error')}")
        for aptPackage in self.packages:
            status = self.runCommand(f"apt install {aptPackage} -y")
            if not status.get("success", ""):
                print(f"The package {aptPackage} was not successfully installed because {status.get('error', 'There is no message in the error')}")
        for command in self.envCommands:
            status = self.runCommand(command)
            if not status.get("success", ""):
                print(f"The command had some issue running: {command}")

    def execute(self):
        self.setup()
        error = []
        output = ""
        for command in self.commands:
            status = self.runCommand(command)
            if status.get('success'):
                output += f"{status.get('output','Null')}"
            else:
                error.append({"command": command, "error": f"the message is {status.get('error','none')}"})
        print(f"error is :{error} \n-----------------------\n output is {output}")
        return {"output": output, "failedCommands": error}

    def runCommand(self, command):
        try:
            print(f"Running: {command}")
            process = subprocess.Popen(
                ['/bin/bash', '-c', command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout, stderr = process.communicate()
            if process.returncode == 0:
                return {"success": True, "output": stdout, "error": stderr}
            else:
                return {"success": False, "output": stdout, "error": stderr, "message": f"Command failed with return code {process.returncode}"}

        except Exception as e:
            return {"success": False, "output": "", "error": str(e), "message": "An error occurred while executing the command"}



@app.task()
def taskRun(tasks, packages, agentId, userId):
    try:
        results = dict()
        for key, values in tasks.items():
            tempStore = {}
            agent = Agent(taskId="", packages=packages, envCommands=[], commands=values.get("command"))
            result = agent.execute()
            print(f"key is {key}")
            tempStore[key] = {"results": result}
            print("--------------------------------------------------------------")
            print(tempStore)
            release.delay(results=tempStore, agentId=agentId, userId=userId)
            results[key] = {"results": result}
        return 0
    except Exception as e:
        print(e)

if __name__ == "__main__":
    pass
