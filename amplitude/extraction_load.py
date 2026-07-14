from modules.extract_function import amplitude_extract
from modules.load_function import amplitude_load
import os
from dotenv import load_dotenv


load_dotenv()
# Read .env file
api_key = os.getenv('AMP_API_KEY')
secret_key = os.getenv('AMP_SECRET_KEY')
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_BUCKET_NAME=os.getenv('AWS_BUCKET_NAME')


start_dttime_str = '20260706T00'
end_dttime_str = '20260710T23'

amplitude_extract(start_dttime_str, end_dttime_str, api_key,secret_key)
amplitude_load(AWS_ACCESS_KEY,AWS_SECRET_ACCESS_KEY,AWS_BUCKET_NAME)
