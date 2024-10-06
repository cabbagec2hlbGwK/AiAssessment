import flask
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
    id = agentManager.crateUser(name="asher", email="asher@asher.com",endpoint="https://google.com",detailedReport=False)
    print(id)
    id = agentManager.crateUser(name="james", email="asher@asher.com",endpoint="https://google.com",detailedReport=False)
    print(id)
    id = agentManager.crateUser(name="bananna", email="asher@asher.com",endpoint="https://google.com",detailedReport=False)
    print(id)

    


if __name__ =="__main__":
    main()
