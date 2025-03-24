import streamlit as st
from pdf_processor import AdvancedPDFProcessor
from report_analyzer import AdvancedReportAnalyzer
from report_generator import HealthReportGenerator
from visualization import VisualizationService
import time
from datetime import datetime
import logging
import traceback
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("healthlens.log")
    ]
)
logger = logging.getLogger("HealthLensAI")

# Configure matplotlib style
try:
    plt.style.use('default')
except Exception as e:
    logger.warning(f"Could not set matplotlib style: {str(e)}")

# Application version
APP_VERSION = "2.0.0"

# Set page configuration
st.set_page_config(
    page_title="HealthLens AI - Lab Report Interpreter",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        color: #1B365D;
        text-align: center;
        font-weight: 700;
        margin-bottom: 0.5rem;
        background: linear-gradient(90deg, #1B365D, #2E7D32);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
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
        transition: all 0.3s ease;
    }
    .info-box:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transform: translateY(-2px);
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
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.processing_complete = False
    st.session_state.show_tutorial = True
    st.session_state.first_visit = True

# App Header
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown('<h1 class="main-header">🩺 HealthLens AI</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center;">Advanced Lab Report Analysis & Interpretation</p>', unsafe_allow_html=True)

# Tutorial for first-time users
if st.session_state.show_tutorial:
    with st.expander("📚 How to use HealthLens AI", expanded=st.session_state.first_visit):
        st.markdown("""
        ### Welcome to HealthLens AI!
        
        This application helps you understand your lab test results in plain language. Here's how to use it:
        
        1. **Upload your lab report** - We support PDF and Word documents
        2. **Enter basic information** - This helps personalize your analysis
        3. **Click Analyze** - Our AI will process your report
        4. **Review the results** - Get plain-language explanations and recommendations
        5. **Download a PDF report** - Save or share your comprehensive analysis
        
        Your data is processed securely and not stored permanently.
        """)
        
        if st.button("Got it! Don't show again"):
            st.session_state.show_tutorial = False
            st.session_state.first_visit = False
            st.rerun()

# Main content area
st.markdown('<div class="info-box">', unsafe_allow_html=True)

# Patient information input
col1, col2, col3 = st.columns(3)
with col1:
    patient_name = st.text_input("Patient Name", "")
with col2:
    patient_age = st.text_input("Age", "")
    if patient_age and not patient_age.isdigit():
        st.warning("Age should be a number")
with col3:
    patient_id = st.text_input("Patient ID", "")

# File upload
uploaded_file = st.file_uploader(
    "Upload your lab report",
    type=["pdf", "docx"],
    help="We support PDF and Word document formats. Your data is processed securely."
)
st.markdown('</div>', unsafe_allow_html=True)

# Initialize services with better error handling
try:
    pdf_processor = AdvancedPDFProcessor()
    report_analyzer = AdvancedReportAnalyzer()
    report_generator = HealthReportGenerator()
    visualization_service = VisualizationService()
    logger.info("All services initialized successfully")
except Exception as e:
    logger.error(f"Error initializing services: {str(e)}")
    # Create fallback services if needed
    if 'pdf_processor' not in locals():
        pdf_processor = AdvancedPDFProcessor()
    if 'report_analyzer' not in locals():
        report_analyzer = AdvancedReportAnalyzer()
    if 'report_generator' not in locals():
        report_generator = HealthReportGenerator()
    if 'visualization_service' not in locals():
        visualization_service = VisualizationService()

# Process uploaded file with better error handling
if uploaded_file:
    with st.spinner("Processing your document..."):
        try:
            # Extract text based on file type
            file_extension = uploaded_file.name.split(".")[-1].lower()
            if file_extension == "pdf":
                lab_text = pdf_processor.extract_text_from_pdf(uploaded_file)
            elif file_extension == "docx":
                lab_text = pdf_processor.extract_text_from_docx(uploaded_file)
            else:
                st.error("❌ Unsupported file format.")
                st.stop()
                
            # Check if text extraction was successful
            if not lab_text or len(lab_text.strip()) < 50:
                st.warning("⚠️ Limited text extracted from the document. Results may be incomplete.")
                
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}\n{traceback.format_exc()}")
            st.error(f"❌ Error processing file: {str(e)}")
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
            structured_data, interpretation = report_analyzer.analyze_lab_report(lab_text)
            
            # Store in session state
            st.session_state.lab_data = structured_data
            st.session_state.interpretation = interpretation
            st.session_state.processing_complete = True
            
            # Generate PDF report with patient information
            patient_data = {
                "Name": patient_name if patient_name else "Not provided",
                "Age": patient_age if patient_age else "Not provided",
                "Patient ID": patient_id if patient_id else "Not provided"
            }
            
            try:
                pdf_content = report_generator.create_pdf_report(
                    patient_data, structured_data, interpretation, visualization_service
                )
                
                if pdf_content is None:
                    st.error("Failed to generate PDF report. Please try again.")
                    logger.error("PDF generation failed")
                else:
                    # Store PDF in session state
                    st.session_state.pdf_content = pdf_content
                    logger.info("PDF report generated successfully")
            except Exception as e:
                st.error(f"Error generating PDF report: {str(e)}")
                logger.error(f"PDF generation error: {str(e)}\n{traceback.format_exc()}")
            
            # Force a rerun to update the UI
            st.rerun()

