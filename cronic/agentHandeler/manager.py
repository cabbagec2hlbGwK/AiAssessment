import flask
import json
import requests
import os
import datetime
import uuid
import random
import base64
from utils import endpointHandeler
from utils.taskHandeler import AgentManager
from utils.endpointHandeler import EndpointHandeler
from utils.kubeHandeler import KubeHandeler
TIMEOUT = 0.5

def deployTask(endpoint:EndpointHandeler, agentManager:AgentManager, k8:KubeHandeler, targer, userId):
    agentId = str(uuid.uuid4())
    rawCommands = endpoint.getCommand(targer)
    packages = endpoint.getPackages(rawCommands)
    if not packages:
        packages=[{}]
    packages = packages[0].get('packages','[]')
    tasks = dict()
    for commands in rawCommands:
        for command in commands.get("commands",[]):
            taskId = agentManager.createTask(userId=userId, agentId=agentId,command=str(command))
            tasks[taskId]={"command":[command]}
        print(tasks)
    k8.createPod(agentId=agentId, tasks=base64.b64encode(json.dumps(tasks).encode("utf-8")), packages=json.dumps(packages), masterEndpoint="test")




def main():
    secret_name = os.getenv("secret_name")
    rds_endpoint = os.getenv("rds_endpoint")
    region_name = os.getenv("AWS_DEFAULT_REGION")
    hostEndpoint = os.getenv("APIHOST")
    agentManager = AgentManager(secret_name, rds_endpoint, region_name, db_name="aiAssesDB2")
    endpoint = EndpointHandeler(host=hostEndpoint)
    k8 = KubeHandeler(agentImage="ubuntu")

    valid_user_ids = [
    "c9d9dd6d-f32f-4518-b90f-624ae281b95e",
    "54a96b2f-21b0-4dbb-be0b-750cd2c16aaf",
    "abc7d8bf-196b-4455-b880-f55c80553387"
    ]
    valid_agent_ids = [
        "89239373-c5e1-4fe4-aaa4-da5814119c88",
        "5da75265-bcbe-42b4-8629-46c88dcc6e6d",
        "bfaa3a74-b6e5-4c8d-8276-742728a00923"
    ]

    deployTask(agentManager=agentManager, endpoint=endpoint, k8=k8, userId=valid_user_ids[1], targer="http://mrgtec.com")


    


if __name__ =="__main__":
    main()
