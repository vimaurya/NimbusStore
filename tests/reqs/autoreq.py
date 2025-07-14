import requests


class req:
    def __init__(self):        
        self.header = {
            'Host' : 'https://localhost:8000',
            'Content-Type' : 'application/json',
            'Accept'    : 'application/json'
        }

        self.url = 'https://localhost:8000'
    
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
            
            print(response.text)
            
        except Exception as e:
            print(str(e))
        
        
    def get_files(self, endpoint='/api/files')->None:
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
        
        


if __name__ == "__main__":
        
    request_obj = req()

    #func = input("Enter what function to call : ")

    func = "signup"
    
    if hasattr(request_obj, func):
        method = getattr(request_obj, func)
        method()
    else:
        print("this function does not exist...")