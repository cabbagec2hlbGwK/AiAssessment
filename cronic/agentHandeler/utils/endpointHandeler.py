import requests 
import json
import os

class EndpointHandeler:
    def __init__(self, host, gcEndpoint = 'get_command', gpEndpoint = 'get_packages', extInformation = 'ext_information') -> None:
        self.host = host
        self.gc = gcEndpoint
        self.gp = gpEndpoint
        self.ei = extInformation
    def getCommand(self, data):
        res = requests.post(url=f"{self.host}/{self.gc}", json={"body":str(data)})
        for counter in range(5):
            if res.json()[0].get('commands'):
                print(res.json()[0].get("commands"))
                return res.json()
            res = requests.post(url=f"{self.host}/{self.gc}", json={"body":str(data)})

        return res.json()
    def getReport(self, data):
        res = requests.post(url=f"{self.host}/{self.gp}", json={"body":str(data)})
        if res:
            return res.json()[0]
        return None

    def extInformation(self, data):
        res = requests.post(url=f"{self.host}/{self.ei}", json={"body":str(data)})
        if res.json():
            return res.json()[0]
        return res.json()
        


def main():
    host = os.getenv("APIHOST")
    endpoint = EndpointHandeler(host=host)
    commands = endpoint.getCommand("google.com")
    packages = endpoint.getPackages(commands)
    print(packages)

if __name__=="__main__":
    main()
