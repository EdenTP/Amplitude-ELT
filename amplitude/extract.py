import requests
from datetime import datetime, timedelta
import os
import json
import logging
import time
import zipfile
from dotenv import load_dotenv
import gzip
import shutil

# Load .env file
load_dotenv()

# Read .env file
api_key = os.getenv('AMP_API_KEY')
secret_key = os.getenv('AMP_SECRET_KEY')

starttime_str = '20260706T00'
endtime_str = datetime.now().strftime('%Y%m%dT%H') 

start_dt = datetime.strptime(starttime_str, '%Y%m%dT%H')
end_dt = datetime.strptime(endtime_str, '%Y%m%dT%H')

daily_chunks = []
current_start = start_dt

while current_start <= end_dt:
    # Set the end of the current chunk to 23:00 of that same day
    end_of_day = current_start.replace(hour=23)
    
    # If the end of the day overshoots our final endtime, clamp it to the final endtime
    current_end = min(end_of_day, end_dt)
    
    # Store the chunk as a tuple of formatted strings
    daily_chunks.append((
        current_start.strftime('%Y%m%dT%H'),
        current_end.strftime('%Y%m%dT%H')
    ))
    
    # Step forward to 00:00 of the next day
    current_start = end_of_day + timedelta(hours=1)

timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)
log_filename = f'{log_dir}/{timestamp}.log'

logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger()
logger.info('Logger has lift off')
os.makedirs('data', exist_ok=True)
data_dir = 'data'

url = 'https://analytics.eu.amplitude.com/api/2/export'


delay = 10
max_retry = 5
for i in range(len(daily_chunks)):
    attempt = 0

    starttime, endtime = daily_chunks[i]
    logger.info(f'Attempting to retrieve data for chunk {starttime} to {endtime}')
    print(f'Attempting to retrieve data for chunk {starttime} to {endtime}')
    while attempt < max_retry:
        params = {
        'start': starttime,
        'end': endtime
    }
        logger.info(f'Attempting to retrieve data from Amplitude API, attempt number {attempt + 1}')
        response = requests.get(url, params=params, auth=(api_key, secret_key))
        status=response.status_code
        if status == 200:
            data = response.content
            logger.info('Data retrieved successfully.')
            print('Data retrieved successfully.')
            
            # 1. Save the zip file
            zip_filepath = os.path.join(data_dir, 'data.zip')
            with open(zip_filepath, 'wb') as file:
                file.write(data)
            
            # 2. Extract the zip file
            extract_dir = os.path.join(data_dir, f'extracted_{starttime}_to_{endtime}')
            os.makedirs(extract_dir, exist_ok=True)
            
            # Define and create the directory for your final JSON files
            JSON_dir = os.path.join(data_dir, f'json_files_{starttime}_to_{endtime}')
            os.makedirs(JSON_dir, exist_ok=True)
            
            print('Extracting files...')
            with zipfile.ZipFile(zip_filepath, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
                
            print(f'Files successfully extracted to {extract_dir}')
            
            # 3. Find, decompress, and save all .gz files as .json
            gz_file_count=0
            json_file_count=0
            failed_files=[]
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    
                    if file.endswith('.gz'):
                        gz_path = os.path.join(root, file)
                        gz_file_count += 1
                        # Remove '.gz' from the filename
                        new_filename = file.replace('.gz', '')
                        json_path = os.path.join(JSON_dir, new_filename)
                        
                        print(f'Decompressing to: {json_path}')
                        
                        with gzip.open(gz_path, 'rb') as f_in:
                            with open(json_path, 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                                json_file_count += 1

                        
                        # --- VERIFICATION & CLEANUP ---
                        # Check if the JSON file exists and actually contains data (>0 bytes)
                        if os.path.exists(json_path) and os.path.getsize(json_path) > 0:
                            logger.info(f'Verified {new_filename}. Deleting original .gz file.')
                            os.remove(gz_path) # Delete the individual .gz file
                        else:
                            print(f'WARNING: {new_filename} failed extraction or is empty.')
                            logger.error(f'Failed extraction for {new_filename}.')
                            failed_files.append(gz_path)

            if gz_file_count>json_file_count:
                print(f'Extraction fail for {gz_file_count-json_file_count} files :{failed_files}')
                logger.error(f'Extraction fail for {gz_file_count-json_file_count} files :{failed_files}')          
            
            
            # 4. Final Cleanup
            print('Cleaning up temporary files...')
            logger.info('Cleaning up temporary files...')
            # Delete the original downloaded zip file
            if os.path.exists(zip_filepath):
                os.remove(zip_filepath)
                logger.info(f'Deleted temporary zip file: {zip_filepath}')
                
            # Delete the intermediate extraction folder (which is now empty of .gz files)
            if os.path.exists(extract_dir):
                shutil.rmtree(extract_dir)
                logger.info(f'Deleted temporary extraction directory: {extract_dir}')
                
            print(f'Cleanup complete. Your {starttime} to {endtime} data is ready in: {JSON_dir}')
            logger.info(f'Cleanup complete. Your {starttime} to {endtime} data is ready in: {JSON_dir}')
            break
        elif status <= 100 or status>=500:
            attempt=attempt+1
            print(f'Sus status({status}) waiting to try again, attempt number {attempt+1}')
            logger.info(f'Sus status({status}) waiting to try again, attempt number {attempt+1}')
            time.sleep(delay)
        else : 
            logger.info(f'PANIK! status code {status} on attempt {attempt+1}')
            break
print(f'Pipeline complete! All daily chunks from {starttime_str} to {endtime_str} have been extracted.')
logger.info('Pipeline complete! All chunks processed successfully.')