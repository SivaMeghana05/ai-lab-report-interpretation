# HealthLensAI User Guide

## Introduction
Welcome to the HealthLensAI User Guide. This document will help you understand and use the HealthLensAI medical report analysis system effectively.

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Tesseract OCR installed on your system
- Required Python packages (install via `pip install -r requirements.txt`)

### Installation
1. Clone the repository:
```bash
git clone https://github.com/yourusername/healthlensai.git
cd healthlensai
```

2. Set up your environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure your environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Basic Usage

### Processing a Medical Report

#### Command Line
```bash
python src/process_lab_report.py --input path/to/report.pdf --output path/to/output
```

#### Python API
```python
from src.report_analyzer import AdvancedReportAnalyzer
from src.report_generator import HealthReportGenerator

# Initialize components
analyzer = AdvancedReportAnalyzer()
generator = HealthReportGenerator()

# Process report
report_text = "Your lab report text here"
structured_data, interpretation = analyzer.analyze_lab_report(report_text)

# Generate PDF
pdf_content = generator.create_pdf_report(
    patient_data={"Name": "John Doe"},
    structured_data=structured_data,
    interpretation=interpretation
)
```

## Features

### 1. Report Analysis
- Automatic extraction of test results
- Reference range validation
- Severity assessment
- Pattern recognition

### 2. Interactive UI
- Category-based filtering
- Real-time data visualization
- Detailed interpretations
- Personalized recommendations

### 3. Report Generation
- Professional PDF output
- Educational content
- Visual data representation
- Comprehensive health insights

## Advanced Usage

### Customizing Report Generation

#### Report Sections
The generated report includes:
1. Cover Page
2. Table of Contents
3. Doctor Summary
4. Wellbeing Index
5. Important Parameters
6. Detailed Analysis
7. Health Recommendations
8. Educational Content
9. References

#### Customizing Visualizations
```python
# Example of customizing visualization settings
visualization_service = VisualizationService(
    chart_style='modern',
    color_scheme='medical',
    dpi=300
)
```

### Error Handling

#### Common Issues and Solutions

1. **OCR Errors**
   - Ensure Tesseract is properly installed
   - Check image quality and resolution
   - Verify file format support

2. **PDF Processing Errors**
   - Verify PDF is not corrupted
   - Check file permissions
   - Ensure sufficient memory

3. **AI Model Errors**
   - Check internet connectivity
   - Verify API credentials
   - Monitor rate limits

## Best Practices

### 1. Input Data
- Use high-quality scans for OCR
- Ensure PDFs are not password-protected
- Include complete patient information

### 2. Performance
- Process large reports in batches
- Use appropriate image resolutions
- Monitor system resources

### 3. Security
- Handle sensitive data appropriately
- Follow HIPAA guidelines
- Secure API credentials

## Troubleshooting

### Common Problems

1. **Installation Issues**
   ```bash
   # Verify Python version
   python --version
   
   # Check package installation
   pip list | grep healthlensai
   ```

2. **Runtime Errors**
   - Check log files in `logs/` directory
   - Verify environment variables
   - Monitor system resources

3. **Output Issues**
   - Verify output directory permissions
   - Check disk space
   - Validate file formats

## Support

### Getting Help
- Check the [FAQ](faq.md)
- Review [API Documentation](api.md)
- Open a GitHub issue
- Contact support team

### Reporting Issues
When reporting issues, include:
1. Error message
2. System information
3. Steps to reproduce
4. Sample input data

## Updates and Maintenance

### Checking for Updates
```bash
git pull origin main
pip install -r requirements.txt
```

### Backup and Recovery
- Regular backup of configuration
- Save processed reports
- Document custom settings

## Security Guidelines

### Data Protection
1. Secure storage of reports
2. Encryption of sensitive data
3. Access control implementation

### Compliance
- HIPAA guidelines
- Data privacy regulations
- Security best practices

## Contact Information
- Technical Support: support@healthlensai.com
- Documentation: docs@healthlensai.com
- General Inquiries: info@healthlensai.com 