import pymysql
import os
import json
import boto3
from pymysql.err import OperationalError
from botocore.exceptions import ClientError

class DatabaseManager:
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
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS user_reg (
            userId VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255),
            endpoint VARCHAR(255),
            Detailed BOOLEAN DEFAULT 0,
            jobState ENUM('success', 'error', 'expired', 'active') NOT NULL,
            timeStamp TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS task_list (
            taskId VARCHAR(255) PRIMARY KEY,
            userId VARCHAR(255),
            AgentId VARCHAR(255),
            command VARCHAR(255),
            output VARCHAR(255),
            error VARCHAR(255),
            errorCounter INT DEFAULT 0,
            taskStatus ENUM('success', 'error', 'expired', 'active') NOT NULL DEFAULT 'active',
            hasMessageBeenSent BOOLEAN DEFAULT 0,
            timeStamp TIMESTAMP,
            FOREIGN KEY (userId) REFERENCES user_reg(userId) ON DELETE CASCADE
        );
        """
        with self.connection.cursor() as cursor:
            cursor.execute(create_table_query)
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

    def close(self):
        try:
            self.connection.close()
            print("Connection closed.")
        except Exception as e:
            print(f"Failed to close connection: {e}")

# Example Usage
def main():
    secret_name = os.getenv("secret_name")
    rds_endpoint = os.getenv("rds_endpoint")
    region_name = os.getenv("AWS_DEFAULT_REGION")
    db_manager = DatabaseManager(secret_name, rds_endpoint, region_name, db_name="aiAssesDB")

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
