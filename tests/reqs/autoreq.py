import requests
import os
from pathlib import Path
import uuid
from requests_toolbelt.multipart.encoder import MultipartEncoder

class req:
    def __init__(self):  
        self.jwt = ""      
        self.header = {
            'Host' : 'https://localhost:8000',
            'Content-Type' : 'application/json',
            'Accept'    : 'application/json',
            'Authorization' : f'Bearer {self.jwt}',
            'Session-ID' : None
        }

        self.url = 'https://localhost:8000'
        
    def login(self, endpoint='/api/login')->None:
        self.url = self.url + endpoint
        
        while True:
            user_id = input("Enter user_id : ")
            password = input("Enter password : ")
            #conf_password = input("Confirm password : ")
            
            conf_password = password
            
            if password==conf_password:
                break
            
            print("passwords do not match...\n")
            
        payload = {
            'user_id' : user_id,
            'password' : password
        } 
        try:   
            response = requests.post(
                self.url, 
                json=payload,
                headers=self.header, 
                verify=False
            ) 
            response.raise_for_status()
            
            response = response.json()
            
            self.jwt = response['jwt']
            
            self.session_id = response['session_id']
        
            print(f"This is session id : {self.session_id}")
            
            self.header['Authorization'] = f'Bearer {self.jwt}'
            
            self.header['Session-ID'] = self.session_id
            
            print(response)
            
        except Exception as e:
            print(str(e))
        
    
    def signup(self, endpoint='/api/signup')->None:
        self.url = self.url + endpoint
        
        while True:
            user_id = input("Enter user_id : ")
            password = input("Enter password : ")
            #conf_password = input("Confirm password : ")
            
            conf_password = password
            
            if password==conf_password:
                break
            
            print("passwords do not match...\n")
            
        payload = {
            'user_id' : user_id,
            'password' : password
        } 
        try:   
            response = requests.post(
                self.url, 
                json=payload,
                headers=self.header, 
                verify=False
            ) 
            response.raise_for_status()
            
            response = response.json()
            
            self.jwt = response['jwt']
            
            self.session_id = response['session_id']
        
            print(f"This is session id : {self.session_id}")
            
            self.header['Authorization'] = f'Bearer {self.jwt}'
            
            self.header['Session-ID'] = self.session_id
            
            print(response)
            
        except Exception as e:
            print(str(e))
        
        
    def get_files(self, endpoint='/api/files')->None:
        
        print(f"this is header : \n{self.header}")
            
        self.url = self.url+endpoint
        response = requests.get(self.url, headers=self.header, verify=False)
        response.encoding = 'utf-8'
        print(response.text)
        
        
    def get_file_by_id(self, endpoint="/api/files/")->None:
        file_id = input("Enter the file_id you want : ")
        self.url = self.url + endpoint + file_id
        if file_id==" ":
            print("file_id can not be empty...")
        else:
            response = requests.get(self.url, headers=self.header, verify=False)
            response.encoding = 'utf-8'
            print(response.text)
        
        
    def upload(self, endpoint="/api/upload/", f_path : Path = None)->None:
        self.url = self.url + endpoint
        
        if not f_path:
            f_path = Path(input("Enter the path : ").strip())
        
        try:        
            if f_path.is_file():
                with open(f_path, "rb") as f:
                    boundary = uuid.uuid4().hex
                    
                    fields = {
                        "file": (f_path.name, f),
                        "filename" : f_path.name, 
                    }
                    
                    mp_encoder = MultipartEncoder(
                        fields = fields,
                        boundary = boundary
                    )
                    headers = {
                        **self.header,
                        'Content-Type' : f'multipart/form-data; boundary={boundary}',
                        'X-Upload-Source' : 'Python Client'
                    }
                    
                    response = requests.post(
                        self.url, 
                        headers=headers,
                        data=mp_encoder,
                        verify=False,
                        timeout=(10, 30)
                    )
                    
                    response.encoding = 'utf-8'
                    print(response.text)
                    
            elif f_path.is_dir():
                contents = os.listdir(f_path)
                for item in contents:
                    self.upload(f_path = item)
            else:
                print("this path does not exist...")
                    
        except Exception as e:
            raise RuntimeError(e)
    
    def print_header(self):
        print(f"this is header : \n {self.header}")
    
                

if __name__ == "__main__":
    
    request_obj = req()

    while True:
        
        request_obj.url = 'https://localhost:8000'
        
        func = input("Enter what function to call : ")

        #func = "signup"
        
        if hasattr(request_obj, func):
            method = getattr(request_obj, func)
            method()
        else:
            print("this function does not exist...")
            print("-"*5)