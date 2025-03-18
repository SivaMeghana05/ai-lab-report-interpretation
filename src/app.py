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
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Load API Key from Streamlit secrets
GENAI_API_KEY = st.secrets["google"]["api_key"]

# Configure Google Gemini API
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Helper functions for data visualization and interpretation
def generate_layman_interpretation(test, status, severity):
    """Generate easy-to-understand interpretation for test results"""
    interpretations = {
        "Hemoglobin": {
            "High": "Your hemoglobin (oxygen-carrying protein) is higher than normal. This might mean your blood is too thick.",
            "Low": "Your hemoglobin is low, which might make you feel tired or short of breath (anemia)."
        },
        "Glucose": {
            "High": "Your blood sugar is higher than normal, which might indicate pre-diabetes or diabetes if persistent.",
            "Low": "Your blood sugar is lower than normal, which might cause weakness or dizziness."
        },
        "Total Cholesterol": {
            "High": "Your cholesterol level is elevated, which may increase your risk of heart disease.",
            "Low": "Your cholesterol is lower than normal, which might affect hormone production."
        },
        "Triglycerides": {
            "High": "Your triglycerides are high, which may increase your risk of heart disease.",
            "Low": "Your triglycerides are lower than normal, which is generally not a concern."
        },
        "HDL Cholesterol": {
            "High": "Your good cholesterol is high, which is beneficial for heart health.",
            "Low": "Your good cholesterol is low, which may increase heart disease risk."
        },
        "LDL Cholesterol": {
            "High": "Your bad cholesterol is high, which increases risk of heart disease.",
            "Low": "Your bad cholesterol is low, which is generally beneficial."
        },
        "Creatinine": {
            "High": "Your creatinine is high, which might indicate kidney function issues.",
            "Low": "Your creatinine is low, which might indicate decreased muscle mass."
        },
        "ALT": {
            "High": "Your liver enzyme (ALT) is elevated, which might indicate liver stress.",
            "Low": "Your liver enzyme (ALT) is low, which is generally not a concern."
        },
        "AST": {
            "High": "Your liver enzyme (AST) is elevated, which might indicate liver stress.",
            "Low": "Your liver enzyme (AST) is low, which is generally not a concern."
        },
        "TSH": {
            "High": "Your thyroid stimulating hormone is high, suggesting possible underactive thyroid.",
            "Low": "Your thyroid stimulating hormone is low, suggesting possible overactive thyroid."
        }
    }
    
    if test in interpretations and status in interpretations[test]:
        return interpretations[test][status]
    return f"This test is {status.lower()} than the normal range. Consult your healthcare provider for specific advice."

def generate_recommendations(test, status):
    """Generate practical recommendations based on test results"""
    recommendations = {
        "Hemoglobin": {
            "High": "• Stay well hydrated\n• Consider consulting a doctor about blood thickness\n• Regular exercise may help",
            "Low": "• Include iron-rich foods (lean meats, spinach, beans)\n• Consider iron supplements (consult doctor)\n• Include vitamin C rich foods to help iron absorption"
        },
        "Glucose": {
            "High": "• Limit sugar and refined carbohydrates\n• Exercise regularly (30 mins daily)\n• Monitor blood sugar levels\n• Consider consulting an endocrinologist",
            "Low": "• Eat regular, balanced meals\n• Include complex carbohydrates\n• Keep a quick sugar source handy\n• Consider small, frequent meals"
        },
        "Total Cholesterol": {
            "High": "• Reduce saturated and trans fats\n• Increase fiber intake\n• Exercise regularly\n• Consider heart-healthy foods",
            "Low": "• Ensure adequate healthy fat intake\n• Consider omega-3 rich foods\n• Consult doctor about hormone health"
        },
        "HDL Cholesterol": {
            "Low": "• Increase physical activity\n• Choose healthy fats (olive oil, avocados)\n• Quit smoking if applicable\n• Consider omega-3 supplements"
        },
        "LDL Cholesterol": {
            "High": "• Limit saturated fats\n• Increase soluble fiber intake\n• Regular exercise\n• Consider plant sterols"
        },
        "Triglycerides": {
            "High": "• Limit sugar and refined carbs\n• Reduce alcohol intake\n• Increase omega-3 fatty acids\n• Regular exercise"
        },
        "Creatinine": {
            "High": "• Stay well hydrated\n• Limit protein intake temporarily\n• Avoid nephrotoxic medications\n• Consider kidney specialist consultation",
            "Low": "• Ensure adequate protein intake\n• Consider strength training\n• Maintain good nutrition"
        }
    }
    
    if test in recommendations and status in recommendations[test]:
        return recommendations[test][status]
    return "• Consult your healthcare provider for personalized advice\n• Consider follow-up testing as recommended\n• Monitor symptoms and changes"

