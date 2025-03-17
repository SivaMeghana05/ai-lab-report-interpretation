import streamlit as st
import google.generativeai as genai
import PyPDF2
import pandas as pd
from io import BytesIO
from docx import Document
import json
import time
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime

# Load API Key from Streamlit secrets
GENAI_API_KEY = st.secrets["google"]["api_key"]

# Configure Google Gemini API
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
        return text.strip() if text else "⚠️ No readable text found in PDF."
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

# Function to extract text from DOCX
def extract_text_from_docx(docx_file):
    try:
        doc = Document(docx_file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip() if text else "⚠️ No readable text found in DOCX."
    except Exception as e:
        return f"Error reading DOCX: {str(e)}"

# Function to process and interpret lab reports with structured data output
def analyze_lab_report(text):
    if not text:
        return None, "⚠️ No valid text found for analysis."
    
    # First prompt to get general interpretation
    interpretation_prompt = f"""
    Analyze the following lab report and provide a detailed interpretation:
    1. Highlight abnormal values and their significance
    2. Provide a comprehensive summary of the overall health indicators
    3. Identify potential health concerns or patterns
    4. Suggest specific follow-up actions and lifestyle modifications
    5. Provide dietary recommendations if relevant
    6. List any medications that might need adjustment
    7. Recommend additional tests if necessary
    
    Lab Report Text:
    {text}
    """
    
    # Second prompt to extract structured data
    extraction_prompt = f"""
    Extract key lab test parameters from the following lab report as structured data in JSON format.
    For each test include:
    1. "Test": The name of the test
    2. "Value": The numerical value (just the number)
    3. "Unit": The unit of measurement
    4. "NormalRange": The normal reference range
    5. "Status": Either "Normal", "High", or "Low"
    6. "Category": The category of the test (e.g., "Blood", "Metabolic", "Hormonal", etc.)
    7. "Severity": The severity level of any abnormality ("None", "Mild", "Moderate", "Severe")
    
    Return ONLY valid JSON without explanation, markdown, or text. The JSON should have a single key "tests" containing an array of test objects.
    
    Lab Report Text:
    {text}
    """
    
    try:
        # Get interpretation
        interpretation_response = model.generate_content(interpretation_prompt)
        interpretation = interpretation_response.text if interpretation_response else "⚠️ No interpretation available."
        
        # Get structured data
        extraction_response = model.generate_content(extraction_prompt)
        structured_text = extraction_response.text if extraction_response else None
        
        # Clean up JSON text (remove markdown code blocks if present)
        if structured_text:
            structured_text = structured_text.replace("```json", "").replace("```", "").strip()
            try:
                structured_data = json.loads(structured_text)
                return structured_data, interpretation
            except json.JSONDecodeError:
                return None, interpretation
        
        return None, interpretation
    except Exception as e:
        return None, f"Error: {str(e)}"

# Function to determine color based on status
def get_color(status):
    if status == "High":
        return "#FF5757"  # Red
    elif status == "Low":
        return "#5D9CEC"  # Blue
    else:
        return "#7ED957"  # Green

# Function to create PDF report
def create_pdf_report(patient_data, structured_data, interpretation):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        name='Title',
        parent=styles['Heading1'],
        fontSize=24,
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    subtitle_style = ParagraphStyle(
        name='Subtitle',
        parent=styles['Heading2'],
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    header_style = ParagraphStyle(
        name='Header',
        parent=styles['Heading3'],
        fontSize=14,
        alignment=TA_LEFT,
        spaceAfter=10
    )
    
    normal_style = ParagraphStyle(
        name='Normal',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_LEFT,
        spaceAfter=6,
        leading=14  # Increased line spacing
    )
    
    interpretation_style = ParagraphStyle(
        name='Interpretation',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceAfter=12,
        leading=16,  # Increased line spacing
        firstLineIndent=20  # Add indentation for paragraphs
    )
    
    # Document content
    content = []
    
    # Cover page
    content.append(Paragraph("LAB REPORT ANALYSIS", title_style))
    content.append(Spacer(1, 0.5*inch))
    content.append(Paragraph("HealthLens AI", subtitle_style))
    content.append(Spacer(1, 1*inch))
    
    # Patient information
    data = [
        ["Name:", patient_data.get("Name", "Not provided")],
        ["Age:", patient_data.get("Age", "Not provided")],
        ["Patient ID:", patient_data.get("Patient ID", "Not provided")],
        ["Report Date:", datetime.now().strftime("%B %d, %Y")],
        ["Analysis Date:", datetime.now().strftime("%B %d, %Y")]
    ]
    
    table = Table(data, colWidths=[1.5*inch, 3*inch])
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    content.append(table)
    content.append(PageBreak())
    
    # AI Interpretation
    content.append(Paragraph("AI INTERPRETATION", header_style))
    content.append(Spacer(1, 0.2*inch))
    
    # Split interpretation into paragraphs and format each one
    paragraphs = interpretation.split('\n')
    for para in paragraphs:
        if para.strip():  # Only add non-empty paragraphs
            content.append(Paragraph(para.strip(), interpretation_style))
    
    content.append(PageBreak())
    
    # Test Results
    if structured_data and 'tests' in structured_data:
        tests = structured_data['tests']
        df = pd.DataFrame(tests)
        
        # Group tests by category
        if 'Category' in df.columns:
            for category in df['Category'].unique():
                content.append(Paragraph(f"TEST RESULTS - {category.upper()}", header_style))
                content.append(Spacer(1, 0.2*inch))
                
                category_df = df[df['Category'] == category]
                
                # Create table data
                table_data = [['Test', 'Value', 'Unit', 'Reference Range', 'Status']]
                for _, row in category_df.iterrows():
                    table_data.append([
                        row['Test'],
                        str(row['Value']),
                        row['Unit'],
                        row['NormalRange'],
                        row['Status']
                    ])
                
                # Create and style the table
                table = Table(table_data, colWidths=[1.5*inch, 1*inch, 0.8*inch, 1.5*inch, 1*inch])
                table.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                ]))
                
                content.append(table)
                content.append(Spacer(1, 0.3*inch))
        
        # Abnormal Results Summary
        content.append(Paragraph("ABNORMAL RESULTS SUMMARY", header_style))
        content.append(Spacer(1, 0.2*inch))
        
        abnormal_df = df[df['Status'] != 'Normal']
        if not abnormal_df.empty:
            for _, row in abnormal_df.iterrows():
                content.append(Paragraph(
                    f"• {row['Test']}: {row['Value']} {row['Unit']} ({row['Status']}) - {row['Severity']} severity",
                    normal_style
                ))
        else:
            content.append(Paragraph("No abnormal results found in this report.", normal_style))
        
        content.append(PageBreak())
    
    # Disclaimer
    disclaimer_text = """
    DISCLAIMER: This analysis is generated by AI and is for informational purposes only. 
    It should not be considered as a substitute for professional medical advice, diagnosis, or treatment. 
    Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.
    """
    content.append(Paragraph(disclaimer_text, normal_style))
    
    # Build the PDF
    doc.build(content)
    
    # Get the PDF content
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content

