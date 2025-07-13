import requests


class req:
    def __init__(self):        
        self.header = {
            'Host' : 'https://localhost:8000',
            'Content-Type' : 'application/json',
            'Accept'    : 'application/json'
        }

        self.url = 'https://localhost:8000'
        
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

    func = input("Enter what function to call : ")

    if hasattr(request_obj, func):
        method = getattr(request_obj, func)
        method()
    else:
        print("this function does not exist...")