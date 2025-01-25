import requests
import json
import os

def lambda_handler(event, context):
    # Extract bucket and file key from the S3 event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']
    
    # CloudConvert & AWS user API details
    API_URL = "https://api.cloudconvert.com/v2/jobs"
    API_KEY = os.getenv('CLOUDCONVERT_API_KEY')
    ACCESS_KEY_ID = os.getenv('ACCESS_KEY_ID')
    SECRET_ACCESS_KEY = os.getenv('SECRET_ACCESS_KEY')

    # CloudConvert Job payload
    payload = {
        "tasks": {
            "import-1": {
                "operation": "import/s3",
                "bucket": bucket_name,
                "region": "us-west-1",
                "access_key_id": ACCESS_KEY_ID,
                "secret_access_key": SECRET_ACCESS_KEY,
                "key": file_key
            },
            "task-1": {
                "operation": "convert",
                "input_format": "pdf",
                "output_format": "html",
                "engine": "pdf2htmlex",
                "input": ["import-1"],
                "outline": False,
                "zoom": 1.5,
                "embed_css": True,
                "embed_javascript": True,
                "embed_images": True,
                "embed_fonts": True,
                "split_pages": False,
                "bg_format": "png",
                "engine_version": "0.18.8-20240611",
                "filename": "index.html"
            },
            "export-1": {
                "operation": "export/s3",
                "input": ["task-1"],
                "bucket": bucket_name,
                "region": "us-west-1",
                "access_key_id": ACCESS_KEY_ID,
                "secret_access_key": SECRET_ACCESS_KEY
            }
        },
        "tag": "jobbuilder"
    }

    # Create job on CloudConvert
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()
        
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Job created successfully!", "details": result})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Failed to create job", "error": str(e)})
        }
