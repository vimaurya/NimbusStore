import os
import logging
import datetime

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

date = datetime.datetime.now().strftime("%d-%m-%Y")


file_name = f'{date}_cloud_storage.log'



logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename = os.path.join(log_dir, file_name),
    filemode='a'
)