import bcrypt
import secrets
import datetime
from datetime import timedelta

class auth:
    def __init__(self):
        self.name = "donbradman"
    
    def generate_api_key(self):
        raw_key = secrets.token_urlsafe(32)
        
        return {
            'raw_key'    : raw_key,
            'key_prefix' : raw_key[:8],
            'key_hash'   : self._hash_key(raw_key),
            'expires_at' : datetime.utcnow() + timedelta(days=30)
        }
    
    def auth_login(self):
        pass
    
    def validate_key(self):
        pass
    
    def hash_password(self, password):
        hash_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        return hash_password.decode()
    
    def authenticate(self):
        auth_header = self.headers.get("Authorization", "")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            self.send_error(401, "Unauthorized")
            
        api_key = auth_header.split(" ")[1]
        
            