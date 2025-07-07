import requests
import threading
import time 

def download_file(url, name):
    response = requests.get(url)
    print(f"{name} : {response.status_code}\n")

url1 = "http://localhost:8000/api/files/DhhTr8M_ayush.pdf"
url2 = "http://localhost:8000/api/files/mdl.jpg"

i = 1
threads = []

start = time.time()

while i<=100:
    
    threads.append(threading.Thread(target=download_file, args=(url1, f"{i}")))
    i+=1

for thread in threads:
    thread.start()
    
for thread in threads:
    thread.join()

end = time.time()

print(f"total time : {end-start}")