import cv2
import pytesseract
import re
import numpy as np

# Set Tesseract Path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Load and preprocess image
image_path = r"D:\MyProjects\ai-lab-report-interpretation\sample_lab_report.jpg"  # Ensure this file exists in your project folder
image = cv2.imread(image_path)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

# Perform OCR
extracted_text = pytesseract.image_to_string(gray)

# Extract key information using regex
def extract_lab_data(text):
    data = {}
    
    # Extract patient name (Assuming format: "Patient Name: John Doe")
    name_match = re.search(r'Patient\s*Name:\s*([A-Za-z ]+)', text)
    if name_match:
        data["Patient Name"] = name_match.group(1).strip()
    
    # Extract test names and values (Assuming format: "Test Name: 123.4 mg/dL")
    test_matches = re.findall(r'([A-Za-z ]+):\s*([\d.]+)\s*(\w+)', text)
    if test_matches:
        data["Tests"] = [{"Name": test[0].strip(), "Value": test[1], "Unit": test[2]} for test in test_matches]

    return data

# Get extracted details
lab_data = extract_lab_data(extracted_text)

# Print results
print("Extracted Lab Data:")
print(lab_data)