def display_test_results(df):
    """Display test results in a professional, easy-to-understand format"""
    # Population benchmarks for common tests (example values)
    population_benchmarks = {
        "Hemoglobin": {
            "18-44 years": {"male": (13.5, 17.5), "female": (12.0, 15.5)},
            "45+ years": {"male": (13.0, 17.0), "female": (11.5, 15.0)}
        },
        "Total Cholesterol": {
            "18-44 years": (125, 200),
            "45+ years": (125, 200)
        }
    }
    
    for category in df['Category'].unique():
        with st.expander(f"📊 {category} Panel", expanded=True):
            # Add category description with enhanced information
            category_descriptions = {
                "Complete Blood Count": "Basic blood test that evaluates overall health, screens for anemia, infections, and other disorders. Key for assessing oxygen-carrying capacity and immune system function.",
                "Lipid Profile": "Measures cholesterol and triglycerides to assess heart disease risk and cardiovascular health. Essential for heart disease prevention.",
                "Liver Function": "Evaluates liver health, screens for liver damage and monitors liver disease. Important for metabolism and detoxification.",
                "Kidney Function": "Assesses kidney health, filtration efficiency, and screens for kidney disease. Critical for maintaining body's water and mineral balance.",
                "Thyroid Profile": "Measures thyroid hormone levels to evaluate thyroid function and metabolism. Affects energy levels and body weight.",
                "Diabetes Profile": "Evaluates blood sugar control and screens for diabetes or pre-diabetes. Key for metabolic health.",
                "Electrolytes": "Measures essential minerals in blood crucial for nerve and muscle function. Important for heart rhythm and cellular function.",
                "Iron Studies": "Assesses iron levels and helps diagnose anemia or iron overload. Essential for oxygen transport.",
                "Vitamin Profile": "Evaluates levels of essential vitamins for overall health and nutrition. Important for immune function and energy.",
                "Hormone Panel": "Measures hormone levels to assess endocrine function and balance. Affects growth, metabolism, and reproduction."
            }
            
            if category in category_descriptions:
                st.info(f"ℹ️ **What is this panel?**\n{category_descriptions[category]}")
            
            category_df = df[df['Category'] == category].copy()
            
            # Add interpretation guidelines with population comparison
            for _, row in category_df.iterrows():
                with st.container():
                    col1, col2, col3 = st.columns([2, 2, 1])
                    with col1:
                        st.markdown(f"### {row['Test']}")
                        value_color = ('🔴' if row['Status'] == 'High' else '🔵' if row['Status'] == 'Low' else '🟢')
                        st.markdown(f"{value_color} **Current Value:** {row['Value']}")
                        st.markdown(f"**Normal Range:** {row['ReferenceRange']}")
                        
                        # Add trend information with enhanced visualization
                        if 'Trend' in row and row['Trend']:
                            trend_icons = {
                                "Improving": "📈 Improving",
                                "Worsening": "📉 Worsening",
                                "Stable": "➡️ Stable"
                            }
                            trend_icon = trend_icons.get(row['Trend'], "ℹ️")
                            st.markdown(f"**Trend:** {trend_icon}")
                            
                            # Add mini trend visualization if previous values exist
                            if 'PreviousValues' in row and row['PreviousValues']:
                                try:
                                    values = [float(v.split()[0]) for v in row['PreviousValues']]
                                    values.append(float(row['Value'].split()[0]))
                                    
                                    # Create mini trend chart
                                    fig, ax = plt.subplots(figsize=(3, 2))
                                    ax.plot(values, marker='o')
                                    ax.set_title('Value Trend', fontsize=8)
                                    st.pyplot(fig)
                                    plt.close()
                                except:
                                    pass
                    
                    with col2:
                        if row['Status'] != 'Normal':
                            severity = row.get('Severity', 'Moderate')
                            severity_colors = {
                                "Severe": "🔴 **Severe**",
                                "Moderate": "🟡 **Moderate**",
                                "Mild": "🟢 **Mild**"
                            }
                            st.markdown(f"**Severity:** {severity_colors.get(severity, severity)}")
                            
                            st.markdown("**What this means:**")
                            interpretation = generate_layman_interpretation(row['Test'], row['Status'], severity)
                            st.markdown(interpretation)
                            
                            st.markdown("**Recommendations:**")
                            recommendations = generate_recommendations(row['Test'], row['Status'])
                            st.markdown(recommendations)
                        else:
                            st.markdown("✅ **Result is within normal range**")
                            st.markdown("Continue maintaining your healthy lifestyle and regular check-ups.")
                    
                    with col3:
                        # Add population comparison if available
                        if row['Test'] in population_benchmarks:
                            st.markdown("**Population Comparison:**")
                            try:
                                value = float(row['Value'].split()[0])
                                benchmark = population_benchmarks[row['Test']]['18-44 years']  # Simplified for example
                                if value < benchmark[0]:
                                    st.markdown("📊 Below average for your age group")
                                elif value > benchmark[1]:
                                    st.markdown("📊 Above average for your age group")
                                else:
                                    st.markdown("📊 Within average range for your age group")
                            except:
                                st.markdown("📊 Population comparison not available")
                
                st.markdown("---")

