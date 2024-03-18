from flask import Flask, render_template, request, redirect, url_for
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
import time
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Variables
subscription_key = os.getenv('AZURE_COGNITIVE_SUBSCRIPTION_KEY')
endpoint = os.getenv('AZURE_COGNITIVE_ENDPOINT')

computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'  # Define the upload folder

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def extract_text_from_image(image_path):
    with open(image_path, 'rb') as image_file:
        read_response = computervision_client.read_in_stream(image_file, raw=True)

    result = ''
    # Get the operation location (URL with an ID at the end) from the response
    read_operation_location = read_response.headers["Operation-Location"]
    # Grab the ID from the URL
    operation_id = read_operation_location.split("/")[-1]
    
    # Call the "GET" API and wait for it to retrieve the results 
    while True:
        read_result = computervision_client.get_read_result(operation_id)
        if read_result.status not in ['notStarted', 'running']:
            break
        time.sleep(1)

    # Add the detected text to result, line by line
    if read_result.status == OperationStatusCodes.succeeded:
        for text_result in read_result.analyze_result.read_results:
            for line in text_result.lines:
                result += " " + line.text
    return result

@app.route("/", methods=['GET', 'POST'])
def main():
    return render_template("index.html")

@app.route("/submit", methods=['POST'])
def get_output():
    if request.method == 'POST':
        if 'image_file' not in request.files:
            return redirect(request.url)
        
        image_file = request.files['image_file']
        if image_file.filename == '':
            return redirect(request.url)
        
        if image_file:
            filename = image_file.filename
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            extracted_text = extract_text_from_image(image_path)
            os.remove(image_path)  # Remove the uploaded image file after processing
            return render_template("index.html", prediction=extracted_text, img_path=filename)

    return redirect(url_for('main'))

if __name__ == "__main__":
    app.run(debug=True)
