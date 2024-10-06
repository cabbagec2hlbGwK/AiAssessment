import flask
import json
import requests
import os
import datetime
import uuid
import random
from utils.taskHandeler import AgentManager
TIMEOUT = 0.5


def main():
    secret_name = os.getenv("secret_name")
    rds_endpoint = os.getenv("rds_endpoint")
    region_name = os.getenv("AWS_DEFAULT_REGION")
    agentManager = AgentManager(secret_name, rds_endpoint, region_name, db_name="aiAssesDB2")

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
    for i in range(10):
        userId = random.choice(valid_user_ids)
        agentId = random.choice(valid_agent_ids)
        command = json.dumps({"command":"nmap -p- localhost"})
        id = agentManager.createTask(userId, agentId, command)
        print(f"task is created with {id}")


    


if __name__ =="__main__":
    main()
