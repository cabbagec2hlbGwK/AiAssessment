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
        create_table_query_user = """
        CREATE TABLE IF NOT EXISTS user_reg (
            userId VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255),
            email VARCHAR(255),
            endpoint VARCHAR(255),
            Detailed BOOLEAN DEFAULT 0,
            jobState ENUM('success', 'error', 'expired', 'active', 'waiting') NOT NULL DEFAULT 'waiting',
            timeStamp TIMESTAMP,
            counter INT DEFAULT 0,
            resultData BLOB DEFAULT NULL,
            information VARCHAR(255) DEFAULT ""
        );
        """
        create_table_query_task = """
        CREATE TABLE IF NOT EXISTS task_list (
            taskId VARCHAR(255) PRIMARY KEY,
            userId VARCHAR(255),
            AgentId VARCHAR(255),
            command VARCHAR(255),
            output BLOB DEFAULT NULL,
            error BLOB DEFAULT NULL,
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

    def createUser(self, name, email, endpoint, detailedReport):
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
    def getUserTask(self,userId):
        query = "SELECT taskId FROM task_list WHERE userId = %s;"
        results = self.execute_query(query, (userId,))
        return results
    def getUserSuccessTask(self,userId):
        query = "SELECT taskId FROM task_list WHERE userId = %s AND taskStatus = 'success';"
        results = self.execute_query(query, (userId,))
        return results
    def getUserErrorTask(self,userId):
        query = "SELECT taskId FROM task_list WHERE userId = %s AND taskStatus = 'error';"
        results = self.execute_query(query, (userId,))
        return results
    def getTaskUpTime(self, taskId):
        startTime = self.getTaskTimeStamp(taskId)
        diffrence = datetime.now() - startTime 
        return diffrence.total_seconds() / 60
    def getUserTaskOutputs(self, userId):
        success = self.getCompletedTask(userId)
        data = ""
        for task in success:
            taskId = task[0]
            data +=f"## Command: {self.getTaskCommand(taskId)} \n output: {self.getTaskOutput(taskId)} Error: {self.getTaskError}\n---\n"
        return data
    def getUserSuccessTaskOutputs(self, userId):
        success = self.getUserSuccessTask(userId)
        data = ""
        for task in success:
            taskId = task[0]
            data +=f"## Command: {self.getTaskCommand(taskId)} \n {self.getTaskOutput(taskId)} \n---\n"
        return data



    def userTaskStatus(self, userId):
        success = len(self.getUserSuccessTask(userId))
        error = len(self.getUserErrorTask(userId))
        total = len(self.getUserTask(userId))
        print(f"Total Successfull Tasks: {success}, Total Error Task: {error}, Total Task: {total}")

    def getTask(self,taskId):
        query = "SELECT * FROM task_list WHERE taskId = %s;"
        results = self.execute_query(query, (taskId,))
        return results
    def getTaskCommand(self, taskId):
        with self.connection.cursor() as cursor:
            query = "SELECT command FROM task_list WHERE taskId = %s;"
            cursor.execute(query, (taskId,))
            result = cursor.fetchone()
            if result:
                return result[0]
            return 0

    def getTaskOutput(self, taskId):
        with self.connection.cursor() as cursor:
            query = "SELECT output FROM task_list WHERE taskId = %s;"
            cursor.execute(query, (taskId,))
            result = cursor.fetchone()
            if result:
                return result[0]
            return 0
    def getTaskError(self, taskId):
        with self.connection.cursor() as cursor:
            query = "SELECT error FROM task_list WHERE taskId = %s;"
            cursor.execute(query, (taskId,))
            result = cursor.fetchone()
            if result:
                return result[0]
            return 0
    def getTaskTimeStamp(self, taskId):
        with self.connection.cursor() as cursor:
            query = "SELECT updateTimeStamp FROM task_list WHERE taskId = %s;"
            cursor.execute(query, (taskId,))
            result = cursor.fetchone()
            if result:
                return result[0]
            return 0
    def getCompletedTask(self, userId):
        query = "SELECT taskId FROM task_list WHERE userId = %s AND taskStatus IN ('success', 'error') AND hasMessageBeenSent = FALSE;"
        results = self.execute_query(query, (userId,))
        return results

    def getActiveTask(self, userId):
        query = "SELECT taskId FROM task_list WHERE userId = %s AND taskStatus ='active' AND hasMessageBeenSent = FALSE;"
        results = self.execute_query(query, (userId,))
        return results
    def isSessionCompleted(self, userId):
        totalActiveTask = len(self.getActiveTask(userId))
        totalCompletedTask = len(self.getCompletedTask(userId))
        total = totalActiveTask + totalCompletedTask
        if total == 0:
            return "none"
        if totalActiveTask > 0:
            return False
        else:
            return True

    def getUser(self, userId):
        query = "SELECT * FROM user_reg WHERE userId = %s;"
        results = self.execute_query(query, (userId,))
        return results
    def getWaitingUser(self):
        query = "SELECT userId FROM user_reg WHERE jobState = 'waiting';"
        results = self.execute_query(query)
        return results
    def getActiveUser(self):
        query = "SELECT userId FROM user_reg WHERE jobState = 'active';"
        results = self.execute_query(query)
        return results
    def getUserTarger(self, userId):
        with self.connection.cursor() as cursor:
            query = "SELECT endpoint FROM user_reg WHERE userId = %s;"
            cursor.execute(query, (userId,))
            result = cursor.fetchone()
            if result:
                return result[0]
            return 0
    def getUserInfo(self, userId):
        with self.connection.cursor() as cursor:
            query = "SELECT information FROM user_reg WHERE userId = %s;"
            cursor.execute(query, (userId,))
            result = cursor.fetchone()
            if result:
                return str(result[0])
            return 0
    def getUserCounter(self, userId):
        with self.connection.cursor() as cursor:
            query = "SELECT counter FROM user_reg WHERE userId = %s;"
            cursor.execute(query, (userId,))
            result = cursor.fetchone()
            if result:
                return int(result[0])
            return 0
    def getErrorCounter(self, taskId):
        with self.connection.cursor() as cursor:
            query = "SELECT errorCounter FROM task_list WHERE taskId = %s;"
            cursor.execute(query, (taskId,))
            result = cursor.fetchone()
            if result:
                return result[0]
            return 0
    def incUserCounter(self, userId):
        try:
            with self.connection.cursor() as cursor:
                query = "UPDATE user_reg SET counter = %s WHERE userId = %s"
                cursor.execute(query, (self.getUserCounter(userId)+1, userId))
                self.connection.commit() 
                return True
        except Exception as e:
            print(e)
            return False
    def setUserActive(self, userId):
        try:
            with self.connection.cursor() as cursor:
                query = "UPDATE user_reg SET jobState = 'active' WHERE userId = %s"
                cursor.execute(query, (userId))
                self.connection.commit() 
                return True
        except Exception as e:
            print(e)
            return False
    def setUserJobSuccess(self, userId):
        try:
            with self.connection.cursor() as cursor:
                query = "UPDATE user_reg SET jobState = 'success' WHERE userId = %s"
                cursor.execute(query, (userId))
                self.connection.commit() 
                return True
        except Exception as e:
            print(e)
            return False
    def setUserReport(self, userId, report):
        try:
            with self.connection.cursor() as cursor:
                query = "UPDATE user_reg SET resultData = %s WHERE userId = %s"
                cursor.execute(query, (report, userId,))
                self.connection.commit() 
                return True
        except Exception as e:
            print(e)
            return False
    def appendUserInformation(self, userId, data):
        try:
            with self.connection.cursor() as cursor:
                query = "UPDATE user_reg SET information = %s WHERE userId = %s"
                cursor.execute(query, (str(self.getUserInfo(userId))+str(data), userId))
                self.connection.commit() 
                return True
        except Exception as e:
            print(e)
            return False
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
# taskStatus ENUM('success', 'error', 'expired', 'active') NOT NULL DEFAULT 'active',

    def setTaskSuccess(self, taskId, output):
        try:
            with self.connection.cursor() as cursor:
                query = "UPDATE task_list SET output = %s, taskStatus = 'success' WHERE taskId = %s"
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
                query = "UPDATE task_list SET error = %s, taskStatus = 'error' WHERE taskId = %s"
                cursor.execute(query, (str(error), taskId))
                self.connection.commit() 
                return True
        except Exception as e:
            print(e)
            return False
    def setTaskTimeout(self, taskId):
        try:
            with self.connection.cursor() as cursor:
                query = "UPDATE task_list SET error = 'TIMEOUT TASK', taskStatus = 'error' WHERE taskId = %s"
                cursor.execute(query, (taskId,))
                self.connection.commit() 
                return True
        except Exception as e:
            print(e)
            return False

    def setUserTaskComplete(self, userId):
        query = "UPDATE task_list SET hasMessageBeenSent = TRUE WHERE userId = %s AND taskStatus IN ('success', 'error');"
        results = self.execute_query(query, (userId,))
        return results


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
