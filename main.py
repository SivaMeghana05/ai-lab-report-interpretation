from src.report_generator import HealthReportGenerator
from datetime import datetime


def main():
    # Sample patient data
    patient_data = {
        "name": "Deepa",
        "age": 35,
        "gender": "Female",
        "id": "DP12345",
        "test_date": datetime.now().strftime("%Y-%m-%d"),
        "collection_date": datetime.now().strftime("%Y-%m-%d")
    }
   
    # Sample lab results with comprehensive test data
    lab_results = [
        {
            "name": "Hemoglobin",
            "value": "11.2",
            "unit": "g/dL",
            "reference_range": "12.0-15.5",
            "is_abnormal": True,
            "category": "Complete Blood Count",
            "severity": "Mild"
        },
        {
            "name": "Glucose (Fasting)",
            "value": "105",
            "unit": "mg/dL",
            "reference_range": "70-99",
            "is_abnormal": True,
            "category": "Diabetes Profile",
            "severity": "Mild"
        },
        {
            "name": "Total Cholesterol",
            "value": "220",
            "unit": "mg/dL",
            "reference_range": "<200",
            "is_abnormal": True,
            "category": "Lipid Profile",
            "severity": "Moderate"
        },
        {
            "name": "HDL Cholesterol",
            "value": "45",
            "unit": "mg/dL",
            "reference_range": ">50",
            "is_abnormal": True,
            "category": "Lipid Profile",
            "severity": "Mild"
        },
        {
            "name": "Vitamin D, 25-OH",
            "value": "22",
            "unit": "ng/mL",
            "reference_range": "30-100",
            "is_abnormal": True,
            "category": "Vitamin Profile",
            "severity": "Moderate"
        }
    ]
   
    # Sample interpretation from AI analysis
    interpretation = """
    EXECUTIVE SUMMARY
    Your recent lab results indicate several areas that require attention, particularly related to blood sugar, cholesterol, and vitamin D levels. While most deviations are mild to moderate, they suggest the need for lifestyle modifications and possibly medical intervention.
   
    DETAILED ANALYSIS BY CATEGORY
   
    Complete Blood Count:
    - Hemoglobin is slightly below normal range, indicating mild anemia
    - This may be contributing to fatigue and reduced energy levels
   
    Diabetes Profile:
    - Fasting glucose is elevated, suggesting pre-diabetes
    - Early intervention through diet and lifestyle changes is recommended
   
    Lipid Profile:
    - Both total cholesterol and HDL (good cholesterol) need attention
    - Current levels indicate moderate cardiovascular risk
   
    Vitamin Profile:
    - Vitamin D deficiency detected
    - This can affect bone health and immune function
   
    RECOMMENDATIONS
    1. Schedule a follow-up with your primary care physician
    2. Consider dietary modifications to address cholesterol and blood sugar
    3. Discuss vitamin D supplementation with your healthcare provider
    4. Implement regular exercise routine
    5. Consider iron-rich foods to address mild anemia
    """
   
    # Structured data for visualizations
    structured_data = {
        "test_categories": ["CBC", "Diabetes", "Lipids", "Vitamins"],
        "abnormal_counts": [1, 1, 2, 1],
        "severity_distribution": {
            "Mild": 3,
            "Moderate": 2,
            "Severe": 0
        },
        "historical_data": {
            "dates": ["2023-01", "2023-04", "2023-07"],
            "glucose_values": [95, 98, 105],
            "cholesterol_values": [190, 205, 220]
        }
    }


    # Create report
    try:
        report_generator = HealthReportGenerator()
        pdf_content = report_generator.create_report(
            patient_data=patient_data,
            lab_results=lab_results,
            interpretation=interpretation,
            structured_data=structured_data
        )
       
        # Save PDF
        if pdf_content:
            output_file = f"health_report_{patient_data['id']}_{datetime.now().strftime('%Y%m%d')}.pdf"
            with open(output_file, "wb") as f:
                f.write(pdf_content)
            print(f"Report generated successfully: {output_file}")
        else:
            print("Failed to generate report: No content generated")
           
    except Exception as e:
        print(f"Error generating report: {str(e)}")


if __name__ == "__main__":
    main()
