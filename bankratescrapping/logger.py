# bankratescrapping/logger.py

import logging
from datetime import datetime, timedelta
import os

# Setup log directory
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Cleanup logs older than 15 days
def clean_old_logs(directory, days=15):
    now = datetime.now()
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            if now - file_mtime > timedelta(days=days):
                os.remove(file_path)

clean_old_logs(log_dir, days=15)

# Set log file path
log_file_path = os.path.join(log_dir, "scrapy_log.log")

# Disable root logger and all handlers
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(handlers=[], level=logging.CRITICAL + 1)

# Set up custom logger
logger = logging.getLogger("custom_logger")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(log_file_path, mode='a')
formatter = logging.Formatter('%(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
