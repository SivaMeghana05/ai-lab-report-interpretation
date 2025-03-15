import streamlit as st
import google.generativeai as genai
import PyPDF2
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from docx import Document

# Set up Google Gemini API
GENAI_API_KEY = "AIzaSyBGDzeo-EVUi5ZH4gdZkm7bdIW5dJeeQiQ"  # Replace with your actual API key
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()

# Function to extract text from DOCX
def extract_text_from_docx(docx_file):
    doc = Document(docx_file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text.strip()

# Function to process and interpret lab reports
def analyze_lab_report(text):
    prompt = f"Extract key lab test parameters and interpret their values:\n\n{text}"
    response = model.generate_content(prompt)
    return response.text if response else "Error: No response from AI."

# Streamlit UI
st.set_page_config(page_title="Lab Report Interpreter", layout="wide")
st.title("🩺 AI-Powered Lab Report Analysis")
st.write("📄 Upload your lab report (PDF/DOCX) to get a detailed health analysis.")

# File Upload
uploaded_file = st.file_uploader("Upload Lab Report", type=["pdf", "docx"])

if uploaded_file:
    st.success("✅ File Uploaded Successfully!")

    # Extract text from the uploaded file
    file_extension = uploaded_file.name.split(".")[-1]
    
    if file_extension == "pdf":
        lab_text = extract_text_from_pdf(uploaded_file)
    elif file_extension == "docx":
        lab_text = extract_text_from_docx(uploaded_file)
    else:
        st.error("❌ Unsupported file format.")
        st.stop()

    # Display extracted text
    with st.expander("🔍 View Extracted Lab Report Text"):
        st.text_area("Extracted Text", lab_text, height=300)

    # AI Interpretation
    if st.button("🧠 Interpret Lab Report"):
        st.subheader("📊 AI-Generated Lab Report Interpretation")
        interpretation = analyze_lab_report(lab_text)
        st.write(interpretation)

        # Sample extracted data (you will replace this with AI output)
        lab_data = {
            "Test": ["Hemoglobin", "Blood Sugar", "Cholesterol", "Vitamin D", "Calcium"],
            "Value": [13.5, 110, 180, 25, 9.2],
            "Normal Range": ["12-16 g/dL", "70-99 mg/dL", "<200 mg/dL", "30-100 ng/mL", "8.5-10.5 mg/dL"],
        }

        df = pd.DataFrame(lab_data)
        st.write("📌 **Extracted Lab Values**")
        st.dataframe(df, use_container_width=True)

        # Plot Bar Chart
        st.subheader("📊 Lab Report Chart")
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(df["Test"], df["Value"], color=["blue", "red", "green", "purple", "orange"])
        ax.set_ylabel("Measured Value")
        ax.set_title("Lab Test Results")
        st.pyplot(fig)
