import subprocess

class Agent:
    def __init__(self, endpoint, taskId, packages, commands, envCommands) -> None:
        self.masterEndpoint = endpoint
        self.taskId= taskId
        self.packages = packages
        self.envCommands = envCommands
        self.commands = commands

    def callBack(self):
        pass
    def setup(self):
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
            print("in progress")
            if status.get('success'):
                output += f"\nthe output for the command \n --- \n {status.get('output','Null')}"
            else:
                error.append({"command":command,"error":f"the message is {status.get('error','none')}"})
        return {"output":output, "failedCommands":error}

    def runCommand(self, command):
        try:
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


agent = Agent(taskId="",endpoint="",packages=["nmap", "python3", "curl"], envCommands=[], commands=["nmap -p- localhost", "curl google.com"])
state = agent.execute()
print(state)