# Streamlit UI
st.set_page_config(page_title="Lab Report Interpreter", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E4057;
        text-align: center;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #4B7F52;
    }
    .info-box {
        background-color: #F0F2F6;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .normal-tag {
        background-color: #7ED957;
        color: white;
        padding: 2px 10px;
        border-radius: 15px;
        font-weight: bold;
    }
    .high-tag {
        background-color: #FF5757;
        color: white;
        padding: 2px 10px;
        border-radius: 15px;
        font-weight: bold;
    }
    .low-tag {
        background-color: #5D9CEC;
        color: white;
        padding: 2px 10px;
        border-radius: 15px;
        font-weight: bold;
    }
    .severity-high {
        color: #FF5757;
        font-weight: bold;
    }
    .severity-moderate {
        color: #FFA500;
        font-weight: bold;
    }
    .severity-mild {
        color: #5D9CEC;
    }
</style>
""", unsafe_allow_html=True)

# App Header
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown('<h1 class="main-header">🩺 HealthLens AI</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center;">Advanced Lab Report Analysis</p>', unsafe_allow_html=True)

# Main content area
st.markdown('<div class="info-box">', unsafe_allow_html=True)

# Add patient information input fields
col1, col2, col3 = st.columns(3)
with col1:
    patient_name = st.text_input("Patient Name", "")
with col2:
    patient_age = st.text_input("Age", "")
with col3:
    patient_id = st.text_input("Patient ID", "")

uploaded_file = st.file_uploader("Upload your lab report", type=["pdf", "docx"], 
                             help="We support PDF and Word document formats")
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file:
    with st.spinner("Processing your document..."):
        # Extract text based on file type
        file_extension = uploaded_file.name.split(".")[-1]
        if file_extension == "pdf":
            lab_text = extract_text_from_pdf(uploaded_file)
        elif file_extension == "docx":
            lab_text = extract_text_from_docx(uploaded_file)
        else:
            st.error("❌ Unsupported file format.")
            st.stop()
    
    st.success(f"✅ File '{uploaded_file.name}' uploaded and processed!")
    
    # Display extracted text with better UX
    with st.expander("🔍 View Extracted Lab Report Text", expanded=False):
        st.text_area("Extracted Text", lab_text, height=250)
    
    # AI Interpretation section
    col1, col2 = st.columns([1, 5])
    with col1:
        analyze_btn = st.button("🧠 Analyze", use_container_width=True)
    with col2:
        if analyze_btn:
            # Show a more engaging progress indicator
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i in range(101):
                # Update progress bar
                progress_bar.progress(i)
                if i < 30:
                    status_text.text("Extracting lab values...")
                elif i < 70:
                    status_text.text("Analyzing results...")
                elif i < 95:
                    status_text.text("Generating interpretation...")
                else:
                    status_text.text("Finalizing report...")
                time.sleep(0.02)
            
            # Remove progress indicators
            progress_bar.empty()
            status_text.empty()
            
            # Process the lab report
            structured_data, interpretation = analyze_lab_report(lab_text)
            
            # Store in session state
            if structured_data:
                st.session_state['lab_data'] = structured_data
                st.session_state['interpretation'] = interpretation
            else:
                st.session_state['lab_data'] = None
                st.session_state['interpretation'] = interpretation
            
            # Generate PDF report with patient information
            patient_data = {
                "Name": patient_name if patient_name else "Not provided",
                "Age": patient_age if patient_age else "Not provided",
                "Patient ID": patient_id if patient_id else "Not provided"
            }
            
            pdf_content = create_pdf_report(patient_data, structured_data, interpretation)
            
            # Provide download button for PDF
            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_content,
                file_name=f"lab_report_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf"
            )
            
            # Display comprehensive analysis results
            st.markdown('<h2 class="sub-header">📊 Comprehensive Analysis Results</h2>', unsafe_allow_html=True)
            
            # Display interpretation in sections
            st.markdown("### 🔍 Detailed Interpretation")
            st.markdown(interpretation)
            
            # Display structured data if available
            if structured_data and 'tests' in structured_data:
                tests = structured_data['tests']
                if tests:
                    # Create a clean dataframe for display
                    df = pd.DataFrame(tests)
                    
                    # Group tests by category
                    if 'Category' in df.columns:
                        st.markdown("### 📋 Test Results by Category")
                        for category in df['Category'].unique():
                            # Create a copy of the filtered DataFrame
                            category_df = df[df['Category'] == category].copy()
                            st.markdown(f"#### {category}")
                            
                            # Format the dataframe with colored status indicators
                            def highlight_status(val):
                                if val == "High":
                                    return '<span class="high-tag">HIGH</span>'
                                elif val == "Low":
                                    return '<span class="low-tag">LOW</span>'
                                else:
                                    return '<span class="normal-tag">NORMAL</span>'
                            
                            # Apply formatting if Status column exists
                            if 'Status' in category_df.columns:
                                category_df.loc[:, 'Status'] = category_df['Status'].apply(highlight_status)
                                st.markdown(category_df.to_html(escape=False, index=False), unsafe_allow_html=True)
                            else:
                                st.dataframe(category_df, use_container_width=True)
                    
                    # Display severity summary
                    if 'Severity' in df.columns:
                        st.markdown("### ⚠️ Abnormal Results Summary")
                        abnormal_df = df[df['Status'] != 'Normal']
                        if not abnormal_df.empty:
                            for _, row in abnormal_df.iterrows():
                                severity_class = f"severity-{row['Severity'].lower()}"
                                st.markdown(f"""
                                    <div class="{severity_class}">
                                    • {row['Test']}: {row['Value']} {row['Unit']} ({row['Status']}) - {row['Severity']} severity
                                    </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.success("No abnormal results found in this report.")
                    
                    # Display reference ranges
                    st.markdown("### 📊 Reference Ranges")
                    ref_df = df[['Test', 'NormalRange']].copy()
                    ref_df.columns = ['Test', 'Reference Range']
                    st.dataframe(ref_df, use_container_width=True)
            else:
                st.warning("Could not extract structured data from this report. See the interpretation above.")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**HealthLens AI** © 2025")
with col2:
    st.markdown("Made with ❤️ and Streamlit")
with col3:
    st.markdown("Version 1.0.0")
