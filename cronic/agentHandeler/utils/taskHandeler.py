from datetime import datetime
import uuid
import pymysql
import os
import json
import boto3
from pymysql.err import OperationalError
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
                port=3306, # Default MySQL port
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
        try:
            connection = pymysql.connect(
                host=self.rds_endpoint,
                user=self.secret["username"],
                password=self.secret["password"],
                port=3306,
                connect_timeout=5
            )
            with connection.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_name}")
                connection.commit()
                print(f"Database '{self.db_name}' created successfully.")
        finally:
            connection.close()

    def ensure_table_exists(self):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("DESCRIBE user_reg;")
            with self.connection.cursor() as cursor:
                cursor.execute("DESCRIBE task_list;")
        except pymysql.MySQLError as e:
            if e.args[0] == 1146:  # Error code for table not found
                print("Table does not exist. Creating table.")
                self.create_table()
            else:
                raise e

    def create_table(self):
        create_table_query_user= f"""
        CREATE TABLE IF NOT EXISTS user_reg (
            userId VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255),
            email VARCHAR(255),
            endpoint VARCHAR(255),
            Detailed BOOLEAN DEFAULT 0,
            jobState ENUM('success', 'error', 'expired', 'active') NOT NULL DEFAULT 'active',
            timeStamp TIMESTAMP
        );
        """
        create_table_query_task = f"""
        CREATE TABLE IF NOT EXISTS task_list (
            taskId VARCHAR(255) PRIMARY KEY,
            userId VARCHAR(255),
            AgentId VARCHAR(255),
            command VARCHAR(255),
            output BLOB DEFAULT "",
            error BLOB DEFAULT "",
            errorCounter INT DEFAULT 0,
            taskStatus ENUM('success', 'error', 'expired', 'active') NOT NULL DEFAULT 'active',
            hasMessageBeenSent BOOLEAN DEFAULT 0,
            updateTimeStamp TIMESTAMP,
            FOREIGN KEY (userId) REFERENCES user_reg(userId) ON DELETE CASCADE
        );
        """
        with self.connection.cursor() as cursor:
            cursor.execute(create_table_query_user)
            cursor.execute(create_table_query_task)
            self.connection.commit()

    def execute_query(self, query, data=None):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, data)
                result = cursor.fetchall()
                self.connection.commit()
                return result
        except pymysql.MySQLError as e:
            print(f"Query execution failed: {e}")
            self.connection.rollback()
            raise e

    def crateUser(self, name, email, endpoint, detailedReport):
        userId = str(uuid.uuid4())
        try:
            with self.connection.cursor() as cursor:
                insert_user_query = """
                INSERT INTO user_reg (userId, name, email, endpoint, Detailed)
                VALUES (%s, %s, %s, %s, %s);
                """
                cursor.execute(insert_user_query, (userId, name, email, endpoint, detailedReport))
                self.connection.commit()
                print(f"sucessfully created the user {name} with the userId : {userId}")
                return userId
        except pymysql.MySQLError as e:
            print(f"Error connecting to the database or inserting user information: {e}")
            return False

    def createTask(self, userId, agentId, command):
        taskId = str(uuid.uuid4())
        try:
            with self.connection.cursor() as cursor:
                insert_task_query = """
                INSERT INTO task_list (taskId, userId, AgentId, command, updateTimeStamp)
                VALUES (%s, %s, %s, %s, %s);
                """
                cursor.execute(insert_task_query, (taskId, userId, agentId, command, str(datetime.now())))
                self.connection.commit()
                print(f"New task with taskId '{taskId}' added successfully.")
                return taskId
        except pymysql.MySQLError as e:
            print(f"Error connecting to the database or inserting task information: {e}")
            return False
    def getAgentTask(self,agentId):
        query = "SELECT * FROM task_list WHERE AgentId = %s;"
        results = self.execute_query(query, (agentId,))
        return results

    def getTask(self,taskId):
        query = "SELECT * FROM task_list WHERE taskId = %s;"
        results = self.execute_query(query, (taskId,))
        return results
    def getUser(self, userId, userName=""):
        pass
    def getErrorCounter(self, taskId):
        with self.connection.cursor() as cursor:
            query = "SELECT errorCounter FROM task_list WHERE taskId = %s;"
            cursor.execute(query, (taskId,))
            result = cursor.fetchone()
            if result:
                return result
            return 0
    def agentHeartBeat(self,agentId):
        try:
            with self.connection.cursor() as cursor:
                query = "UPDATE task_list SET updateTimeStamp = %s WHERE AgentId = %s;"
                cursor.execute(query, (datetime.now(), agentId))
                self.connection.commit() 
                return True
        except Exception as e:
            print(e)
            return False
    def setTaskSuccess(self, taskId, output):
        try:
            with self.connection.cursor() as cursor:
                query = "UPDATE task_list SET output = %s WHERE taskId = %s"
                cursor.execute(query, (str(output), taskId))
                self.connection.commit() 
                return True
        except Exception as e:
            print(e)
            return False
    def setTaskError(self, taskId, error, errorCounter=None):
        if not errorCounter:
            errorCounter = int(self.getErrorCounter(taskId))+1
        try:
            with self.connection.cursor() as cursor:
                query = "UPDATE task_list SET error = %s WHERE taskId = %s"
                cursor.execute(query, (str(error), taskId))
                self.connection.commit() 
                return True
        except Exception as e:
            print(e)
            return False



    def close(self):
        try:
            self.connection.close()
            print("Connection closed.")
        except Exception as e:
            print(f"Failed to close connection: {e}")

def main():
    secret_name = os.getenv("secret_name")
    rds_endpoint = os.getenv("rds_endpoint")
    region_name = os.getenv("AWS_DEFAULT_REGION")
    db_manager = AgentManager(secret_name, rds_endpoint, region_name, db_name="aiAssesDB1")

    try:
        db_manager.execute_query("DESCRIBE user_reg;")

    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps("An error occurred.")
        }

    finally:
        db_manager.close()

if __name__=="__main__":
    main()
