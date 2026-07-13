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

start_dttime_str = '20260706T00'
end_dttime_str = datetime.now().strftime('%Y%m%dT%H') 

start_dt = datetime.strptime(start_dttime_str, '%Y%m%dT%H')
end_dt = datetime.strptime(end_dttime_str, '%Y%m%dT%H')

daily_chunks = []
current_start = start_dt

#While loop to create array of time arguments
while current_start <= end_dt:
    # Default end of day is hour 23
    end_of_day = current_start.replace(hour=23)
    
    # If the end of the day is bigger than the set end date time, select the less of the 2
    current_end = min(end_of_day, end_dt) 
    
    # Storing the daily chunks as in string format needed for API an array of 2s
    daily_chunks.append((
        current_start.strftime('%Y%m%dT%H'),
        current_end.strftime('%Y%m%dT%H')
    ))
    
    # Step forward to 00:00 of the next day
    current_start = end_of_day + timedelta(hours=1)


#Logging set up
timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
log_dir = 'logs\extract'
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


#Lets start extracting(set up)
url = 'https://analytics.eu.amplitude.com/api/2/export'

# Setting retry parameters
delay = 10
max_retry = 5

#we query the API for each day individually
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
                file.write(data) #this saves the zip as data.zip
            
            # 2. Extract the zip file, define zip directory and create it
            extract_dir = os.path.join(data_dir, f'extracted_{starttime}_to_{endtime}')
            os.makedirs(extract_dir, exist_ok=True)
            
            # Define and create the directory for your final JSON files, define json directory and create it
            JSON_dir = os.path.join(data_dir, f'json_files_{starttime}_to_{endtime}')
            os.makedirs(JSON_dir, exist_ok=True)
            
            #print and log current status
            print('Extracting files...')
            logger.info('Extracting files...')
            #using zip module to extract, 'r' argument is for reading
            with zipfile.ZipFile(zip_filepath, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
                
            print(f'Files successfully extracted to {extract_dir}')
            logger.info(f'Files successfully extracted to {extract_dir}')

            #This is where the fun begins
            # 3. Find, decompress, and save all .gz files as .json
            #file counts made for gz to json checks down the line
            gz_file_count=0
            json_file_count=0
            failed_files=[] #We're going to check for failed files, so we create an empty array

            #this is a loop that walks through each folder and file found under extract_dir
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    
                    if file.endswith('.gz'):
                        gz_path = os.path.join(root, file)
                        gz_file_count += 1
                        # Remove '.gz' from the filename
                        new_filename = file.replace('.gz', '')
                        #create a json file_path(os.path.join) makes filepaths so you don't have to figure out operating system filepath syntax
                        json_path = os.path.join(JSON_dir, new_filename)
                        
                        print(f'Decompressing to: {json_path}')
                        logger.info(f'Decompressing to: {json_path}')

                        #gzip deals with GZIPS, here we open the gzip then we open the json file and copy the contents of the gzip to the json file.
                        with gzip.open(gz_path, 'rb') as f_in:
                            with open(json_path, 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                                json_file_count += 1

                        
                        # --- VERIFICATION & CLEANUP ---
                        # Check if the JSON file exists and actually contains data (>0)
                        if os.path.exists(json_path) and os.path.getsize(json_path) > 0:
                            logger.info(f'Verified {new_filename}. Deleting original {file}')
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

            #Do I want to check we have succesfulyl got all expected jsons before deleting the zip, if gz_count doesnt match json, do I wanna just run it all again? 
            if os.path.exists(zip_filepath):
                os.remove(zip_filepath)
                logger.info(f'Deleted temporary zip file: {zip_filepath}')
                
            # Delete the intermediate extraction folder, could be more robust check if empty first, did all .gz get extracted
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
print(f'Pipeline complete! All daily chunks from {start_dttime_str} to {end_dttime_str} have been extracted.')
logger.info('Pipeline complete! All chunks processed successfully.')