from socketserver import ThreadingMixIn
from http.server import BaseHTTPRequestHandler, HTTPServer
import re
import os
from dotenv import load_dotenv  
import mimetypes
from utility import util_funcs
import certnkey
import ssl


load_dotenv()

STORAGE_PATH = os.getenv('STORAGE_PATH')
SSL_PATH = os.getenv('SSL_PATH')
PORT = int(os.getenv('PORT'))

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

class SimpleAPIHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.utils = util_funcs(STORAGE_PATH=STORAGE_PATH)
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        
        self.paths = [
            "/api/files",
            "/api/files/"
        ]
        
        print(f"\n{self.headers}")
            
        if self.path in self.paths:
            self.utils.files(self)
            
        elif re.match(r'/api/files/[\w-]+\.[\w]+(\?download=true)?$', self.path):
            file_id = self.path.split("/")[-1]
            
            if '?' in file_id:
                file_id = file_id.split("?")[0]
                
            self.utils.file_by_id(self, file_id)  
            
        else:
            self.send_error(404, "endpoint not found")
                    
        
    def do_POST(self):
        paths = [
            "/api/upload",
            "/api/upload/",
            "/api/signup/",
            "/api/signup"
        ]
        
        if self.path in paths:
            self.utils.upload(self)
        else:
            self.send_error(404, "Not Found")
            

            
        
if __name__ == "__main__":
    mimetypes.init()
    
    mimetypes.add_type("application/wasm", ".wasm")
    
    server = ThreadedHTTPServer(("localhost", PORT), SimpleAPIHandler)
    
    sslcontext = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    
    sslcontext.load_cert_chain(SSL_PATH+'/cert.pem', SSL_PATH+'/key.pem')
    
    server.socket = sslcontext.wrap_socket(server.socket, server_side=True)
    
    print(f"Server running at https://localhost:{PORT}")
    
    server.serve_forever()