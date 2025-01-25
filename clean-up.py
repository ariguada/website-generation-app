import boto3
import os

# Create an S3 client
s3 = boto3.client('s3')

# List all buckets
response = s3.list_buckets()

# Filter out buckets that start with "my-cv-"
buckets_to_delete = [bucket['Name'] for bucket in response['Buckets'] if bucket['Name'].startswith('my-cv-')]

# Name of the bucket to be emptied (convertion-service-bucket)
bucket_to_empty = "conversion-service-bucket"

# Empty the convertion-service-bucket
try:
    print(f"Emptying bucket: {bucket_to_empty}")
    
    # List all objects in the convertion-service-bucket
    objects = s3.list_objects_v2(Bucket=bucket_to_empty)
    if 'Contents' in objects:
        for obj in objects['Contents']:
            s3.delete_object(Bucket=bucket_to_empty, Key=obj['Key'])
    
    print(f"Bucket {bucket_to_empty} emptied successfully.")

except Exception as e:
    print(f"Error emptying bucket {bucket_to_empty}: {str(e)}")

# Iterate over each bucket starting with "my-cv-" and empty it, then delete it
for bucket_name in buckets_to_delete:
    try:
        print(f"Emptying and deleting bucket: {bucket_name}")
        
        # Empty the bucket (delete all objects inside)
        objects = s3.list_objects_v2(Bucket=bucket_name)
        if 'Contents' in objects:
            for obj in objects['Contents']:
                s3.delete_object(Bucket=bucket_name, Key=obj['Key'])
        
        # After emptying, delete the bucket itself
        s3.delete_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} deleted successfully.")
    
    except Exception as e:
        print(f"Error deleting bucket {bucket_name}: {str(e)}")

## Uncomment next section if you need your frontend files to be uploaded.

#file_paths = [
#  '/mnt/c/Users/user/Desktop/frontend/conversion-frontend.js',
#  '/mnt/c/Users/user/Desktop/frontend/conversion-frontend.html'
#]

#for file_path in file_paths:
#    file_name = os.path.basename(file_path)
    
#    try:
#        # Open and upload the file
#        with open(file_path, 'rb') as file_data:
#            print(f"Uploading file {file_name} to {bucket_to_empty}...")
#            s3.upload_fileobj(file_data, bucket_to_empty, file_name)
#            print(f"File {file_name} uploaded successfully.")
#
#    except Exception as e:
#        print(f"Error uploading file {file_name}: {str(e)}")
