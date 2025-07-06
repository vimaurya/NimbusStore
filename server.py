from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import re
import os


STORAGE_PATH = "C:/Users/Vikash maurya/backendproject/apis/API cloud storage/Storage"

class SimpleAPIHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        if self.path in ["/api/hello", "/api/hello/"]:
            self.hello()
        elif self.path in ["/api/files", "/api/files/"]:
            self.files()
            
        elif re.match(r'^/api/files/[\w]+$', self.path):
            file_id = self.path.split("/")[-1]
            self.file_by_id(file_id)
            
        else:
            self.send_error(404, "Not Found")
            
    def files(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        
        dirs = os.listdir(STORAGE_PATH)

        response = {"Files":f"{dirs}"}
        self.wfile.write(json.dumps(response).encode())
        
        
    def file_by_id(self, id):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        response = {"Files" : f"searching file id : {id}"}
        self.wfile.write(json.dumps(response).encode())
        
        
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
            
            
            with open(os.path.join("./storage",filename), "wb") as f:
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
    server = HTTPServer(("localhost", 8000), SimpleAPIHandler)
    print("Server running at http://localhost:8000")
    server.serve_forever()