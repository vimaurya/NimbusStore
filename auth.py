
class auth:
    def create_user():
        pass
    
    def generate_api_key():
        pass
    
    def auth_login():
        pass
    
    def validate_key():
        pass
    
    def authenticate(self):
        auth_header = self.headers.get("Authorization", "")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            self.send_error(401, "Unauthorized")
            
        api_key = auth_header.split(" ")[1]
        
            