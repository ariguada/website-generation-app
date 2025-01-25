import json
import boto3
import os
import time

# Initialize SQS client
sqs = boto3.client('sqs')
queue_url = os.getenv('SQS_QUEUE_URL')

def lambda_handler(event, context):
    try:
        for _ in range(5):  # Maximum of 5 iterations
            # Poll SQS for messages
            response = sqs.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=1,  # Fetch up to 1 message at a time
                WaitTimeSeconds=3
            )

            if 'Messages' in response:
                # Process the first message from the SQS queue
                message = response['Messages'][0]
                print('Received message:', message['Body'])

                # Process the message (e.g., parsing, modifying, etc.)
                processed_message = json.loads(message['Body'])  # Ensure the message is in JSON format

                # Delete the message from the queue after processing
                sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=message['ReceiptHandle']
                )

                # Return the processed data to API Gateway, directly sending the link
                return {
                    'statusCode': 200,
                    'body': json.dumps({'link': processed_message['link']})  # Return the link as a direct value
                }

            # Wait for 2 seconds before the next iteration if no message is found
            time.sleep(2)

        # If no message is received after 5 attempts
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'No messages available after 5 attempts'})
        }

    except Exception as e:
        print('Error:', str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal Server Error', 'error': str(e)})
        }
