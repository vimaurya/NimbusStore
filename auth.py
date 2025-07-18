import bcrypt
import secrets
import datetime
import hashlib
import hmac
from datetime import timedelta
from dotenv import load_dotenv
import os
from functools import wraps
import jwt

load_dotenv()


TOKEN_BLOCK = set()


class auth:
    def __init__(self):
        self.secret_key = os.getenv('API_KEY_SECRET', secrets.token_hex(32))
        self.name = "donbradman"
    
    
    def jwt_required(self, func):
        @wraps(func)
        def wrapper(self_var, handler, *args, **kwargs):
            auth_header = handler.headers.get("Authorization")

            if not auth_header or not auth_header.startswith("Bearer "):
                return handler.send_error(404, "Missing or invalid token")

            try:
                decoded_token = auth.validate_jwt(auth_header)
                if decoded_token:
                    g.user = decoded_token 
                    g.username = g.user['username']
                else:
                    hanlder.send_error(401, "Invalid token")
            except jwt.ExpiredSignatureError:
                handler.send_error(401, "Token has expired")
            except jwt.InvalidTokenError:
                handler.send_error(401, "Invalid token")

            return func(self_var, handler, *args, **kwargs)

        return wrapper

    def generate_api_key(self):
        raw_key = secrets.token_urlsafe(32)
        
        return {
            'raw_key'    : raw_key,
            'key_prefix' : raw_key[:8],
            'key_hash'   : self._hash_key(raw_key),
            'expires_at' : datetime.datetime.utcnow() + timedelta(days=30)
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
    
    def generate_jwt(self, payload):
        exp = datetime.now() + timedelta(minutes=5)
        payload["exp"] = exp.timestamp()
        print(f"payload : {payload}")
        JWT = jwt.encode(payload, SECRET, algorithm="HS256")
        print(JWT)
        return JWT
            
            
    def validate_jwt(self, token):
        try:
            token = token.split(" ")[1]
            
            if token in TOKEN_BLOCKLIST:
                raise jwt.ExpiredSignatureError
            
            decoded_token = jwt.decode(token, SECRET, algorithms=["HS256"])
            print(f'User : {decoded_token}')
            return decoded_token
        except Exception as e:
            print(f'Exception verifying jwt : {e}')
            raise RuntimeError(e)
        
        
    def hash_password(self, password):
        hash_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        return hash_password.decode()
    
    
    def authenticate(self):
        auth_header = self.headers.get("Authorization", "")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            self.send_error(401, "Unauthorized")
            
        api_key = auth_header.split(" ")[1]
        
            