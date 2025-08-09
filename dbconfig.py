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
        try:
            print("initialising database connection...")
            self._connection_pool = ConnectionPool(
                                    max_connections=10,
                                    host = DB_HOST,
                                    user = DB_USERNAME,
                                    password = DB_PASSWORD,
                                    db = DATABASE
            )
            
            print("connection pool created successfully...")
            self.auth = auth()
            self.users = "users"
            self.api_keys_table = "api_keys"
            
        except Exception as e:
            print("database initialization failed...")
            raise RuntimeError(e)
        
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
    
    def create_user(self, user_id, password)->None:
        if len(password)<8:
            raise ValueError("minimum password length is 8")
        
        self.user_id = user_id
        self.password = self.auth.hash_password(password)
        with self._get_connection() as conn:
            try:
                with conn.cursor() as cursor:
                    query = "INSERT INTO `{}`(user_id, password_hash) VALUES (%s, %s)".format(self.users)
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
            key_data = self.auth.generate_api_key()
            try:
                with conn.cursor() as cursor:
                    query = """INSERT INTO `{}`(
                                user_id, key_hash, key_prefix, expires_at
                            )
                            VALUES(
                                %s, %s, %s, %s
                            )
                            """.format(self.api_keys_table)
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

    
    def check_user_data(self, user_id:str, password:str)->bool:
        if not self._user_exists(user_id):
            raise KeyError("User {user_id} not found")
        
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    query = "SELECT password_hash FROM users WHERE user_id = %s LIMIT 1"
                    cursor.execute(query, (user_id,))
                    result = cursor.fetchone()
                    
                    if not result:
                        return False 
                    
                    stored_hash = result[0]
                    
                    return self.auth.verify_password(password, stored_hash)
                    
        except Exception as e:
            conn.rollback()
            raise RuntimeError(f"Credential verification failed: {str(e)}")
        
class ConnectionPool:
    def __init__(self, max_connections=5, **kwargs):
        self._connections = Queue(max_connections)
        self.lock = threading.Lock()
        self._connection_args = kwargs
        
        for i in range(max_connections):
            try:
                conn = pymysql.connect(
                    connect_timeout=5,
                    **self._connection_args
                )
                conn.ping(reconnect=True)
                self._connections.put(conn)
                print(f"connection {i+1} established")
            except Exception as e:
                print(f"failed to establish connection {i+1}")
                raise RuntimeError(e)
            
    def get_connection(self):
        conn =  self._connections.get()
        try:
            conn.ping(reconnect=True)
            return conn
        except Exception:
            print("connection dead, establishing new connection...")
            new_conn = self._connections.get(**self._connection_args)
            self._connections.put(new_conn)
            return new_conn

    def release_connection(self, conn):
        try:
            if conn.open:
                self._connections.put(conn)
            else:
                print("Connection was closed, replacing...")
                self._connections.put(pymysql.connect(**self._connection_args))
        except Exception as e:
            print(f"Error releasing connection: {str(e)}")
            self._connections.put(pymysql.connect(**self._connection_args))      
                
    