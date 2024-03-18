from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
import os
import time
from dotenv import load_dotenv

load_dotenv()

# Authenticate
key = os.getenv("AZURE_OCR_KEY")
endpoint = os.getenv("AZURE_OCR_ENDPOINT")
computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))
# End - Authenticate

class OCR:
    @staticmethod
    def OCR_FILE(path):
        with open(path, "rb") as file:
            response = computervision_client.read_in_stream(file, raw=True)
        return response

    @staticmethod
    def GET_TEXT_FROM_FILE(file):
        response = OCR.OCR_FILE(file)
        operation_location = response.headers["Operation-Location"]
        operation_id = operation_location.split("/")[-1]
        
        while True:
            result = computervision_client.get_read_result(operation_id)
            if result.status not in ['notStarted', 'running']:
                break
            time.sleep(1)

        return_text = ''
        if result.status == OperationStatusCodes.succeeded:
            for text_result in result.analyze_result.read_results:
                for line in text_result.lines:
                    return_text += line.text + '\n'

        return return_text

local_image_path = 'C:/Users/prade/OneDrive/Desktop/Projects/OCR Project/Images/IMG_3238.png'
extracted_text = OCR.GET_TEXT_FROM_FILE(local_image_path)
print("Extracted text:")
print(extracted_text)
