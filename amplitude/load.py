import os
import boto3
import logging
from datetime import datetime
from dotenv import load_dotenv

timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
log_dir = 'logs/load'
os.makedirs(log_dir, exist_ok=True)
log_filename = f'{log_dir}/load_{timestamp}.log'
data_dir='data'

handlers=[
    logging.FileHandler(f"{log_filename}"),  # Saves to file
    logging.StreamHandler()                        # Prints to terminal
]
logging.basicConfig(
    format = '%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=handlers
)

logger = logging.getLogger()

load_dotenv()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_BUCKET_NAME=os.getenv('AWS_BUCKET_NAME')

s3_client=boto3.client(
    's3',
    aws_access_key_id = AWS_ACCESS_KEY,
    aws_secret_access_key = AWS_SECRET_ACCESS_KEY
)

def file_exists_in_s3(s3_path):
    try:
        # head_object only retrieves metadata, making it very fast
        s3_client.head_object(Bucket=AWS_BUCKET_NAME, Key=s3_path)
        return True
    
    except Exception as e:
       
            return False




# file_name = 'python-import/100011471_2026-07-06_0#0.json'

# s3_client.upload_file('data/json_files_20260706T00_to_20260706T23/100011471_2026-07-06_0#0.json',AWS_BUCKET_NAME,file_name)
# print(file_exists_in_s3(file_name))
files_uploaded=0
for root, dirs, files in os.walk(data_dir):
    
    for file in files:
        file_path=os.path.join(root,file)

        if file_exists_in_s3(file_path) == True:
            logger.info(f'{file}: Im already there')

        elif file.endswith('.json'):
            try : 
                file_name = f'python-import/{file}'
                s3_client.upload_file(file_path,AWS_BUCKET_NAME,file_name)
                logger.info(f'{file} uploaded to S3')
                files_uploaded += 1
                #os.remove(file_path)
                #logger.info(f'{file} removed from local storage')
            except Exception as e:
                logger.error(f' we are cooked {file} failed to upload to S3')
    
logger.info(f'{files_uploaded} files uploaded')
