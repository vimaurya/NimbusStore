import pymysql
import os
from dotenv import load_dotenv
from auth import auth

load_dotenv()

DATABASE = os.getenv("DATABASE")
PORT =  os.getenv("PORT")
TABLE = os.getenv("TABLE")
DB_HOST = os.getenv("DB_HOST")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_USERNAME = os.getenv("DB_USERNAME")


class create_connection:
    def __init__(self):
        self.host = DB_HOST
        self.port = PORT
        self.db_username = DB_USERNAME
        self.db_password = DB_PASSWORD
        self.database = DATABASE
        self.table = TABLE
        
    def create_connection(self):
        
        connection = pymysql.connect(
            host = self.host,
            user = self.db_username,
            password = self.password,
            database = self.database,
            charset = 'utf8m4'
        )
        return connection
                
                
                
class database:
    def __init__(self, user):
        self.user = user
    
    
    def create_user(self, connection, user_id, password):
        self.connection = connection
        self.user_id = user_id
        self.password = auth.hash_password(password)
        
    def fetch_api_key(self, user):
        pass