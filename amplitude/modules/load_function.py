import os
import boto3
import logging

logger=logging.getLogger(__name__)

def amplitude_load(aws_access_key,aws_secret_access_key,aws_bucket_name):
    """
        Load amplitude data to S3.

        Args:
            aws_access_key (str): The AWS access key for authenticating with S3.
            aws_secret_access_key (str): The AWS secret access key for authenticating with S3
            aws_bucket_name (str): The name of the S3 bucket where the data will be loaded.

        Returns:
            None, but uploads the extracted data to the specified S3 bucket.
        """
    
    data_dir='data'
    
    s3_client=boto3.client(
        's3',
        aws_access_key_id = aws_access_key,
        aws_secret_access_key = aws_secret_access_key
    )

    def file_exists_in_s3(s3_path):
        try:
            # head_object only retrieves metadata, making it very fast
            s3_client.head_object(Bucket=aws_bucket_name, Key=s3_path)
            return True
        
        except Exception as e:
        
                return False
        

    files_uploaded=0
    for root, dirs, files in os.walk(data_dir):
        
        for file in files:
            file_path=os.path.join(root,file)
            s3_path=f'python-import/{file}'
            if file_exists_in_s3(s3_path) == True:
                logger.info(f'{file}: Im already there')

            elif file.endswith('.json'):
                try : 
                    file_name = f'python-import/{file}'
                    s3_client.upload_file(file_path,aws_bucket_name,file_name)
                    logger.info(f'{file} uploaded to S3')
                    files_uploaded += 1
                    #os.remove(file_path)
                    #logger.info(f'{file} removed from local storage')
                except Exception as e:
                    logger.error(f' we are cooked {file} failed to upload to S3')
        
    logger.info(f'{files_uploaded} files uploaded')

    return None
