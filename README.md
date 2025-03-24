# HealthLensAI - Medical Report Analysis System

## Overview
HealthLensAI is an advanced medical report analysis system that transforms complex lab reports into clear, actionable insights using AI-powered technology. The system processes medical reports, extracts key information, and generates comprehensive health reports with visualizations and recommendations.

## Features
- **Smart PDF Processing**: Advanced extraction of text and data from medical reports
- **AI-Powered Analysis**: Intelligent interpretation of test results using Google's Gemini models
- **Interactive UI**: User-friendly interface for viewing and analyzing results
- **Professional Report Generation**: Comprehensive PDF reports with visualizations
- **Educational Content**: Integrated health information and recommendations

## Technology Stack
- Python 3.8+
- PyMuPDF for PDF processing
- OpenCV for image analysis
- Tesseract OCR for text extraction
- Google Gemini AI models
- Streamlit for UI
- Matplotlib for visualizations
- ReportLab for PDF generation

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/healthlensai.git
cd healthlensai
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Usage

### Command Line
```bash
python src/process_lab_report.py --input path/to/report.pdf --output path/to/output
```

### Python API
```python
from src.report_analyzer import AdvancedReportAnalyzer
from src.report_generator import HealthReportGenerator

# Initialize components
analyzer = AdvancedReportAnalyzer()
generator = HealthReportGenerator()

# Process a report
report_text = "Your lab report text here"
structured_data, interpretation = analyzer.analyze_lab_report(report_text)

# Generate PDF report
pdf_content = generator.create_pdf_report(
    patient_data={"Name": "John Doe"},
    structured_data=structured_data,
    interpretation=interpretation
)
```

## Project Structure
```
healthlensai/
├── src/
│   ├── __init__.py
│   ├── process_lab_report.py
│   ├── report_analyzer.py
│   ├── report_generator.py
│   └── ocr_processor.py
├── tests/
│   └── __init__.py
├── docs/
│   ├── api.md
│   └── user_guide.md
├── requirements.txt
├── README.md
└── LICENSE
```

## Documentation
- [API Documentation](docs/api.md)
- [User Guide](docs/user_guide.md)
- [Development Guide](docs/development.md)

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
- Google Gemini AI for providing the AI models
- PyMuPDF team for PDF processing capabilities
- All contributors and maintainers

## Contact
For questions and support, please open an issue in the GitHub repository.