# Display results if processing is complete
if 'processing_complete' in st.session_state and st.session_state.processing_complete:
    # Display comprehensive analysis results
    st.markdown('<h2 class="sub-header">📊 Comprehensive Analysis Results</h2>', unsafe_allow_html=True)
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📝 Analysis", "📊 Visualizations", "📋 Raw Data"])
    
    with tab1:
        # Display interpretation
        st.markdown("### 🔍 Complete Analysis")
        st.markdown(st.session_state.interpretation)
        
        # Provide download button for PDF
        if 'pdf_content' in st.session_state and st.session_state.pdf_content:
            st.download_button(
                label="📥 Download Detailed PDF Report",
                data=st.session_state.pdf_content,
                file_name=f"lab_report_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                help="Download a comprehensive PDF report with all analysis and visualizations"
            )
    
    with tab2:
        # Display visualizations with better error handling
        try:
            if 'lab_data' in st.session_state and st.session_state.lab_data:
                import pandas as pd
                df = pd.DataFrame(st.session_state.lab_data)
                
                # Display health score gauge with error handling
                try:
                    health_score = visualization_service.extract_health_score(st.session_state.interpretation)
                    if health_score > 0:
                        st.markdown("### Health Score")
                        fig = visualization_service.create_health_score_chart(health_score)
                        st.pyplot(fig)
                        plt.close(fig)  # Clean up
                except Exception as e:
                    logger.error(f"Error creating health score chart: {str(e)}")
                    st.warning("Could not generate health score visualization")
                
                # Display severity distribution with error handling
                try:
                    st.markdown("### Test Result Severity Distribution")
                    fig = visualization_service.create_severity_chart(df)
                    st.pyplot(fig)
                    plt.close(fig)  # Clean up
                except Exception as e:
                    logger.error(f"Error creating severity chart: {str(e)}")
                    st.warning("Could not generate severity distribution visualization")
                
                # Display category distribution with error handling
                try:
                    st.markdown("### Test Categories Analysis")
                    fig = visualization_service.create_category_chart(df)
                    st.pyplot(fig)
                    plt.close(fig)  # Clean up
                except Exception as e:
                    logger.error(f"Error creating category chart: {str(e)}")
                    st.warning("Could not generate category analysis visualization")
                
        except Exception as e:
            logger.error(f"Error in visualization tab: {str(e)}\n{traceback.format_exc()}")
            st.error("An error occurred while generating visualizations")
    
    with tab3:
        # Display raw test results
        if 'lab_data' in st.session_state and st.session_state.lab_data:
            import pandas as pd
            df = pd.DataFrame(st.session_state.lab_data)
            
            st.markdown("### Raw Test Results")
            st.dataframe(df, use_container_width=True)
            
            # Add export options
            col1, col2 = st.columns(2)
            with col1:
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name=f"lab_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            with col2:
                json_str = df.to_json(orient='records', indent=2)
                st.download_button(
                    label="📥 Download as JSON",
                    data=json_str,
                    file_name=f"lab_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
    
    # Display detailed test results
    if 'lab_data' in st.session_state and st.session_state.lab_data:
        import pandas as pd
        df = pd.DataFrame(st.session_state.lab_data)
        report_analyzer.display_test_results(df)

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"**HealthLens AI** © {datetime.now().year}")
with col2:
    st.markdown("Made with ❤️ and Streamlit")
with col3:
    st.markdown(f"Version {APP_VERSION}")