import boto3
import json
import pymysql
import uuid
from datetime import datetime
from pymysql import OperationalError
from botocore.exceptions import ClientError

class AgentManager:
    def __init__(self, secret_name=None, rds_endpoint=None, region_name=None, db_name="defaultDB", use_local=False):
        self.use_local = use_local
        self.db_name = db_name
        
        if use_local:
            # Local database connection settings
            self.connection = self.connect_to_local_database()
        else:
            # AWS RDS connection settings
            self.rds_endpoint = rds_endpoint
            self.region_name = region_name
            self.secret = self.get_secret(secret_name)  # Get secrets from AWS
            self.connection = self.connect_to_database()
        
        self.ensure_table_exists()  # Ensure the table exists

    def get_secret(self, secret_name):
        if not self.use_local:  # Only get secrets if not in local mode
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
        return {
            "username": "local_user",  # Replace with your local username
            "password": "local_password",  # Replace with your local password
        }

    def connect_to_local_database(self):
        try:
            connection = pymysql.connect(
                host='127.0.0.1',
                user='django_user',  
                password='django_password',
                db='django_db',
                port=3306, 
                connect_timeout=5
            )
            print("Local Connection successful")
        except OperationalError as e:
            print(f"Error connecting to local database: {e}")
            raise e
        return connection

    def connect_to_database(self):
        try:
            connection = pymysql.connect(
                host=self.rds_endpoint,
                user=self.secret["username"],
                password=self.secret["password"],
                db=self.db_name,
                port=3306,
                connect_timeout=5
            )
            print("RDS Connection successful")
        except OperationalError as e:
            if e.args[0] == 1049:  # Database not found
                print("Database not found, creating database.")
                self.create_database()
                connection = self.connect_to_database()  # Try connecting again
            else:
                raise e
        return connection

    def get_django_database_settings(self):
        """Return the settings for Django's DATABASES configuration."""
        return {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'django_db',
            'USER': self.secret["username"] if not self.use_local else 'django_user',
            'PASSWORD': self.secret["password"] if not self.use_local else 'django_password',
            'HOST': self.rds_endpoint if not self.use_local else '127.0.0.1',
            'PORT': '3306',
        }

    # Function to write (insert) user data into the database
    def insert_user(self, name, email, endpoint, detailed_report):
        user_id = str(uuid.uuid4())  # Generate a unique UUID for the user
        try:
            with self.connection.cursor() as cursor:
                insert_user_query = """
                INSERT INTO user_reg (userId, name, email, endpoint, Detailed)
                VALUES (%s, %s, %s, %s, %s);
                """
                cursor.execute(insert_user_query, (user_id, name, email, endpoint, detailed_report))
                self.connection.commit()  # Commit the transaction
                print(f"Successfully created the user {name} with the userId: {user_id}")
                return user_id
        except Exception as e:
            print(f"Error inserting user: {e}")
            return False

    # # Function to read (fetch) user data from the database
    # def fetch_user(self, user_id):
    #     try:
    #         with self.connection.cursor() as cursor:
    #             select_user_query = """
    #             SELECT userId, name, email, endpoint, resultData
    #             FROM user_reg
    #             WHERE userId = %s AND Detailed = 0;
    #             """
    #             cursor.execute(select_user_query, [user_id])
    #             user_data = cursor.fetchone()  # Fetch one row from the result
    #             return user_data  # Return the user data tuple (or None if not found)
    #     except Exception as e:
    #         print(f"Error fetching user: {e}")
    #         return None



    def fetch_user(self, user_id):
        try:
            with self.connection.cursor() as cursor:
                select_user_query = """
                SELECT name, email, endpoint, resultData
                FROM user_reg
                WHERE userId = %s AND Detailed = 0;
                """
                cursor.execute(select_user_query, [user_id])
                user_data = cursor.fetchone()  # Fetch one row from the result
                
                if user_data:
                    # Extract individual fields
                    name = user_data[0]      # Name is at index 0
                    email = user_data[1]     # Email is at index 1
                    endpoint = user_data[2]   # Endpoint is at index 2
                    result_data_blob = user_data[3]  # resultData is at index 3

                    # Decode and parse JSON from the BLOB
                    result_data = json.loads(result_data_blob.decode('utf-8')) if result_data_blob else None

                    # Create a dictionary to return
                    user_data_dict = {
                        'name': name,
                        'email': email,
                        'endpoint': endpoint,
                        'resultData': result_data  # Include the parsed resultData
                    }
                    return user_data_dict  # Return the user data dictionary
                
                # Log if no user data was found
                print(f"No user found for user_id: {user_id}")
                return None  # Return None if no data is found
        except Exception as e:
            print(f"Error fetching user: {e}")  # Log the error
            return None


    def ensure_table_exists(self):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("DESCRIBE user_reg;")
        except pymysql.MySQLError as e:
            if e.args[0] == 1146:  # Error code for table not found
                print("Table does not exist. Creating table.")
                self.create_table()
            else:
                raise e
