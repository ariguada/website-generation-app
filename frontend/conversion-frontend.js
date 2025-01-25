const bucketName = "convertion-service-bucket";
const region = "us-west-1";
const accessKeyId = "AAAAAAAAAAAAAAA";
const secretAccessKey = "DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD";
const apiGW = "http://example.com"

document.getElementById("uploadButton").addEventListener("click", async () => {
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];

    if (!file || (file.type !== "application/pdf" && file.type !== "text/html")) {
        alert("Please select a PDF or HTML file.");
        return;
    }

    const fileName = file.name;
    const uploadUrl = `https://${bucketName}.s3.${region}.amazonaws.com/${fileName}`;

    const s3Params = {
        method: "PUT",
        headers: {
            "Content-Type": file.type, 
        },
        body: file,
    };

    try {
        const response = await fetch(uploadUrl, s3Params);
        const statusElement = document.getElementById("status");

        if (response.ok) {
            statusElement.textContent = "File uploaded successfully!";
            statusElement.className = "success";
            
            // Wait for 5 seconds before calling the API Gateway
            setTimeout(async () => {
                try {
                    console.log("Calling API Gateway...");

                    const apiResponse = await fetch(apiGW, { 
                        method: "GET",  
                        headers: {
                            "Content-Type": "application/json"
                        },
                    });

                    if (apiResponse.ok) {
                        const apiData = await apiResponse.json();  // Parse the response as JSON
                        console.log("Raw API Response:", apiData);

                        // Extract the link directly from the response
                        const websiteLink = apiData.link; // Directly access the link key

                        if (websiteLink) {
                            // Create and display the "Go to Website" button
                            const goToWebsiteButton = document.createElement("button");
                            goToWebsiteButton.className = "goToWebsiteButton";
                            goToWebsiteButton.textContent = "Go to Website";
                            goToWebsiteButton.onclick = () => {
                                window.open(websiteLink, "_blank");
                            };

                            // Append the button to the page
                            const container = document.querySelector(".container");
                            container.appendChild(goToWebsiteButton);
                        } else {
                            console.log("Link not found in the response.");
                        }
                    } else {
                        console.log("API Gateway error:", apiResponse.statusText);
                    }
                } catch (error) {
                    console.error("Error calling API Gateway:", error);
                }
            }, 5000); // Wait for 5 seconds (5000 milliseconds)
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