# Define prompts for lab report analysis
def get_extraction_prompt(text):
    return f"""
    Extract key lab test parameters from the following lab report as structured data in JSON format.
    For each test include:
    1. "Test": The name of the test
    2. "Value": The numerical value with unit (e.g., "10 g/dL")
    3. "ReferenceRange": The normal reference range
    4. "Status": "High" if above range, "Low" if below range, "Normal" if within range
    5. "Category": Group tests into categories like "Complete Blood Count", "Iron Studies", "Diabetes Profile", etc.
    6. "PreviousValues": Array of up to 3 previous test values with dates if available
    7. "Trend": "Improving", "Worsening", or "Stable" based on previous values
    8. "Severity": Calculate severity as:
       - "Severe" if value is >50% outside range
       - "Moderate" if 25-50% outside range
       - "Mild" if <25% outside range
       - "None" if within range

    Pay special attention to:
    - Maintaining exact test names as shown in report
    - Including all units exactly as specified
    - Preserving reference ranges in original format
    - Capturing trend data from previous results
    - Grouping tests into their proper categories

    Return ONLY valid JSON without explanation, markdown, or text.

    Lab Report Text:
    {text}
    """

def get_interpretation_prompt(text):
    return f"""
    Analyze the following lab report and provide a comprehensive medical interpretation. Format the response as follows:

    EXECUTIVE SUMMARY
    - Overall health assessment in 2-3 sentences
    - List of critical findings requiring immediate attention
    - Health score (0-100) with explanation of calculation

    DETAILED ANALYSIS BY CATEGORY
    [For each test category present in the report]
    - Category name and overview
    - Analysis of each abnormal result:
      * Current value vs reference range
      * Severity assessment
      * Trend analysis (improving/worsening)
      * Clinical significance
    - Potential underlying causes
    - Related health implications

    KEY CONCERNS AND RECOMMENDATIONS
    - Prioritized list of health concerns
    - Specific follow-up tests recommended
    - Suggested specialist consultations if needed
    - Timeline for retesting abnormal values

    LIFESTYLE AND DIETARY ADVICE
    - Specific dietary recommendations based on results
    - Exercise and activity guidelines
    - Lifestyle modifications needed
    - Supplements to consider (if applicable)

    MONITORING PLAN
    - Tests requiring immediate retesting
    - Recommended monitoring schedule
    - Target values to aim for
    - Warning signs to watch for

    Format with clear headers and bullet points. Prioritize actionable insights.
    Focus on patterns and relationships between different test results.

    Lab Report Text:
    {text}
    """

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

# Function to create health score chart with smaller size
def create_health_score_chart(score):
    plt.clf()  # Clear any existing plots
    fig, ax = plt.subplots(figsize=(4, 2), dpi=100)
    cmap = plt.cm.RdYlGn
    norm = plt.Normalize(0, 100)
    
    plt.barh([0], [100], color='lightgray', height=0.3)
    plt.barh([0], [score], color=cmap(norm(score)), height=0.3)
    
    plt.xlim(0, 100)
    plt.ylim(-0.5, 0.5)
    plt.axis('off')
    
    plt.text(score, 0, f'{score}%', 
             ha='center', va='center',
             bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))
    
    plt.close()  # Close the figure to free memory
    return fig

# Function to create severity chart
def create_severity_chart(df):
    plt.clf()  # Clear any existing plots
    severity_counts = df['Severity'].value_counts()
    colors = {'Severe': '#FF5757', 'Moderate': '#FFA500', 'Mild': '#5D9CEC', 'None': '#7ED957'}
    
    fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
    bars = plt.bar(severity_counts.index, severity_counts.values, 
                  color=[colors.get(x, '#CCCCCC') for x in severity_counts.index])
    
    plt.title('Test Result Severities', fontsize=10)
    plt.ylabel('Count', fontsize=8)
    plt.xticks(fontsize=8)
    plt.yticks(fontsize=8)
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    plt.close()  # Close the figure to free memory
    return fig

