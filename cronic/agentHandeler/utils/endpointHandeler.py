import requests 
import json
import os

class EndpointHandeler:
    def __init__(self, host, gcEndpoint = 'get_command', gpEndpoint = 'get_packages') -> None:
        self.host = host
        self.gc = gcEndpoint
        self.gp = gpEndpoint
    def getCommand(self, data):
        res = requests.post(url=f"{self.host}/{self.gc}", json={"body":str(data)})
        return res.json()
    def getPackages(self, data):
        res = requests.post(url=f"{self.host}/{self.gp}", json={"body":str(data)})
        return res.json()
        


def main():
    host = os.getenv("APIHOST")
    endpoint = EndpointHandeler(host=host)
    commands = endpoint.getCommand("google.com")
    packages = endpoint.getPackages(commands)
    print(packages)

if __name__=="__main__":
    main()
