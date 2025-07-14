import pymysql
import os
from dotenv import load_dotenv
from auth import auth
import threading
from queue import Queue
from contextlib import contextmanager

load_dotenv()

DATABASE = os.getenv("DATABASE")
PORT =  int(os.getenv("PORT"))
TABLE = os.getenv("TABLE")
DB_HOST = os.getenv("DB_HOST")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_USERNAME = os.getenv("DB_USERNAME")


class Database:
    def __init__(self):
        self._connection_pool = ConnectionPool(max_connections=10)
        self.auth = auth()
        self.users_table = "users"
        self.api_key_table = "api_keys"

    @contextmanager
    def _get_connection(self):
        conn = self._connection_pool.get_connection()
        try:
            yield conn
        finally:
            self._connection_pool.release_connection(conn)

    def _user_exists(self, user_id:str)->bool:
        with self._get_connection() as conn:
            try:
                with conn.cursor() as cursor:
                    query = "SELECT * FROM `{}` WHERE user_id=%s LIMIT 1".format(self.users)
                    
                    cursor.execute(query, (user_id, ))
                    
                    return bool(cursor.fetchone())
                
            except Exception as e:
                raise RuntimeError(e)
    
    def create_user(self, user_id, password):
        if len(password)<8:
            raise ValueError("minimum password length is 8")
        
        self.user_id = user_id
        self.password = self.auth.hash_password(password)
        
        with self._get_connection() as conn:
            try:
                with conn.cursor() as cursor:
                    query = "INSERT INTO `{}`(user_id, password) VALUES (%s, %s)".format(self.users)
                    cursor.execute(query, (self.user_id, self.password))
                    
                conn.commit()
            except pymysql.IntegrityError:
                raise ValueError("user already exists")
            except Exception as e:
                conn.rollback()
                raise RuntimeError(f"user creation failed : {str(e)}")
        
        
    def create_api_key(self, user_id):
        if not self._user_exists(user_id):
            raise KeyError(f"User {user_id} not found")

        with self._get_connection() as conn:
            key_data = self.auth.generate_api_key(user_id)
            try:
                with conn.cursor() as cursor:
                    query = """INSERT INTO TABLE `{}`(
                                user_id, key_hash, key_prefix, expires_at
                            )
                            VALUES(
                                %s, %s, %s, %s
                            )
                            """.format(self.api_key_table)
                    cursor.execute(query, (
                        user_id, 
                        key_data['key_hash'], 
                        key_data['key_prefix'],
                        key_data['expires_at'])
                       )
                    
                conn.commit()
                
                return key_data['raw_key']
                
            except Exception as e:
                conn.rollback()
                raise RuntimeError(f"Key storage failed: {str(e)}")



class ConnectionPool:
    def __init__(self, max_connections=5):
        self._connections = Queue(max_connections)
        self.lock = threading.Lock()
        
        for _ in range(max_connections):
            self._connections.put(pymysql.connect(
                host=DB_HOST,
                port=PORT,
                user=DB_USERNAME,
                password=DB_PASSWORD,
                database=DATABASE
            ))

    def get_connection(self):
        return self._connections.get()

    def release_connection(self, conn):
        self._connections.put(conn)       
                
    