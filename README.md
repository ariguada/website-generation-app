## Step 1: Upload PDF to S3 via Frontend

This step provides a simple frontend that allows users to upload PDF files to the S3 bucket `convertion-service-bucket`. The interface is hosted on the same bucket and built with an HTML file and a JavaScript file.

### Frontend Details
- **HTML**: Provides a file input, an upload button, and a status message area for user interaction.
- **JavaScript**: Handles the file upload directly to S3 using a PUT request.

The S3 bucket name, region, and access credentials are temporarily hardcoded for simplicity. The files are uploaded directly to S3 with basic error handling and status updates displayed to the user.


## Step 2: Trigger CloudConvert Job via Lambda

When a PDF file is uploaded to the S3 bucket, it triggers the **TriggerCloudConvertJob** Lambda function. This function creates a job on CloudConvert to convert the PDF file to HTML and saves the resulting HTML file back to the same S3 bucket.

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


## Step 3: Create Static Website via Lambda

When the HTML file (`index.html`) is uploaded to the `convertion-service-bucket`, it triggers the **createWebSite** Lambda function. This function creates a new S3 bucket, copies the `index.html` file from the original bucket to the new one, and enables static website hosting for the new bucket. The function also sets the necessary permissions to make the website publicly accessible.

### Lambda Function Details

The Lambda function performs the following tasks:
1. **Extracts details** of the uploaded file and source bucket from the event.
2. **Generates a random name** for the new S3 bucket to host the website.
3. **Creates a new S3 bucket** and enables static website hosting.
4. **Copies the `index.html` file** from the source bucket to the new bucket.
5. **Configures the bucket's policy** to allow public access and disables the "Block all public access" setting.
6. **Constructs the website URL** for the newly created static website.

The Lambda function ensures the website is publicly accessible and returns the URL of the static website once the process is completed.

