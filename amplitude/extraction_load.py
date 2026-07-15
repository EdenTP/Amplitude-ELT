from modules.extract_function import amplitude_extract
from modules.load_function import amplitude_load
import os
from dotenv import load_dotenv
from modules.log_function import log_config
from datetime import datetime

timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
log_dir = 'logs'

logger=log_config(timestamp,log_dir)
logger.info('Logger has lift off')
load_dotenv()
# Read .env file
api_key = os.getenv('AMP_API_KEY')
secret_key = os.getenv('AMP_SECRET_KEY')
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_BUCKET_NAME=os.getenv('AWS_BUCKET_NAME')


start_dttime_str = '20260710T00'
end_dttime_str = '20260714T05'

amplitude_extract(start_dttime_str, end_dttime_str, api_key,secret_key)
amplitude_load(AWS_ACCESS_KEY,AWS_SECRET_ACCESS_KEY,AWS_BUCKET_NAME)
