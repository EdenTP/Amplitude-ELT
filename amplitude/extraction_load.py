from modules.extract_function import amplitude_extract
import os
from dotenv import load_dotenv


load_dotenv()
# Read .env file
api_key = os.getenv('AMP_API_KEY')
secret_key = os.getenv('AMP_SECRET_KEY')


start_dttime_str = '20260706T00'
end_dttime_str = '20260710T23'

amplitude_extract(start_dttime_str, end_dttime_str, api_key,secret_key)
