from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import re
import os
from dotenv import load_dotenv
import shortuuid    
import mimetypes


load_dotenv()

STORAGE_PATH = os.getenv('STORAGE_PATH')
PORT = int(os.getenv('PORT'))

print(f"this is storage path : {STORAGE_PATH}")


class SimpleAPIHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        if self.path in ["/api/hello", "/api/hello/"]:
            self.hello()
        elif self.path in ["/api/files", "/api/files/"]:
            self.files()
        elif re.match(r'^/api/files/[\w]+\.[\w]+$', self.path):
            file_id = self.path.split("/")[-1]
            self.file_by_id(file_id)  
        else:
            self.send_error(404, "something Not Found")
            
    def files(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        
        dirs = os.listdir(STORAGE_PATH)

        response = {"Files":f"{dirs}"}
        self.wfile.write(json.dumps(response).encode())
        
        
    def file_by_id(self, file_id):
        file_path = os.path.join(STORAGE_PATH, file_id)
        
        print(f"File path : {file_path}")
        
        if not os.path.exists(file_path):
            self.send_error(404, f"file {file_id} not found")
        
        user_agent = self.headers.get('User-Agent', '').lower()
        is_terminal = 'curl' in user_agent
        
        if is_terminal:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {
                "preview_link": f"http://localhost:8000/api/files/{file_id}",
                "download_link": f"http://localhost:8000/api/files/{file_id}?download=true"
            }
            self.wfile.write(json.dumps(response).encode()) 
              
        else: 
            print("accessing from browser")
            preview = "download" not in self.headers.get("Accept", " ").lower()
            
            self._serve_file(file_path, preview)
            
        
    def _serve_file(self, file_path, preview=True):
        mime_type, encoding = mimetypes.guess_type(file_path)
        
        if not mime_type:
            mime_type = "application/octet-stream"
            
        with open(file_path, "rb") as f:
            file_data = f.read()
        
        self.send_response(200)
        self.send_header("Content-Type", mime_type)
        self.send_header("Content-Length", str(len(file_data)))
      
        if mime_type.startswith(('image/', 'text/', 'application/pdf')):
            filename = os.path.basename(file_path)
            self.send_header("Content-Disposition", f"inline; filename=\"{filename}\"")
        else:
            filename = os.path.basename(file_path)
            self.send_header("Content-Disposition", f"attachment; filename=\"{filename}\"")            
        
        self.end_headers()
        self.wfile.write(file_data)
            
        
    def do_POST(self):
          
        if self.path in ["/api/upload", "/api/upload/"]:
            self.upload()
        else:
            self.send_error(404, "Not Found")
            

    def upload(self):
        content_type = self.headers['Content-Type']
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        
        boundary = content_type.split("boundary=")[1]
        
        try:  
            data, filename = self._parsefile(post_data, boundary)
            
            uuid = shortuuid.uuid()
            short_uuid = uuid[:7]
            
            filename = short_uuid+"_"+filename
            
            with open(os.path.join(STORAGE_PATH, filename), "wb") as f:
                f.write(data)
                
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"success" : f"file {filename} uploaded successfully"}
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_error(400, f"error parsing file : {str(e)}")
        
        
    
    def _parsefile(self, post_data, boundary):
        boundary = boundary.encode('utf-8')
        pattern = re.compile(b'--' + boundary + b'\r\nContent-Disposition: form-data; name="file"; filename="(.*?)"\r\nContent-Type: .*?\r\n\r\n(.*?)\r\n--' + boundary + b'--\r\n', re.DOTALL)
        
        match = pattern.search(post_data)
        if not match:
            raise ValueError("Could not parse multipart data")
            
        filename = match.group(1).decode('utf-8')
        file_content = match.group(2)
        
        return file_content, filename
            
                
            
        
if __name__ == "__main__":
    mimetypes.init()
    
    mimetypes.add_type("application/wasm", ".wasm")
    
    server = HTTPServer(("localhost", PORT), SimpleAPIHandler)
    print(f"Server running at http://localhost:{PORT}")
    server.serve_forever()