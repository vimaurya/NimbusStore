import bcrypt
import secrets
import datetime
import hashlib
import hmac
from datetime import timedelta, timezone
from dotenv import load_dotenv
import os
from functools import wraps
import jwt
from session import session_manager
from logs import logging
import ssl


load_dotenv()


TOKEN_BLOCKLIST = set()

class auth:
    def __init__(self):
        self.sessions = session_manager
        
        self.secret_key = os.getenv('API_KEY_SECRET', secrets.token_hex(32))
        self.SECRET = "sachinetendulkaristhegreatestcricketerofalltime"
        self.ALGORITHM = "HS256"
        self.TOKEN_EXPIRE_MINUTES = 5
    
    def session_required(self, func):
        @wraps(func)
        def wrapper(self_var, handler, *args, **kwargs):
            session_id = handler.headers.get("Session-ID")
            
            logging.info(f"retrieved session id : {session_id}")
            
            if not session_id:
                handler.send_error(401, "Invalid or expired session")
                return None
            
            session = self.sessions.get_session(session_id)
            
            logging.info(f"session from session_manager : {session}")
            
            if not session: 
                handler.send_error(401, "Invalid or expired session")
                return None
            
            handler.current_user = {
                'user_id' : session['user_id'],
                'session_id' : session_id
            }
            
            return func(self_var, handler, *args, **kwargs)
        
        return wrapper
    
    
    def jwt_required(self, func):
        @wraps(func)
        def wrapper(self_var, handler, *args, **kwargs):
            auth_header = handler.headers.get("Authorization")
            if not auth_header:
                handler.send_error(401, "Missing token")
                return None

            token = auth_header.split(" ")[1] 
            
            try:
                unverified = jwt.decode(token, options={"verify_signature": False})
                logging.info(f"Unverified token contents: {unverified}")
            except Exception as e:
                logging.error(f"Token decode failed: {e}")

            try:
                decoded = self.validate_jwt(token)
                logging.info(f"result of validate_jwt : {decoded}")
                if not decoded:
                    handler.send_error(401, "Invalid token")
                    return None
                    
                handler.token_data = decoded
                return func(self_var, handler, *args, **kwargs)
                
            except jwt.ExpiredSignatureError:
                handler.send_error(401, "Token expired")
                return None
            except jwt.InvalidTokenError as e:
                handler.send_error(401, f"Invalid token: {str(e)}")
                return None

        return wrapper
    
    
    def generate_api_key(self):
        raw_key = secrets.token_urlsafe(32)
        
        return {
            'raw_key': raw_key,
            'key_prefix': raw_key[:8],
            'key_hash': self._hash_key(raw_key),
            'expires_at': datetime.datetime.now() + datetime.timedelta(days=30)  
        }
        
    def _hash_key(self, key: str) -> str:
        return hmac.new(
            self.secret_key.encode(),
            key.encode(),
            hashlib.sha256
        ).hexdigest()
        
    def auth_login(self):
        pass
    
    def validate_key(self):
        pass
    
    def generate_jwt(self, user_id):
        try:
                now = datetime.datetime.now(timezone.utc)
                payload = {
                    "sub": user_id,
                    "iat": now, 
                    "exp": now + timedelta(hours=1)  
                }
                return jwt.encode(payload, self.SECRET, algorithm="HS256")
        except Exception as e:
            print(f"JWT generation failed: {str(e)}")
            raise RuntimeError("Could not generate authentication token")

            
    def validate_jwt(self, token):
        try:
            decoded = jwt.decode(
                token,
                self.SECRET,  
                algorithms=["HS256"],
                options={
                    "verify_iat": True,
                    "leeway": 10,  
                }
            )
            return decoded
        except jwt.PyJWTError as e:
            logging.error(f"JWT validation failed: {e}")
            return None    
        
    def verify_password(self, password, stored_hash)->bool:
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                stored_hash.encode('utf-8')
            )   
        except Exception as e:
            print(f"{str(e)}")
            return False
        
    def hash_password(self, password):
        hash_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        return hash_password.decode()
    
    
    def authenticate(self):
        auth_header = self.headers.get("Authorization", "")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            self.send_error(401, "Unauthorized")
            
        api_key = auth_header.split(" ")[1]
        
    def _is_connection_active(self, handler):
        try:
            handler.wfile.flush()
            return True
        except (ConnectionError, OSError, ssl.SSLEOFError):
            return False