# Function to create category chart
def create_category_chart(df):
    plt.clf()  # Clear any existing plots
    category_counts = df['Category'].value_counts()
    
    fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
    plt.pie(category_counts.values, labels=category_counts.index, autopct='%1.1f%%',
            colors=plt.cm.Pastel1(np.linspace(0, 1, len(category_counts))),
            textprops={'fontsize': 8})
    plt.title('Test Categories', fontsize=10)
    
    plt.tight_layout()
    plt.close()  # Close the figure to free memory
    return fig

# Function to process and interpret lab reports with structured data output
def analyze_lab_report(text):
    if not text:
        return None, "⚠️ No valid text found for analysis."
    
    try:
        # Get interpretation and structured data using the prompt functions
        interpretation_prompt = get_interpretation_prompt(text)
        extraction_prompt = get_extraction_prompt(text)
        
        interpretation_response = model.generate_content(interpretation_prompt)
        extraction_response = model.generate_content(extraction_prompt)
        
        interpretation = interpretation_response.text if interpretation_response else "⚠️ No interpretation available."
        structured_text = extraction_response.text if extraction_response else None
        
        if structured_text:
            structured_text = structured_text.replace("```json", "").replace("```", "").strip()
            try:
                structured_data = json.loads(structured_text)
                if isinstance(structured_data, dict) and 'tests' in structured_data:
                    return structured_data['tests'], interpretation
                elif isinstance(structured_data, list):
                    return structured_data, interpretation
                return [], interpretation
            except json.JSONDecodeError:
                return [], interpretation
        return [], interpretation
    except Exception as e:
        return [], f"Error: {str(e)}"

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
    
    # Enhanced styles for better formatting
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        alignment=TA_CENTER,
        spaceAfter=30,
        textColor=colors.HexColor('#1B365D'),
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        alignment=TA_LEFT,
        spaceAfter=12,
        textColor=colors.HexColor('#2E7D32'),
        fontName='Helvetica-Bold'
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading3'],
        fontSize=14,
        alignment=TA_LEFT,
        spaceAfter=10,
        textColor=colors.HexColor('#1B365D'),
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_LEFT,
        spaceAfter=8,
        textColor=colors.HexColor('#333333'),
        fontName='Helvetica'
    )
    
    content = []
    
    # Report Header
    content.append(Paragraph("LABORATORY REPORT ANALYSIS", title_style))
    content.append(Spacer(1, 0.3*inch))
    
    # Patient Information Table
    patient_info = [
        ["Patient Information", ""],
        ["Name:", patient_data.get("Name", "Not provided")],
        ["Age:", patient_data.get("Age", "Not provided")],
        ["Patient ID:", patient_data.get("Patient ID", "Not provided")],
        ["Report Date:", datetime.now().strftime("%d/%m/%Y")],
        ["Analysis Date:", datetime.now().strftime("%d/%m/%Y")]
    ]
    
    table = Table(patient_info, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('GRID', (0, 1), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B365D')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('SPAN', (0, 0), (1, 0)),
        ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#F5F9F5')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    content.append(table)
    content.append(Spacer(1, 0.3*inch))
    
    # Test Results Summary
    if structured_data:
        df = pd.DataFrame(structured_data)
        content.append(Paragraph("TEST RESULTS SUMMARY", subtitle_style))
        content.append(Spacer(1, 0.2*inch))
        
        for category in df['Category'].unique():
            content.append(Paragraph(category, header_style))
            category_df = df[df['Category'] == category]
            
            # Table headers with better formatting
            table_data = [['Test Name', 'Result', 'Reference Range', 'Status']]
            
            for _, row in category_df.iterrows():
                status_color = (colors.red if row['Status'] == 'High'
                              else colors.blue if row['Status'] == 'Low'
                              else colors.green)
                
                table_data.append([
                    row['Test'],
                    row['Value'],
                    row['ReferenceRange'],
                    row['Status']
                ])
            
            # Create and style the table
            results_table = Table(table_data, colWidths=[2.5*inch, 1.5*inch, 2*inch, 1*inch])
            results_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B365D')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('ALIGN', (1, 1), (1, -1), 'CENTER'),
                ('ALIGN', (3, 1), (3, -1), 'CENTER'),
            ]))
            
            content.append(results_table)
            content.append(Spacer(1, 0.2*inch))
    
    # Interpretation Section
    content.append(PageBreak())
    content.append(Paragraph("DETAILED ANALYSIS", subtitle_style))
    
    # Process interpretation sections
    sections = interpretation.split('\n\n')
    for section in sections:
        if section.strip():
            if section.strip().upper() == section.strip():
                content.append(Paragraph(section.strip(), header_style))
            else:
                content.append(Paragraph(section.strip(), normal_style))
            content.append(Spacer(1, 0.1*inch))
    
    # Professional Disclaimer
    content.append(Spacer(1, 0.3*inch))
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#666666'),
        alignment=TA_JUSTIFY
    )
    
    disclaimer_text = """
    DISCLAIMER: This report is generated using artificial intelligence and is intended for informational purposes only. 
    It should not be considered as a substitute for professional medical advice, diagnosis, or treatment. 
    Always seek the guidance of your physician or other qualified health provider with any questions you may have regarding your medical condition.
    
    Report generated by HealthLens AI on {date}
    """.format(date=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    
    content.append(Paragraph(disclaimer_text, disclaimer_style))
    
    try:
        doc.build(content)
        pdf_content = buffer.getvalue()
        buffer.close()
        return pdf_content
    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
        return None

# Streamlit UI
st.set_page_config(page_title="Lab Report Interpreter", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        color: #1B365D;
        text-align: center;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #2E7D32;
        font-weight: 600;
    }
    .info-box {
        background-color: #F5F9F5;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 25px;
        border: 1px solid #E0E0E0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .normal-tag {
        background-color: #4CAF50;
        color: white;
        padding: 3px 12px;
        border-radius: 20px;
        font-weight: bold;
    }
    .high-tag {
        background-color: #F44336;
        color: white;
        padding: 3px 12px;
        border-radius: 20px;
        font-weight: bold;
    }
    .low-tag {
        background-color: #2196F3;
        color: white;
        padding: 3px 12px;
        border-radius: 20px;
        font-weight: bold;
    }
    .severity-high {
        color: #F44336;
        font-weight: bold;
    }
    .severity-moderate {
        color: #FF9800;
        font-weight: bold;
    }
    .severity-mild {
        color: #2196F3;
        font-weight: bold;
    }
    .stButton>button {
        background-color: #1B365D;
        color: white;
        font-weight: bold;
        border-radius: 20px;
        padding: 10px 25px;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #2E7D32;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .uploadedFile {
        background-color: #F5F9F5;
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
    }
    .css-1d391kg {
        padding: 1rem 1rem 1.5rem;
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
            st.session_state['lab_data'] = structured_data
            st.session_state['interpretation'] = interpretation
            
            # Generate PDF report with patient information
            patient_data = {
                "Name": patient_name if patient_name else "Not provided",
                "Age": patient_age if patient_age else "Not provided",
                "Patient ID": patient_id if patient_id else "Not provided"
            }
            
            pdf_content = create_pdf_report(patient_data, structured_data, interpretation)
            
            # Display comprehensive analysis results
            st.markdown('<h2 class="sub-header">📊 Comprehensive Analysis Results</h2>', unsafe_allow_html=True)
            
            # Display interpretation
            st.markdown("### 🔍 Complete Analysis")
            st.markdown(interpretation)
            
            # Display test results if available
            if structured_data:  # Changed from checking 'tests' key
                df = pd.DataFrame(structured_data)  # Direct conversion of list to DataFrame
                
                # Display test results in an expandable section
                with st.expander("📋 View Detailed Test Results"):
                st.dataframe(df, use_container_width=True)

            # Provide download button for PDF
            st.download_button(
                label="📥 Download Detailed PDF Report",
                data=pdf_content,
                file_name=f"lab_report_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf"
            )

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**HealthLens AI** © 2025")
with col2:
    st.markdown("Made with ❤️ and Streamlit")
with col3:
    st.markdown("Version 1.0.0")

# Update the main UI section
if 'interpretation' in st.session_state:
    st.markdown("### 🔍 Expert Analysis Results")
    
    # Display interpretation in sections
    sections = st.session_state['interpretation'].split('\n\n')
    for section in sections:
        if section.strip():
            if section.strip().upper() == section.strip():
                st.markdown(f"#### {section.strip()}")
            else:
                st.markdown(section.strip())
    
    # Display test results if available
    if 'lab_data' in st.session_state and st.session_state['lab_data']:
        df = pd.DataFrame(st.session_state['lab_data'])
        display_test_results(df)
