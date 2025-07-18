import mimetypes
import json
import re
import shortuuid
import os
import ssl
import dbconfig
from auth import auth


auth = auth()

class util_funcs:
    def __init__(self, STORAGE_PATH):
        self.STORAGE_PATH = STORAGE_PATH
        self.CHUNK_SIZE = 1024 * 64  
        mimetypes.init()
        
    def signup(self, handler):
        try:
            content_type = handler.headers['Content-Type']
            if content_type != 'application/json':
                handler.send_error(415, "only json data accepted")
                return 
            
            content_length = int(handler.headers.get('Content-Length', 0))
            post_data = handler.rfile.read(content_length)
            
            user_data = json.loads(post_data)
            
            print(f"this is user data : {user_data}")
            
            required = ['user_id', 'password']
            
            if not all(field in user_data for field in required):
                handler.send_error(400, "missing required field(s)")
                return
            
            user_id = user_data['user_id']
            password = user_data['password']
            
            if not user_id or not password:
                raise ValueError("required fields can not be empty")
            
            #database operations
            
            db = dbconfig.Database()
            
            db.create_user(user_id, password)
        
            api_key = db.create_api_key(user_id)
            
            if api_key:
                token = auth.generate_jwt({"user" : f"{user_id}"})
                handler.send_response(201)
                handler.send_header("Content-Type", "application/json")
                handler.end_headers()

                response = {
                    "success": True,
                    "user_id" : user_id,
                    "api_key" : f"{api_key}",
                    "message" : "handle the api keys with safety, store it in a trusted location",
                    "jwt"     : f"{token}"
                }
                
                handler.wfile.write(json.dumps(response).encode())  
            else:
                handler.send_error(500, "can not generate api key for user : {user}")
    
            
        except Exception as e:
            handler.send_error(500, f"{str(e)}")
        
    @auth.jwt_required   
    def files(self, handler):
        handler.send_response(200)
        handler.send_header("Content-Type", "application/json")
        handler.end_headers()
        
        dirs = os.listdir(self.STORAGE_PATH)

        response = {"Files":f"{dirs}"}
        handler.wfile.write(json.dumps(response).encode())   
        
    @auth.jwt_required
    def file_by_id(self, handler, file_id):
        try:
            print(f"Requested file: {file_id}")
            
            file_path = os.path.join(self.STORAGE_PATH, file_id)
            print(f"Resolved path: {file_path}")
            
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Path {file_path} doesn't exist")
            
            user_agent = handler.headers.get('User-Agent', '').lower()
            
            print (f"user agent : {user_agent}")
            
            non_showable_agents = ['curl', 'powershell', 'wget', 'python-requests']
            if any(agent in user_agent for agent in non_showable_agents):
                handler.send_response(200)
                handler.send_header('Content-Type', 'application/json')
                handler.end_headers()
                
                host = handler.headers.get('Host', 'localhost:8000')
            
                #host = 'localhost:8000'
                
                protocol = "http"
                
                if hasattr(handler.server, 'socket') and isinstance(handler.server.socket, ssl.SSLSocket):
                    protocol = "https"
                
                response = {
                    "preview_link": f"{protocol}://{host}/api/files/{file_id}",
                    "download_link": f"{protocol}://{host}/api/files/{file_id}?download=true"
                }
                handler.wfile.write(json.dumps(response).encode())
                return
            else:
                download = 'download=true' in handler.path
                self._serve_file(handler, file_path, not download)
                
        except FileNotFoundError as e:
            handler.send_error(404, str(e))
        except Exception as e:
            handler.send_error(500, f"Server error: {str(e)}")
            print(f"Error serving file: {e}")


    def _serve_file(self, handler, file_path, preview=True):
        try:
            mime_type, _ = mimetypes.guess_type(file_path)
            mime_type = mime_type or "application/octet-stream"
            
            file_size = os.path.getsize(file_path)
            filename = os.path.basename(file_path)
            
            handler.send_response(200)
            handler.send_header('Content-Type', mime_type)
            handler.send_header('Content-Length', str(file_size))
            
            if preview and mime_type.startswith(('image/', 'text/', 'application/pdf')):
                handler.send_header('Content-Disposition', f'inline; filename="{filename}"')
            else:
                handler.send_header('Content-Disposition', f'attachment; filename="{filename}"')
            
            handler.end_headers()
            
            with open(file_path, 'rb') as f:
                while chunk := f.read(self.CHUNK_SIZE):
                    try:
                        handler.wfile.write(chunk)
                        handler.wfile.flush()
                    except (ConnectionResetError, BrokenPipeError):
                        print("Client disconnected during transfer")
                        break
                        
        except Exception as e:
            print(f"File serving error: {e}")
           
    @auth.jwt_required            
    def upload(self, handler):
        try:
            content_type = handler.headers['Content-Type']
            
            if 'multipart/form-data' not in content_type:
                raise ValueError("Expected multipart/form-data content type")
            
            content_length = int(handler.headers.get("Content-Length", 0))
            post_data = handler.rfile.read(content_length)
            
            print(f"content type : {content_type}")
            print(f"content length : {content_length}")
    
            boundary = content_type.split("boundary=")[1]
        
            data, filename = self._parsefile(post_data, boundary)
            
            uuid = shortuuid.uuid()
            short_uuid = uuid[:7]
            
            filename = short_uuid+"_"+filename
            
            with open(os.path.join(self.STORAGE_PATH, filename), "wb") as f:
                f.write(data)
                
            handler.send_response(200)
            handler.send_header("Content-Type", "application/json")
            handler.end_headers()
            response = {"success" : f"file {filename} uploaded successfully"}
            handler.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            handler.send_error(400, f"error : {str(e)}")
        
        
    """
    def _parsefile(self, post_data, boundary):
        boundary = boundary.encode('utf-8')
        pattern = re.compile(b'--' + boundary + b'\r\nContent-Disposition: form-data; name="file"; filename="(.*?)"\r\nContent-Type: .*?\r\n\r\n(.*?)\r\n--' + boundary + b'--\r\n', re.DOTALL)
        try:
            match = pattern.search(post_data)
            if not match:
                raise ValueError("Could not parse multipart data")
                
            filename = match.group(1).decode('utf-8')
            file_content = match.group(2)
            
            return file_content, filename
        except Exception as e:
            return e
    """
        
    def _parsefile(self, post_data, boundary):
        try:
            boundary = boundary.encode('utf-8')
            parts = post_data.split(b'--' + boundary)
            
            for part in parts:
                if not part.strip() or part.endswith(b'--\r\n'):
                    continue 
                    
                header_data, _, file_data = part.partition(b'\r\n\r\n')
                headers = header_data.decode('utf-8')
                
                filename_match = re.search(
                    r'filename=(["\'])(.*?)\1', 
                    headers, 
                    re.IGNORECASE
                )
                if filename_match:
                    filename = os.path.basename(filename_match.group(2))
                    return file_data.rstrip(b'\r\n'), filename
                    
            raise ValueError("No file found in multipart data")
            
        except Exception as e:
            raise ValueError(f"Parse failed: {str(e)}") 
                
    