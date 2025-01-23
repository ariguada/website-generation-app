const bucketName = "convertion-service-bucket";
const region = "us-west-1";
const accessKeyId = "AAAAAAAAAAAAAAAAAAAA";
const secretAccessKey = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX";

document.getElementById("uploadButton").addEventListener("click", async () => {
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];

    if (!file || file.type !== "application/pdf") {
        alert("Please select a PDF file.");
        return;
    }

    const fileName = file.name;
    const uploadUrl = `https://${bucketName}.s3.${region}.amazonaws.com/${fileName}`;

    const s3Params = {
        method: "PUT",
        headers: {
            "Content-Type": "application/pdf",
        },
        body: file,
    };

    try {
        const response = await fetch(uploadUrl, s3Params);
        const statusElement = document.getElementById("status");

        if (response.ok) {
            statusElement.textContent = "File uploaded successfully!";
            statusElement.className = "success";
        } else {
            statusElement.textContent = `Error: ${response.statusText}`;
            statusElement.className = "error";
        }
    } catch (error) {
        const statusElement = document.getElementById("status");
        statusElement.textContent = `Error: ${error.message}`;
        statusElement.className = "error";
    }
});
