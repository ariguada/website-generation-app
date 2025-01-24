## Step 1: Upload PDF to S3 via Frontend

This step provides a simple frontend that allows users to upload PDF files to the S3 bucket `conversion-service-bucket`. The interface is hosted on the same bucket and built with an HTML file and a JavaScript file.

HTML file upload is also enabled for testing purposes.

### Frontend files (located in /frontend)
- **`conversion-frontend.html`**: Provides a file input, an upload button, and a status message area for user interaction.
- **`conversion-frontend.js`**: Handles the file upload directly to S3 using a PUT request.

The S3 bucket name, region, and access credentials are **temporarily hardcoded for simplicity**. I will use Cognito and Pre-signed URL in next update of this project. The files are uploaded directly to S3 with basic error handling and status updates displayed to the user.

### Permissions:
1.  JavaScript file needs permission to PUT files into S3. I have created a user that has this permission and hardcoded access to this user API in the JS code. Make sure you **don't do that for production**, as whole JS code will be visible to whole world, including hardcoded credentials.
2.  S3 needs **Bucket policy** to Allow anyone to make GET request: "Principal": "*", Action": "s3:GetObject".
3.  S3 needs **Cross-origin resource sharing** (CORS) to allow all origins

--- 
## Step 2: Trigger CloudConvert Job via Lambda

If PDF file was uploaded uploaded to the S3 bucket, it triggers the **TriggerCloudConvertJob** Lambda function. This function creates a job on CloudConvert to convert the PDF file to HTML and saves the resulting HTML file back to the same S3 bucket.

### Lambda Function Details

The Lambda function performs the following tasks:
1. **Extracts the S3 bucket and file key** from the event triggered by the upload.
2. **Creates a job on CloudConvert** using its REST API to convert the PDF to HTML. The job includes:
   - Importing the PDF file from the S3 bucket.
   - Converting the PDF to HTML with specified parameters.
   - Exporting the resulting HTML back to the same S3 bucket.
3. The function uses AWS credentials (access key and secret access key) and CloudConvert API key stored as environment variables.

The Lambda function is triggered by the S3 event for `.pdf` file uploads. It uses the `requests` library to communicate with the CloudConvert API, which is included as a Lambda layer.

**Environment Variables**:
- `CLOUDCONVERT_API_KEY`: CloudConvert API key.
- `ACCESS_KEY_ID`: AWS access key ID.
- `SECRET_ACCESS_KEY`: AWS secret access key.

### Permissions:
1. **`TriggerCloudConvertJob`** Lambda needs **s3:GetObject** and **s3:PutObject** permissions to `conversion-service-bucket`.

--- 
## Step 3: Create Static Website via Lambda

When the HTML file (`index.html`) is uploaded to the `convertion-service-bucket`, it triggers the **createWebSite** Lambda function. This function creates a new S3 bucket, moves the `index.html` file from the original bucket to the new one, and enables static website hosting for the new bucket. The function also sets the necessary permissions to make the website publicly accessible.

### Lambda Function Details

The Lambda function performs the following tasks:
1. **Extracts details** of the uploaded file and source bucket from the event.
2. **Generates a random name** for the new S3 bucket to host the website.
3. **Creates a new S3 bucket** and enables static website hosting.
4. **Moves the `index.html` file** from the source bucket to the new bucket.
5. **Configures the bucket's policy** to allow public access and disables the "Block all public access" setting.
6. **Constructs the website URL** for the newly created static website.
7. **Puts the website URL into SQS `file-processing-logs`**

The Lambda function ensures the website is publicly accessible and puts the URL of the static website into SQS `file-processing-logs` once the process is completed.

### Permissions

The **`createWebSite`** Lambda function requires the following permissions:  

1. **sqs:SendMessage** to `file-processing-logs` SQS
2. **s3:GetObject**, **s3:DeleteObject** to `conversion-service-bucket` S3 bucket
3. **s3:CreateBucket**, **s3:PutObject**, **s3:PutBucketWebsite**, **s3:PutBucketPolicy**, **s3:PutPublicAccessBlock** to dynamically created new S3 Bucket

--- 
## Step 4: Frontend shows the URL to the website in UI

### For this purpose two more elements were configured:
1. Lambda function **`logProcessing`**
2. API Gateway **`logAPI`**

### This is the process how Frontend receives URL:

1. Frontend makes GET request to API Gateway 
2. API Gateway `logAPI` that triggers `logProcessing` lambda
3. Lambda function `logProcessing` that fetches website URL from SQS sends the response back to frontend




