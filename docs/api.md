# HealthLensAI API Documentation

## Overview
This document provides detailed API documentation for the HealthLensAI medical report analysis system.

## Core Components

### AdvancedReportAnalyzer

#### Class: `AdvancedReportAnalyzer`
Main class for analyzing medical reports using AI.

```python
from src.report_analyzer import AdvancedReportAnalyzer

analyzer = AdvancedReportAnalyzer()
```

#### Methods

##### `analyze_lab_report(report_text)`
Analyzes lab report text and returns structured data and interpretation.

**Parameters:**
- `report_text` (str): The text content of the lab report

**Returns:**
- `tuple`: (structured_data, interpretation)
  - `structured_data`: Dictionary containing analyzed test results
  - `interpretation`: AI-generated interpretation of the results

**Example:**
```python
structured_data, interpretation = analyzer.analyze_lab_report(report_text)
```

##### `generate_layman_interpretation(test, status, severity)`
Generates easy-to-understand interpretation for test results.

**Parameters:**
- `test` (str): Name of the test
- `status` (str): Status of the test (High/Low/Normal)
- `severity` (str): Severity level of the result

**Returns:**
- `str`: Human-readable interpretation

##### `generate_recommendations(test, status)`
Generates recommendations based on test results.

**Parameters:**
- `test` (str): Name of the test
- `status` (str): Status of the test

**Returns:**
- `str`: Formatted recommendations

### HealthReportGenerator

#### Class: `HealthReportGenerator`
Main class for generating comprehensive health reports.

```python
from src.report_generator import HealthReportGenerator

generator = HealthReportGenerator()
```

#### Methods

##### `create_pdf_report(patient_data, structured_data=None, interpretation=None, visualization_service=None)`
Creates a comprehensive health report PDF.

**Parameters:**
- `patient_data` (dict): Patient information
- `structured_data` (list, optional): Structured data for visualizations
- `interpretation` (str, optional): AI interpretation of results
- `visualization_service` (object, optional): Service for creating visualizations

**Returns:**
- `bytes`: PDF report as bytes

**Example:**
```python
pdf_content = generator.create_pdf_report(
    patient_data={"Name": "John Doe"},
    structured_data=structured_data,
    interpretation=interpretation
)
```

## Data Structures

### Patient Data
```python
patient_data = {
    "Name": "John Doe",
    "Age": 45,
    "Gender": "Male",
    "Patient ID": "12345",
    "Test Date": "2024-02-20",
    "Collection Date": "2024-02-19"
}
```

### Structured Data
```python
structured_data = [
    {
        "Test": "Hemoglobin",
        "Value": "14.5 g/dL",
        "ReferenceRange": "13.5-17.5 g/dL",
        "Status": "Normal",
        "Category": "Complete Blood Count",
        "Severity": "None"
    }
]
```

## Error Handling

### Common Exceptions
- `ValueError`: Invalid input data
- `FileNotFoundError`: Missing input files
- `JSONDecodeError`: Invalid JSON data
- `Exception`: General processing errors

### Error Response Format
```python
{
    "error": "Error message",
    "details": "Detailed error information",
    "timestamp": "2024-02-20T10:30:00Z"
}
```

## Best Practices

1. **Input Validation**
   - Always validate input data before processing
   - Check for required fields in patient data
   - Verify file formats and content

2. **Error Handling**
   - Use try-except blocks for error handling
   - Log errors with appropriate severity levels
   - Provide meaningful error messages

3. **Performance**
   - Process large reports in chunks
   - Use caching for frequently accessed data
   - Optimize image processing operations

4. **Security**
   - Sanitize input data
   - Handle sensitive information securely
   - Follow HIPAA compliance guidelines

## Examples

### Complete Workflow
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
patient_data = {
    "Name": "John Doe",
    "Age": 45,
    "Gender": "Male"
}

pdf_content = generator.create_pdf_report(
    patient_data=patient_data,
    structured_data=structured_data,
    interpretation=interpretation
)

# Save PDF
with open("health_report.pdf", "wb") as f:
    f.write(pdf_content)
```

## Support
For additional support or questions, please refer to:
- GitHub Issues: [Project Issues](https://github.com/yourusername/healthlensai/issues)
- Documentation: [User Guide](user_guide.md)
- Email: support@healthlensai.com 