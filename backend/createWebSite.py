import boto3
import json
import random
import string
import logging
import os

# Initialize clients
s3_client = boto3.client('s3')
sqs_client = boto3.client('sqs')

# Set up the SQS queue URL (update with your actual SQS Queue URL)
sqs_queue_url = os.getenv('SQS_QUEUE_URL')

# Configure logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Set the log level to INFO

def send_log_to_sqs(log_message):
    try:
        # Send log message to SQS
        response = sqs_client.send_message(
            QueueUrl=sqs_queue_url,
            MessageBody=json.dumps(log_message)  # Send as a JSON string
        )
        logger.info(f"Sent log message to SQS with MessageId: {response['MessageId']}")
    except Exception as e:
        logger.error(f"Error sending log message to SQS: {e}")

def lambda_handler(event, context):
    try:
        # Extract source bucket and file details from the event
        source_bucket = event['Records'][0]['s3']['bucket']['name']
        file_key = event['Records'][0]['s3']['object']['key']

        if file_key != 'index.html':
            error_message = f"Uploaded file is not index.html: {file_key}"
            logger.error(error_message)
            return {
                'statusCode': 400,
                'body': 'Uploaded file is not index.html. No action taken.'
            }
        
        # Generate a random name for the new website bucket
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        new_bucket_name = f"my-cv-{random_suffix}"
        
        # Create a new S3 bucket
        s3_client.create_bucket(
            Bucket=new_bucket_name,
            CreateBucketConfiguration={'LocationConstraint': 'us-west-1'}  # Adjust region if needed
        )
        
        # Enable static website hosting
        s3_client.put_bucket_website(
            Bucket=new_bucket_name,
            WebsiteConfiguration={
                'IndexDocument': {'Suffix': 'index.html'},
            }
        )
        
        # Move the index.html file to the new bucket
        s3_client.copy_object(
            CopySource={'Bucket': source_bucket, 'Key': file_key},
            Bucket=new_bucket_name,
            Key='index.html',
            ContentType='text/html'
        )

        # Delete the index.html file from the source bucket
        s3_client.delete_object(
            Bucket=source_bucket,
            Key=file_key
        )
        
        # Construct the website URL
        website_url = f"http://{new_bucket_name}.s3-website-us-west-1.amazonaws.com"
        
        # Send only the final success message to SQS
        log_message = {"link": website_url}  # Send the link in the required format
        send_log_to_sqs(log_message)
        
        # Add bucket policy for public access
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{new_bucket_name}/*"
                }
            ]
        }

        # Disable "Block all public access"
        try:
            s3_client.put_public_access_block(
                Bucket=new_bucket_name,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': False,
                    'IgnorePublicAcls': False,
                    'BlockPublicPolicy': False,
                    'RestrictPublicBuckets': False
                }
            )
        except Exception as e:
            error_message = f"Failed to disable block public access for {new_bucket_name}: {e}"
            logger.error(error_message)
            raise

        # Apply the policy to the bucket
        try:
            s3_client.put_bucket_policy(
                Bucket=new_bucket_name,
                Policy=json.dumps(bucket_policy)
            )
        except Exception as e:
            error_message = f"Failed to apply bucket policy to {new_bucket_name}: {e}"
            logger.error(error_message)
            raise

        return {
            'statusCode': 200,
            'body': f"Static website created successfully: {website_url}"
        }
    
    except Exception as e:
        error_message = f"Error in Lambda execution: {e}"
        logger.error(error_message, exc_info=True)
        return {
            'statusCode': 500,
            'body': f"An error occurred: {str(e)}"
        }
