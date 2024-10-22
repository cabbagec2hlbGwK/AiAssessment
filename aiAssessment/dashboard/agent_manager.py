import boto3
import json
import pymysql
from pymysql import OperationalError
from botocore.exceptions import ClientError

class AgentManager:
    def __init__(self, secret_name, rds_endpoint, region_name, db_name="defaultDB"):
        self.rds_endpoint = rds_endpoint
        self.region_name = region_name
        self.secret = self.get_secret(secret_name)
        self.db_name = db_name
        self.connection = self.connect_to_database()
        self.ensure_table_exists()

    def get_secret(self, secret_name):
        session = boto3.session.Session()
        print(f"the region is {session.region_name}")
        client = session.client(
            service_name='secretsmanager',
            region_name=self.region_name
        )

        try:
            get_secret_value_response = client.get_secret_value(
                SecretId=secret_name
            )
            secret = get_secret_value_response['SecretString']
        except ClientError as e:
            raise e

        return json.loads(secret)

    def connect_to_database(self):
        try:
            connection = pymysql.connect(
                host=self.rds_endpoint,
                user=self.secret["username"],
                password=self.secret["password"],
                db=self.db_name,
                port=3306,  # Default MySQL port
                connect_timeout=5
            )
            print("Connection successful")
        except OperationalError as e:
            if e.args[0] == 1049:  # Error code for database not found
                print("Database not found, creating database.")
                self.create_database()
                connection = self.connect_to_database()  # try connecting again
            else:
                raise e
        return connection

    def create_database(self):
        # Implement the logic to create a database if it doesn't exist
        pass

    def get_django_database_settings(self):
        """Return the settings for Django's DATABASES configuration."""
        return {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': self.db_name,
            'USER': self.secret["username"],
            'PASSWORD': self.secret["password"],
            'HOST': self.rds_endpoint,
            'PORT': '3306',
        }
