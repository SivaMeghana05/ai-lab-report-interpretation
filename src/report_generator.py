# Enhanced report generator to create comprehensive health reports
# with proper error handling and fallback content

import logging
import traceback
import re
from io import BytesIO
import pandas as pd
import numpy as np
from datetime import datetime
import fitz  # PyMuPDF
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle, StyleSheet1
from reportlab.lib.colors import HexColor, Color
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    Image, Flowable, Frame, PageTemplate, NextPageTemplate, KeepTogether
)
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Circle, Wedge, String, Rect
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import json

# Set up logging
logger = logging.getLogger("HealthLensAI.PremiumReportGenerator")

class HealthReportGenerator:
    """Enhanced health report generator for comprehensive medical reports"""
    
    def __init__(self):
        """Initialize the report generator with styles and colors"""
        self.styles = getSampleStyleSheet()
        
        # Define colors
        self.reportlab_colors = {
            'primary': HexColor('#2c3e50'),
            'secondary': HexColor('#34495e'),
            'text_dark': HexColor('#2c3c50'),
            'text_light': HexColor('#ffffff'),
            'border': HexColor('#bdc3c7'),
            'light_bg': HexColor('#ecf0f1'),
            'warning': HexColor('#e74c3c'),
            'success': HexColor('#2ecc71'),
            'chart1': HexColor('#3498db'),
            'chart2': HexColor('#2ecc71'),
            'chart3': HexColor('#f1c40f'),
            'chart4': HexColor('#e74c3c'),
            'chart5': HexColor('#9b59b6')
        }
        
        # Define fonts
        self.fonts = {
            'heading': 'Helvetica-Bold',
            'body': 'Helvetica'
        }
        
        # Configure matplotlib to use a style that works
        try:
            plt.style.use('default')
        except Exception as e:
            logger.warning(f"Could not set matplotlib style: {str(e)}")
        
        # Instead of adding new styles, modify existing ones or use unique names
        # Modify existing Title style
        self.styles['Title'].fontSize = 24
        self.styles['Title'].leading = 28
        self.styles['Title'].alignment = TA_CENTER
        self.styles['Title'].spaceAfter = 12
        
        # Modify existing Normal style
        self.styles['Normal'].spaceBefore = 6
        self.styles['Normal'].spaceAfter = 6
        
        # Add custom styles with unique names
        self.styles.add(ParagraphStyle(
            name='ReportSubtitle',  # Changed from 'Subtitle'
            fontName='Helvetica-Bold',
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            spaceAfter=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='ReportSectionTitle',  # Changed from 'SectionTitle'
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            spaceBefore=12,
            spaceAfter=6
        ))
        
        self.styles.add(ParagraphStyle(
            name='ReportBullet',  # Changed from 'Bullet'
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            leftIndent=20,
            bulletIndent=10,
            spaceBefore=2,
            spaceAfter=2
        ))
        
        self.styles.add(ParagraphStyle(
            name='ReportTableHeader',  # Changed from 'TableHeader'
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=12,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='ReportTableCell',  # Changed from 'TableCell'
            fontName='Helvetica',
            fontSize=9,
            leading=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='ReportCaption',  # Changed from 'Caption'
            fontName='Helvetica-Oblique',
            fontSize=8,
            leading=10,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='ReportFooter',  # Changed from 'Footer'
            fontName='Helvetica',
            fontSize=8,
            leading=10,
            alignment=TA_CENTER
        ))

    def create_pdf_report(self, patient_data, structured_data=None, interpretation=None, visualization_service=None):
        """Create a comprehensive health report PDF"""
        try:
        buffer = BytesIO()
        
            # Create document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch,
            title=f"Health Report - {patient_data.get('Name', 'Patient')}",
                author="HealthLensAI",
            subject="Medical Lab Report Analysis",
            keywords="health, medical, lab, report, analysis"
        )
        
            # Create page templates with headers and footers
            def header_footer(canvas, doc):
                canvas.saveState()
                # Header
                header_text = f"Health Report - {patient_data.get('Name', 'Patient')}"
                canvas.setFont('Helvetica-Bold', 10)
                canvas.setFillColor(self.reportlab_colors['primary'])
                canvas.drawString(doc.leftMargin, doc.height + doc.topMargin - 0.25*inch, header_text)
                canvas.setStrokeColor(self.reportlab_colors['primary'])
                canvas.line(doc.leftMargin, doc.height + doc.topMargin - 0.3*inch, 
                          doc.width + doc.leftMargin, doc.height + doc.topMargin - 0.3*inch)
                
                # Footer
                footer_text = f"Page {doc.page} | Generated on {datetime.now().strftime('%Y-%m-%d')}"
                canvas.setFont('Helvetica', 8)
                canvas.setFillColor(self.reportlab_colors['text_dark'])
                canvas.drawString(doc.leftMargin, 0.5*inch, footer_text)
                canvas.setStrokeColor(self.reportlab_colors['border'])
                canvas.line(doc.leftMargin, 0.7*inch, doc.width + doc.leftMargin, 0.7*inch)
                
                canvas.restoreState()
            
        # Create page templates
            frame = Frame(
                doc.leftMargin, 
                doc.bottomMargin, 
                doc.width, 
                doc.height,
                id='normal'
            )
            
            template = PageTemplate(
                id='standard',
                frames=[frame],
                onPage=header_footer
            )
            
            doc.addPageTemplates([template])
        
        # Initialize content
        content = []
        
        # Add cover page
        content.extend(self._create_cover_page(patient_data))
        content.append(PageBreak())
        
        # Add table of contents
        content.extend(self._create_table_of_contents())
        content.append(PageBreak())
        
            # Add doctor summary
            content.extend(self._create_doctor_summary(patient_data, structured_data))
            content.append(PageBreak())
        
            # Add wellbeing index
            content.extend(self._create_wellbeing_index(patient_data))
            content.append(PageBreak())
        
            # Add important parameters
            content.extend(self._create_important_parameters(structured_data))
            
            # Add detailed analysis if interpretation is available
        if interpretation:
                try:
                    content.extend(self._create_executive_summary(interpretation))
                except Exception as e:
                    logger.error(f"Error creating executive summary: {str(e)}")
                    content.extend(self._create_fallback_analysis(structured_data))
            else:
                content.extend(self._create_fallback_analysis(structured_data))
            
            # Add health recommendations
            content.extend(self._create_health_recommendations(structured_data))
            
            # Add educational content
            content.extend(self._create_educational_content())
            
            # Add references
            content.extend(self._create_references())
            
            # Build the document
            doc.build(content)
            pdf_content = buffer.getvalue()
            buffer.close()
            return pdf_content
            
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}\n{traceback.format_exc()}")
            return self._create_error_pdf(patient_data, str(e))
    
    def _create_error_pdf(self, patient_data, error_message):
        """Create a simple error PDF when the main report generation fails"""
        try:
            buffer = BytesIO()
            
            # Create a simple document
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=0.5*inch,
                leftMargin=0.5*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch,
                title="Error Report"
            )
            
            # Create simple content
            content = []
            
            # Add title
            title = Paragraph("Error Generating Health Report", self.styles['Title'])
            content.append(title)
            content.append(Spacer(1, 0.5*inch))
            
            # Add patient info
            patient_info = Paragraph(f"Patient: {patient_data.get('Name', 'Unknown')}", self.styles['Normal'])
            content.append(patient_info)
            content.append(Spacer(1, 0.2*inch))
            
            # Add error message
            error_title = Paragraph("Error Details:", self.styles['ReportSectionTitle'])
            content.append(error_title)
            content.append(Spacer(1, 0.1*inch))
            
            error_text = Paragraph(f"An error occurred while generating the report: {error_message}", self.styles['Normal'])
            content.append(error_text)
            content.append(Spacer(1, 0.2*inch))
            
            # Add recommendation
            recommendation = Paragraph(
                "Please try again or contact support if the issue persists. "
                "Your health data is still available and can be analyzed by your healthcare provider.",
                self.styles['Normal']
            )
            content.append(recommendation)
            
            # Build the document
            doc.build(content)
            pdf_content = buffer.getvalue()
            buffer.close()
            return pdf_content
            
        except Exception as e:
            logger.error(f"Error creating error PDF: {str(e)}")
            # If even the error PDF fails, return a simple PDF with minimal content
            return self._create_minimal_pdf()
    
    def _create_minimal_pdf(self):
        """Create a minimal PDF when all else fails"""
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(1*inch, 9*inch, "Error Generating Health Report")
        c.setFont("Helvetica", 12)
        c.drawString(1*inch, 8*inch, "An unexpected error occurred while generating your health report.")
        c.drawString(1*inch, 7.5*inch, "Please try again or contact support.")
        c.save()
        pdf_content = buffer.getvalue()
        buffer.close()
        return pdf_content
    
    def _create_cover_page(self, patient_data):
        """Create the cover page of the report"""
        content = []
        
        # Add report title
        title = Paragraph("PERSONAL HEALTH<br/>SMART REPORT", self.styles['Title'])
        content.append(title)
        content.append(Spacer(1, 0.2*inch))
        
        # Add subtitle
        subtitle = Paragraph("A comprehensive analysis of your health using<br/>Blood, Physicals, and Health Questionnaire data", 
                           self.styles['ReportSubtitle'])
        content.append(subtitle)
        content.append(Spacer(1, 0.5*inch))
        
        # Add patient information
        patient_info = [
            ["Prepared for", "Basic Info", "Patient ID"],
            [f"{patient_data.get('Name', 'Patient')}", 
             f"{patient_data.get('Gender', '')} / {patient_data.get('Age', '')} Yrs", 
             f"{patient_data.get('Patient ID', '')}"],
            ["Report released on", "Date of Test", ""],
            [f"{datetime.now().strftime('%d/%m/%Y')}", 
             f"{patient_data.get('Test Date', datetime.now().strftime('%d/%m/%Y'))}", ""]
        ]
        
        patient_table = Table(patient_info, colWidths=[2*inch, 2*inch, 2*inch])
        patient_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), self.fonts['heading']),
            ('FONTNAME', (0, 2), (-1, 2), self.fonts['heading']),
            ('FONTNAME', (0, 1), (-1, 1), self.fonts['body']),
            ('FONTNAME', (0, 3), (-1, 3), self.fonts['body']),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 2), (-1, 2), 12),
            ('FONTSIZE', (0, 1), (-1, 1), 14),
            ('FONTSIZE', (0, 3), (-1, 3), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 2), (-1, 2), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 2), (-1, 2), 12),
        ]))
        
        content.append(patient_table)
        content.append(Spacer(1, 1*inch))
        
        # Add patient ID and collection date at bottom
        id_date = [
            ["Patient ID", "Date of Collection"],
            [f"{patient_data.get('Patient ID', '')}", f"{patient_data.get('Collection Date', datetime.now().strftime('%d/%m/%y'))}"]
        ]
        
        id_date_table = Table(id_date, colWidths=[3*inch, 3*inch])
        id_date_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), self.fonts['heading']),
            ('FONTNAME', (0, 1), (-1, 1), self.fonts['body']),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, 1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
        ]))
        
        content.append(id_date_table)
        
        return content
    
    def _create_table_of_contents(self):
        """Create table of contents for the report"""
        content = []
        
        # Add section title
        title = Paragraph("Table of contents", self.styles['ReportSectionTitle'])
        content.append(title)
        content.append(Spacer(1, 0.1*inch))
        
        # Add description
        description = Paragraph("Your smart report includes the following sections.", self.styles['Normal'])
        content.append(description)
        content.append(Spacer(1, 0.2*inch))
        
        # Create TOC table
        toc_data = [
            ["S. No.", "Section", "Page No"],
            ["01", "Summary for Doctors", "03"],
            ["02", "Your Wellbeing Index", "06"],
            ["03", "Glance of Important Parameters", "07"],
            ["04", "Wellness Recommendations", "12"],
            ["05", "References", "13"],
            ["06", "Lab Report", ""]
        ]
        
        toc_table = Table(toc_data, colWidths=[0.7*inch, 4*inch, 1*inch])
        toc_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), self.fonts['heading']),
            ('FONTNAME', (0, 1), (-1, -1), self.fonts['body']),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, self.reportlab_colors['border']),
        ]))
        
        content.append(toc_table)
        content.append(Spacer(1, 0.3*inch))
        
        # Add disclaimer
        disclaimer_title = Paragraph("Disclaimer", self.styles['ReportSectionTitle'])
        content.append(disclaimer_title)
        content.append(Spacer(1, 0.1*inch))
        
        disclaimer_items = [
            "• This is an electronically generated report and is not a substitute for medical advice.",
            "• While following the recommendations, please be careful of any allergies or intolerances.",
            "• If you are pregnant or lactating, some of the recommendations and analyzed information in the Smart Report may not directly apply to you. Please consult a doctor regarding your test results and recommendations.",
            "• Analysis uses the attached blood test report and Well Being Index Questionnaire data, if present, and urine analysis report, if present.",
            "• HealthLensAI is not liable for any direct, indirect, special, consequential, or other damages. This report cannot be used for any medico-legal purposes. Partial reproduction of the test results is not permitted. Also, HealthLensAI is not responsible for any misinterpretation or misuse of the information."
        ]
        
        for item in disclaimer_items:
            disclaimer = Paragraph(item, self.styles['Normal'])
            content.append(disclaimer)
            content.append(Spacer(1, 0.05*inch))
        
        return content
    
    def _create_doctor_summary(self, patient_data, structured_data):
        """Create summary section for doctors"""
        content = []
        
        # Add section header
        header = [
            ["Patient ID", "Date of Collection"],
            [f"{patient_data.get('Patient ID', '')}", f"{patient_data.get('Collection Date', datetime.now().strftime('%d/%m/%y'))}"]
        ]
        
        header_table = Table(header, colWidths=[3*inch, 3*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), self.fonts['heading']),
            ('FONTNAME', (0, 1), (-1, 1), self.fonts['body']),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, 1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
        ]))
        
        content.append(header_table)
        content.append(Spacer(1, 0.2*inch))
        
        # Add doctor summary title
        title = Paragraph(f"Doctor Summary For<br/>{patient_data.get('Name', 'Patient')}<br/>{patient_data.get('Gender', '')} /{patient_data.get('Age', '')} Yrs", self.styles['ReportSectionTitle'])
        content.append(title)
        content.append(Spacer(1, 0.1*inch))
        
        # Add test name
        test_name = Paragraph("Comprehensive Health Checkup with Smart Report", self.styles['Normal'])
        content.append(test_name)
        content.append(Spacer(1, 0.1*inch))
        
        # Add note
        note = Paragraph("Note: This is an electronically generated summary of the attached report. It is advised to read this summary in conjunction with the attached report and to correlate it clinically. For the trends section, the out of range values are highlighted with respect to the bio reference range of respective reports.", self.styles['Normal'])
        content.append(note)
        content.append(Spacer(1, 0.2*inch))
        
        # Create summary table
        if structured_data:
            # Group results by category
            categories = self._group_results_by_category(structured_data)
            
            for category, tests in categories.items():
                # Add category header
                category_title = Paragraph(category, self.styles['ReportSectionTitle'])
                content.append(category_title)
                content.append(Spacer(1, 0.1*inch))
                
                # Create table for this category
                table_data = [["Test Name", "Result", "Bio. Ref. Interval", "Trends (For last three tests)"]]
                
                for test in tests:
                    row = [
                        test.get('Test', ''),
                        f"{test.get('Value', '')}",
                        test.get('ReferenceRange', ''),
                        "--- --- ---"  # Placeholder for trends
                    ]
                    table_data.append(row)
                
                table = Table(table_data, colWidths=[2*inch, 1*inch, 1.5*inch, 2*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), self.reportlab_colors['primary']),
                    ('TEXTCOLOR', (0, 0), (-1, 0), self.reportlab_colors['text_light']),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), self.fonts['heading']),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('GRID', (0, 0), (-1, -1), 0.5, self.reportlab_colors['border']),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTNAME', (0, 1), (-1, -1), self.fonts['body']),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('TOPPADDING', (0, 1), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
                ]))
                
                content.append(table)
                content.append(Spacer(1, 0.2*inch))
        else:
            # Fallback if no lab results
            no_results = Paragraph("No laboratory results available for summary.", self.styles['Normal'])
            content.append(no_results)
        
        return content
    
    def _create_wellbeing_index(self, patient_data):
        """Create wellbeing index section"""
        content = []
        
        # Add section header
        header = [
            ["Patient ID", "Date of Collection"],
            [f"{patient_data.get('Patient ID', '')}", f"{patient_data.get('Collection Date', datetime.now().strftime('%d/%m/%y'))}"]
        ]
        
        header_table = Table(header, colWidths=[3*inch, 3*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), self.fonts['heading']),
            ('FONTNAME', (0, 1), (-1, 1), self.fonts['body']),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, 1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
        ]))
        
        content.append(header_table)
        content.append(Spacer(1, 0.2*inch))
        
        # Add wellbeing index title
        title = Paragraph("Wellbeing Index", self.styles['ReportSectionTitle'])
        content.append(title)
        content.append(Spacer(1, 0.1*inch))
        
        # Add subtitle
        subtitle = Paragraph("Important Findings from your Wellbeing Index", self.styles['Normal'])
        content.append(subtitle)
        content.append(Spacer(1, 0.2*inch))
        
        # Create physical measurements section
        physical_title = Paragraph("Physicals", self.styles['ReportSectionTitle'])
        content.append(physical_title)
        content.append(Spacer(1, 0.1*inch))
        
        # Create physical measurements table
        physical_data = [
            ["Height", "Weight", "Waist"],
            ["Data not available", "Data not available", "Data not available"],
            ["BMI", "Heart Age", "BP"],
            ["Data not available", "Data not available", "Data not available"]
        ]
        
        physical_table = Table(physical_data, colWidths=[2*inch, 2*inch, 2*inch])
        physical_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), self.fonts['heading']),
            ('FONTNAME', (0, 2), (-1, 2), self.fonts['heading']),
            ('FONTNAME', (0, 1), (-1, 1), self.fonts['body']),
            ('FONTNAME', (0, 3), (-1, 3), self.fonts['body']),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 2), (-1, 2), 10),
            ('FONTSIZE', (0, 1), (-1, 1), 10),
            ('FONTSIZE', (0, 3), (-1, 3), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 2), (-1, 2), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 2), (-1, 2), 8),
        ]))
        
        content.append(physical_table)
        content.append(Spacer(1, 0.3*inch))
        
        # Create disease risks section
        risks_title = Paragraph("Disease Risks", self.styles['ReportSectionTitle'])
        content.append(risks_title)
        content.append(Spacer(1, 0.1*inch))
        
        # Create disease risks table
        risks_data = [
            ["Diabetes", "Hypertension", "Stroke"],
            ["Survey not taken yet", "Survey not taken yet", "Survey not taken yet"],
            ["CVD", "Depression", "Anxiety"],
            ["Survey not taken yet", "Survey not taken yet", "Survey not taken yet"],
            ["Stress", "", ""],
            ["Survey not taken yet", "", ""]
        ]
        
        risks_table = Table(risks_data, colWidths=[2*inch, 2*inch, 2*inch])
        risks_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), self.fonts['heading']),
            ('FONTNAME', (0, 2), (-1, 2), self.fonts['heading']),
            ('FONTNAME', (0, 4), (-1, 4), self.fonts['heading']),
            ('FONTNAME', (0, 1), (-1, 1), self.fonts['body']),
            ('FONTNAME', (0, 3), (-1, 3), self.fonts['body']),
            ('FONTNAME', (0, 5), (-1, 5), self.fonts['body']),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 2), (-1, 2), 10),
            ('FONTSIZE', (0, 4), (-1, 4), 10),
            ('FONTSIZE', (0, 1), (-1, 1), 10),
            ('FONTSIZE', (0, 3), (-1, 3), 10),
            ('FONTSIZE', (0, 5), (-1, 5), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 2), (-1, 2), 8),
            ('BOTTOMPADDING', (0, 4), (-1, 4), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 2), (-1, 2), 8),
            ('TOPPADDING', (0, 4), (-1, 4), 8),
        ]))
        
        content.append(risks_table)
        content.append(Spacer(1, 0.2*inch))
        
        # Add note about completing wellbeing index
        note = Paragraph("* Embark on a better you by completing the wellbeing index. Here", self.styles['Normal'])
        content.append(note)
        content.append(Spacer(1, 0.3*inch))
        
        # Create lifestyle data section
        lifestyle_title = Paragraph("Lifestyle Data", self.styles['ReportSectionTitle'])
        content.append(lifestyle_title)
        content.append(Spacer(1, 0.1*inch))
        
        # Create lifestyle data table
        lifestyle_data = [
            ["Habits", "Family History"],
            ["Data not available", "Data not available"]
        ]
        
        lifestyle_table = Table(lifestyle_data, colWidths=[3*inch, 3*inch])
        lifestyle_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), self.fonts['heading']),
            ('FONTNAME', (0, 1), (-1, 1), self.fonts['body']),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, 1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
        ]))
        
        content.append(lifestyle_table)
        
        return content
    
    def _create_important_parameters(self, structured_data):
        """Create important parameters section"""
        content = []
        
        # Add section title
        title = Paragraph("Important Parameters", self.styles['ReportSectionTitle'])
        content.append(title)
        content.append(Spacer(1, 0.1*inch))
        
        # Add subtitle
        subtitle = Paragraph("From your Comprehensive Health Checkup with Smart Report", self.styles['Normal'])
        content.append(subtitle)
        content.append(Spacer(1, 0.2*inch))
        
        if structured_data:
            # Group results by category
            categories = self._group_results_by_category(structured_data)
            
            for category, tests in categories.items():
                # Add category header
                category_title = Paragraph(category, self.styles['ReportSectionTitle'])
                content.append(category_title)
            content.append(Spacer(1, 0.1*inch))
            
                # Add category description
                description = self._get_category_description(category)
                category_desc = Paragraph(description, self.styles['Normal'])
                content.append(category_desc)
                content.append(Spacer(1, 0.2*inch))
                
                # Create parameter boxes for this category
                for test in tests:
                    param_box = self._create_parameter_box(test)
                    content.append(param_box)
            content.append(Spacer(1, 0.1*inch))
            
            content.append(Spacer(1, 0.2*inch))
                else:
            # Fallback if no lab results
            no_results = Paragraph("No laboratory results available for analysis.", self.styles['Normal'])
            content.append(no_results)
        
        return content
    
    def _create_parameter_box(self, test):
        """Create a box for displaying a single parameter"""
        # Create a table with parameter name, value, and reference range
        data = [
            [test.get('Test', '')],
            [f"{test.get('Value', '')}"],
            [f"Range: {test.get('ReferenceRange', '')}"]
        ]
        
        # Determine color based on whether value is in range
        bg_color = self.reportlab_colors['light_bg']
        if test.get('Status', '') != 'Normal':
            bg_color = self.reportlab_colors['warning']
        
        table = Table(data, colWidths=[2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), self.reportlab_colors['primary']),
            ('BACKGROUND', (0, 1), (0, 1), bg_color),
            ('TEXTCOLOR', (0, 0), (0, 0), self.reportlab_colors['text_light']),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (0, 0), self.fonts['heading']),
            ('FONTNAME', (0, 1), (0, -1), self.fonts['body']),
            ('FONTSIZE', (0, 0), (0, 0), 10),
            ('FONTSIZE', (0, 1), (0, 1), 12),
            ('FONTSIZE', (0, 2), (0, 2), 9),
            ('BOTTOMPADDING', (0, 0), (0, -1), 6),
            ('TOPPADDING', (0, 0), (0, -1), 6),
            ('BOX', (0, 0), (0, -1), 1, self.reportlab_colors['border']),
        ]))
        
        return table
    
    def _create_executive_summary(self, interpretation):
        """Create executive summary section based on AI interpretation"""
        content = []
        
        # Add section title
        title = Paragraph("Detailed Analysis", self.styles['ReportSectionTitle'])
        content.append(title)
        content.append(Spacer(1, 0.1*inch))
        
        # Process interpretation text
        if interpretation:
            # Split interpretation into sections
            try:
                # Handle different types of interpretation objects
                if hasattr(interpretation, 'text'):
                    interpretation_text = interpretation.text
                elif hasattr(interpretation, 'parts'):
                    interpretation_text = ''.join([part.text for part in interpretation.parts])
                else:
                    interpretation_text = str(interpretation)
                
                sections = interpretation_text.split('\n\n')
                for section in sections:
                    if section.strip():
                        para = Paragraph(section, self.styles['Normal'])
                        content.append(para)
                content.append(Spacer(1, 0.1*inch))
            except Exception as e:
                logger.error(f"Error processing interpretation: {str(e)}")
                fallback = Paragraph("Detailed analysis not available. Please consult with your healthcare provider to interpret your test results.", 
                                   self.styles['Normal'])
                content.append(fallback)
        else:
            # Fallback if no interpretation
            fallback = Paragraph("Detailed analysis not available. Please consult with your healthcare provider to interpret your test results.", 
                               self.styles['Normal'])
            content.append(fallback)
        
        content.append(PageBreak())
        return content

    def _create_fallback_analysis(self, structured_data):
        """Create fallback analysis when no AI interpretation is available"""
        content = []
        
        # Add section title
        title = Paragraph("Test Results Analysis", self.styles['ReportSectionTitle'])
        content.append(title)
                    content.append(Spacer(1, 0.1*inch))
                    
        # Add introduction
        intro = Paragraph(
            "The following analysis is based on your laboratory test results. "
            "This is a general overview and should be discussed with your healthcare provider for a complete interpretation.",
            self.styles['Normal']
        )
        content.append(intro)
                    content.append(Spacer(1, 0.2*inch))
                
        if structured_data:
            # Find abnormal results
            abnormal_results = [test for test in structured_data if test.get('Status', '') != 'Normal']
            
            if abnormal_results:
                abnormal_title = Paragraph("Abnormal Test Results", self.styles['ReportSectionTitle'])
                content.append(abnormal_title)
            content.append(Spacer(1, 0.1*inch))
            
                for test in abnormal_results:
                    test_name = Paragraph(f"<b>{test.get('Test', '')}</b>: {test.get('Value', '')}", 
                                        self.styles['Normal'])
                    content.append(test_name)
                    
                    reference = Paragraph(f"Reference Range: {test.get('ReferenceRange', '')}", self.styles['Normal'])
                    content.append(reference)
                    
                    # Add generic interpretation based on test name
                    interpretation = self._get_generic_interpretation(test.get('Test', ''))
                    if interpretation:
                        interp_para = Paragraph(interpretation, self.styles['Normal'])
                        content.append(interp_para)
                    
                content.append(Spacer(1, 0.1*inch))
            else:
                normal_note = Paragraph(
                    "All test results appear to be within normal reference ranges. "
                    "This suggests that the measured parameters are currently within expected values.",
                    self.styles['Normal']
                )
                content.append(normal_note)
        else:
            # Fallback if no lab results
            no_results = Paragraph("No laboratory results available for analysis.", self.styles['Normal'])
            content.append(no_results)
        
        content.append(PageBreak())
        return content
    
    def _create_health_recommendations(self, structured_data):
        """Create health recommendations section"""
        content = []
        
        # Add section title
        title = Paragraph("Wellness Recommendations", self.styles['ReportSectionTitle'])
        content.append(title)
        content.append(Spacer(1, 0.1*inch))
        
        # Add subtitle
        subtitle = Paragraph("Care for better health and wellbeing", self.styles['Normal'])
        content.append(subtitle)
        content.append(Spacer(1, 0.2*inch))
        
        # Create lifestyle recommendations
        lifestyle_title = Paragraph("Lifestyle", self.styles['ReportSectionTitle'])
        content.append(lifestyle_title)
        content.append(Spacer(1, 0.1*inch))
        
        # Create healthy eating section
        eating_title = Paragraph("Healthy eating", self.styles['ReportSectionTitle'])
        content.append(eating_title)
        content.append(Spacer(1, 0.1*inch))
        
        # Create dos and don'ts table
        dos_donts = [
            ["Do's", "Dont's"],
            [
                Paragraph("<b>Take Your Time Eating</b><br/>Eat slowly and savor each bite to promote fullness and prevent overeating.", self.styles['Normal']),
                ""
            ],
            [
                Paragraph("<b>Listen To Your Body</b><br/>Stop eating when you feel full and avoid emptying your plate.", self.styles['Normal']),
                ""
            ]
        ]
        
        dos_donts_table = Table(dos_donts, colWidths=[3*inch, 3*inch])
        dos_donts_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), self.fonts['heading']),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        content.append(dos_donts_table)
        content.append(Spacer(1, 0.2*inch))
        
        # Create sleep hygiene section
        sleep_title = Paragraph("Sleep hygiene", self.styles['ReportSectionTitle'])
        content.append(sleep_title)
                content.append(Spacer(1, 0.1*inch))
            
        # Create sleep dos table
        sleep_dos = [
            ["Do's"],
            [
                Paragraph("<b>Identify Your Triggers</b><br/>Identify your triggers for sleeplessness and try to avoid them", self.styles['Normal'])
            ],
            [
                Paragraph("<b>Keep The Sleep Environment Quiet And Dark</b><br/>Minimize noise and light exposure during sleep. Use white noise, earplugs, blackout shades, or an eye mask to promote restful sleep.", self.styles['Normal'])
            ]
        ]
        
        sleep_dos_table = Table(sleep_dos, colWidths=[6*inch])
        sleep_dos_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), self.fonts['heading']),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        content.append(sleep_dos_table)
                content.append(Spacer(1, 0.2*inch))
        
        # Create exercise section
        exercise_title = Paragraph("Exercise", self.styles['ReportSectionTitle'])
        content.append(exercise_title)
            content.append(Spacer(1, 0.1*inch))
            
        # Create exercise dos table
        exercise_dos = [
            ["Do's"],
            [
                Paragraph("<b>Even 5 Minutes Of Exercise Has Real Health Benefits.</b><br/>Guidelines recommend 150-300 minutes of moderate-intensity activity per week for substantial health benefits, with even 5 minutes having real benefits.", self.styles['Normal'])
            ],
            [
                Paragraph("<b>Park Farther Away</b><br/>Park farther and walk to promote physical activity, but prioritize safety.", self.styles['Normal'])
            ]
        ]
        
        exercise_dos_table = Table(exercise_dos, colWidths=[6*inch])
        exercise_dos_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), self.fonts['heading']),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        content.append(exercise_dos_table)
        content.append(Spacer(1, 0.2*inch))
        
        # Add specific recommendations based on abnormal results
        if structured_data:
            abnormal_results = [test for test in structured_data if test.get('Status', '') != 'Normal']
            
            if abnormal_results:
                specific_title = Paragraph("Specific Recommendations Based on Your Results", self.styles['ReportSectionTitle'])
                content.append(specific_title)
                content.append(Spacer(1, 0.1*inch))
        
                for test in abnormal_results:
                    recommendations = self._get_specific_recommendations(test.get('Test', ''))
                    if recommendations:
                        test_name = Paragraph(f"<b>{test.get('Test', '')}</b>", self.styles['Normal'])
                        content.append(test_name)
                        
                        for rec in recommendations:
                            rec_para = Paragraph(f"• {rec}", self.styles['Normal'])
                            content.append(rec_para)
                        
                        content.append(Spacer(1, 0.1*inch))
        
        content.append(PageBreak())
        return content
    
    def _create_educational_content(self):
        """Create educational content section"""
        content = []
        
        # Add section title
        title = Paragraph("Educational Content", self.styles['ReportSectionTitle'])
        content.append(title)
        content.append(Spacer(1, 0.1*inch))
        
        # Add introduction
        intro = Paragraph(
            "This section provides educational information about common health topics related to your test results. "
            "Understanding these concepts can help you make informed decisions about your health.",
            self.styles['Normal']
        )
        content.append(intro)
        content.append(Spacer(1, 0.2*inch))
        
        # Add educational topics
        topics = [
            {
                "title": "Understanding Blood Sugar",
                "content": "Blood glucose (sugar) is a primary source of energy for your body's cells. Your body creates glucose from the food you eat. The hormone insulin helps your body's cells use glucose. Blood sugar levels that are too high (hyperglycemia) or too low (hypoglycemia) can cause health problems. Diabetes is a disease that occurs when your blood sugar is too high because your body doesn't make enough insulin or doesn't use insulin properly."
            },
            {
                "title": "Cholesterol and Heart Health",
                "content": "Cholesterol is a waxy, fat-like substance found in all cells of the body. Your liver makes all the cholesterol your body needs to form cell membranes and produce certain hormones. High-density lipoprotein (HDL) is known as 'good' cholesterol because it helps remove other forms of cholesterol from your bloodstream. Low-density lipoprotein (LDL) is known as 'bad' cholesterol because it can build up in the walls of your arteries and increase your risk for heart disease."
            },
            {
                "title": "The Importance of Vitamins and Minerals",
                "content": "Vitamins and minerals are essential nutrients that your body needs in small amounts to work properly. They play crucial roles in many bodily functions, including energy production, immune function, blood clotting, and bone health. Most vitamins need to come from food because the body either doesn't produce them or produces very little. Minerals are inorganic elements that originate in the earth and cannot be made by living organisms."
            }
        ]
        
        for topic in topics:
            topic_title = Paragraph(topic["title"], self.styles['ReportSectionTitle'])
            content.append(topic_title)
            content.append(Spacer(1, 0.1*inch))
            
            topic_content = Paragraph(topic["content"], self.styles['Normal'])
            content.append(topic_content)
            content.append(Spacer(1, 0.2*inch))
        
        content.append(PageBreak())
        return content

    def _create_references(self):
        """Create references section"""
        content = []
        
        # Add section title
        title = Paragraph("References", self.styles['ReportSectionTitle'])
        content.append(title)
        content.append(Spacer(1, 0.1*inch))
        
        # Add subtitle
        subtitle = Paragraph("From trusted sources", self.styles['Normal'])
        content.append(subtitle)
        content.append(Spacer(1, 0.2*inch))
        
        # Add references
        references = [
            "01 Estimation of 10-year Cardiovascular Disease (CVD) Risk<br/>D'Agostino RB Sr, et al. General cardiovascular risk profile for use in primary care: the Framingham Heart Study.Circulation. 2008 Feb 12;117(6):743-53",
            "02 Framingham Heart Study: Hypertension Risk<br/>Parikh NI, et al. A risk score for predicting near-term incidence of hypertension: the Framingham Heart Study.Ann Intern Med. 2008;148(2):102-110.",
            "03 Framningham Heart Study. Stroke Risk<br/>D'Agostino RB, et al. Stroke risk profile: adjustment for antihypertensive medication. The Framingham Study. Stroke. 1994;25(1):40-3.",
            "04 Depression: Patient Health Questionnaire-2 (PHQ-2)<br/>Kroenke K, et al. The Patient Health Questionnaire-2: validity of a two-item depression screener.Med Care. 2003;41(11):1284-1292.",
            "05 Anxiety: Generalized Anxiety Disorder 2-item (GAD-2)<br/>Kroenke K, et al. Anxiety disorders in primary care: prevalence, impairment, comorbidity, and detection.Ann Intern Med. 2007;146(5):317-325.",
            "06 Anxiety: Generalized Anxiety Disorder 7-item (GAD-7)<br/>Spitzer RL, et al. A brief measure for assessing generalized anxiety disorder: the GAD-7.Arch Intern Med. 2006;166:1092-7.",
            "07 Indian Diabetes Risk Score [IDRS]<br/>Mohan V, et al. A simplified Indian Diabetes Risk Score for screening for undiagnosed diabetic subjects. J Assoc Physicians India. 2005;53:759-763.",
            "08 Dietary Guidelines for Indians<br/>Dietary Guidelines for Indians - A Manual, Second Edition, 2011.ICMR-National Institute of Nutrition, Hyderabad.",
            "09 My plate for the day<br/>R. Hemalatha. Promotionof 'My Plate for the Day' and physical activity among the population to prevent all forms of malnutrition and NCDs in the country, 2023.ICMR-National Institute of Nutrition, Hyderabad.",
            "10 Healthy Eating Plate<br/>Building a Healthy and Balanced DietThe Nutrition Source, Department of Nutrition, Harvard T.H. Chan School of Public Health."
        ]
        
        for ref in references:
            ref_para = Paragraph(ref, self.styles['Normal'])
            content.append(ref_para)
        content.append(Spacer(1, 0.1*inch))
        
        # Add end of report marker
        content.append(Spacer(1, 0.5*inch))
        end_marker = Paragraph("***End of Smart Report***", self.styles['Normal'])
        content.append(end_marker)
        
        return content
    
    def _group_results_by_category(self, structured_data):
        """Group lab results by category"""
        categories = {
            "Complete Blood Count": [],
            "Inflammatory markers": [],
            "Iron Studies": [],
            "Diabetes Profile": [],
            "Kidney Function Test": [],
            "Lipid Profile": [],
            "Liver Function Test": [],
            "Urine Routine & Microscopy": [],
            "Calcium and Bone Health": [],
            "Vitamin Profile": [],
            "Thyroid Function Test": [],
            "Other Tests": []
        }
        
        # Map test names to categories
        category_mapping = {
            "Hemoglobin": "Complete Blood Count",
            "RBC": "Complete Blood Count",
            "WBC": "Complete Blood Count",
            "Platelets": "Complete Blood Count",
            "Erythrocyte Sedimentation Rate": "Inflammatory markers",
            "C-Reactive Protein": "Inflammatory markers",
            "Iron": "Iron Studies",
            "Ferritin": "Iron Studies",
            "Transferrin": "Iron Studies",
            "Glucose": "Diabetes Profile",
            "HbA1c": "Diabetes Profile",
            "Creatinine": "Kidney Function Test",
            "BUN": "Kidney Function Test",
            "eGFR": "Kidney Function Test",
            "Sodium": "Kidney Function Test",
            "Potassium": "Kidney Function Test",
            "Cholesterol": "Lipid Profile",
            "Triglycerides": "Lipid Profile",
            "HDL": "Lipid Profile",
            "LDL": "Lipid Profile",
            "AST": "Liver Function Test",
            "ALT": "Liver Function Test",
            "Bilirubin": "Liver Function Test",
            "Alkaline Phosphatase": "Liver Function Test",
            "Calcium": "Calcium and Bone Health",
            "Vitamin D": "Vitamin Profile",
            "Vitamin B12": "Vitamin Profile",
            "TSH": "Thyroid Function Test",
            "T3": "Thyroid Function Test",
            "T4": "Thyroid Function Test"
        }
        
        # Categorize each test
        for test in structured_data:
            test_name = test.get('Test', '')
            
            # Find category based on test name
            category = "Other Tests"
            for key, value in category_mapping.items():
                if key.lower() in test_name.lower():
                    category = value
                    break
            
            categories[category].append(test)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}

    def _get_category_description(self, category):
        """Get description for a test category"""
        descriptions = {
            "Complete Blood Count": "Gives an insight into the health of blood and blood cells which are essential to carry out various bodily functions like transporting oxygen, fighting infections, and clotting blood after an injury.",
            "Inflammatory markers": "Helps to understand presence of an inflammation in the body. Inflammation is bodies defence against infection or injury.",
            "Iron Studies": "Iron is a vital mineral. It helps our blood cells to transport oxygen. Iron studies are used to assess level of iron in blood and blood's ability to attach itself to iron.",
            "Diabetes Profile": "Measures the level of glucose in the body and helps identify the body's ability to process glucose. It can be used for screnning as well as monitoring the treatment of diabetes.",
            "Kidney Function Test": "Performed to determine how well the kidneys are working. Kidneys regulate elimination of waste from our body and maintain electrolyte balance.",
            "Lipid Profile": "Measures the amount of Cholesterol and Triglycerides in your blood. This gives an insight into the health of heart and blood vessels.",
            "Liver Function Test": "Group of blood tests commonly performed to evaluate the function of the liver which is essential to digest food and removing toxins from the body.",
            "Urine Routine & Microscopy": "Microscopic examination of urine sample to check for the presence of blood cells, crystals, bacteria, parasites, and cells from tumors in it.",
            "Calcium and Bone Health": "Measures the levels of calcium and vitamin D in the blood which are responsible for keeping bones, teeth, and muscles healthy.",
            "Vitamin Profile": "Vitamins are the essential nutrients for human life. This profile offers tests to check level of different types of vitamin B, vitamin D, vitamin E and vitamin K.",
            "Thyroid Function Test": "Window to the health of the butterfly shaped gland - Thyroid, which detemines how the body uses energy.",
            "Other Tests": "Additional laboratory tests that provide valuable information about your health status."
        }
        
        return descriptions.get(category, "")

    def _get_generic_interpretation(self, test_name):
        """Get generic interpretation for a test"""
        interpretations = {
            "Glucose": "Elevated glucose levels may indicate diabetes or prediabetes. This suggests that your body is having difficulty regulating blood sugar levels.",
            "HbA1c": "HbA1c measures your average blood sugar level over the past 2-3 months. Elevated levels indicate that your blood sugar has been consistently high, which is associated with diabetes.",
            "Cholesterol": "Elevated total cholesterol may increase your risk of heart disease and stroke. It's important to maintain healthy cholesterol levels through diet, exercise, and sometimes medication.",
            "HDL": "HDL is often called 'good' cholesterol. Low levels of HDL cholesterol may increase your risk of heart disease.",
            "LDL": "LDL is often called 'bad' cholesterol. Elevated levels of LDL cholesterol may increase your risk of heart disease and stroke.",
            "Triglycerides": "Elevated triglyceride levels may contribute to hardening of the arteries or thickening of the artery walls, which increases the risk of stroke, heart attack, and heart disease.",
            "Hemoglobin": "Low hemoglobin levels may indicate anemia, which means you don't have enough red blood cells to carry adequate oxygen to your tissues.",
            "Iron": "Low iron levels may lead to iron deficiency anemia. Iron is essential for producing hemoglobin, which carries oxygen in your blood.",
            "Vitamin D": "Low vitamin D levels are common and may affect bone health, immune function, and overall health. Vitamin D is produced when your skin is exposed to sunlight.",
            "TSH": "Abnormal TSH levels may indicate a thyroid disorder. The thyroid gland produces hormones that regulate metabolism.",
            "Creatinine": "Elevated creatinine levels may indicate kidney problems. Creatinine is a waste product that your kidneys filter from your blood."
        }
        
        # Look for partial matches in test name
        for key, value in interpretations.items():
            if key.lower() in test_name.lower():
                return value
        
        return "This test result is outside the reference range. Please consult with your healthcare provider for interpretation."

    def _get_specific_recommendations(self, test_name):
        """Get specific recommendations based on test name"""
        recommendations = {
            "Glucose": [
                "Monitor your blood sugar levels regularly as recommended by your healthcare provider",
                "Follow a balanced diet low in simple sugars and high in fiber",
                "Engage in regular physical activity, aiming for at least 150 minutes of moderate exercise per week",
                "Maintain a healthy weight or work toward weight loss if overweight",
                "Take medications as prescribed by your healthcare provider"
            ],
            "HbA1c": [
                "Work with your healthcare provider to develop a diabetes management plan",
                "Monitor your blood sugar levels regularly",
                "Follow a balanced diet with consistent carbohydrate intake throughout the day",
                "Engage in regular physical activity",
                "Take medications as prescribed"
            ],
            "Cholesterol": [
                "Adopt a heart-healthy diet low in saturated and trans fats",
                "Increase consumption of fruits, vegetables, whole grains, and lean proteins",
                "Engage in regular physical activity",
                "Maintain a healthy weight",
                "Avoid smoking and limit alcohol consumption"
            ],
            "HDL": [
                "Engage in regular aerobic exercise",
                "Quit smoking if applicable",
                "Maintain a healthy weight",
                "Include healthy fats in your diet, such as olive oil, nuts, and avocados",
                "Limit refined carbohydrates and added sugars"
            ],
            "LDL": [
                "Reduce intake of saturated and trans fats",
                "Increase consumption of soluble fiber from sources like oats, beans, and fruits",
                "Consider plant sterols and stanols, which can help lower LDL cholesterol",
                "Engage in regular physical activity",
                "Take medications as prescribed by your healthcare provider"
            ],
            "Triglycerides": [
                "Limit added sugars and refined carbohydrates",
                "Reduce alcohol consumption",
                "Choose omega-3 rich foods like fatty fish",
                "Maintain a healthy weight",
                "Engage in regular physical activity"
            ],
            "Hemoglobin": [
                "Include iron-rich foods in your diet, such as lean meats, beans, and leafy greens",
                "Pair iron-rich foods with vitamin C sources to enhance absorption",
                "Avoid consuming calcium-rich foods or coffee/tea with iron-rich meals",
                "Consider iron supplements if recommended by your healthcare provider",
                "Follow up with your healthcare provider to monitor your hemoglobin levels"
            ],
            "Iron": [
                "Include iron-rich foods in your diet",
                "Consider iron supplements if recommended by your healthcare provider",
                "Pair iron-rich foods with vitamin C sources to enhance absorption",
                "Avoid consuming calcium-rich foods or coffee/tea with iron-rich meals",
                "Follow up with your healthcare provider to monitor your iron levels"
            ],
            "Vitamin D": [
                "Spend time outdoors in sunlight, but avoid sunburn",
                "Include vitamin D-rich foods in your diet, such as fatty fish, egg yolks, and fortified foods",
                "Consider vitamin D supplements if recommended by your healthcare provider",
                "Follow up with your healthcare provider to monitor your vitamin D levels",
                "Be aware that certain medications can affect vitamin D levels"
            ],
            "TSH": [
                "Follow up with your healthcare provider for further evaluation",
                "Take thyroid medications as prescribed, if applicable",
                "Be consistent with the timing of thyroid medication",
                "Inform your healthcare provider of all medications and supplements you are taking",
                "Monitor for symptoms of thyroid dysfunction and report them to your healthcare provider"
            ],
            "Creatinine": [
                "Stay well-hydrated",
                "Follow a kidney-friendly diet if recommended by your healthcare provider",
                "Monitor your blood pressure regularly",
                "Avoid medications that can harm the kidneys, such as certain pain relievers",
                "Follow up with your healthcare provider to monitor your kidney function"
            ]
        }
        
        # Look for partial matches in test name
        for key, value in recommendations.items():
            if key.lower() in test_name.lower():
                return value
        
        return None

    def analyze_lab_report(self, report_text):
        """Analyze lab report text and return structured data and interpretation"""
        try:
            if not (self.primary_model or self.backup_model):
                logger.error("No AI models available for analysis")
                return None, None

            interpretation_prompt = self._prepare_interpretation_prompt(report_text)
            extraction_prompt = self._prepare_extraction_prompt(report_text)
            
            interpretation_response = None
            extraction_response = None
            
            # Try primary model first
            if self.primary_model:
                try:
                    interpretation_response = self.primary_model.generate_content(interpretation_prompt)
                    extraction_response = self.primary_model.generate_content(extraction_prompt)
                except Exception as e:
                    logger.warning(f"Primary model failed: {str(e)}")
            
            # Fall back to backup model if primary failed or not available
            if not (interpretation_response and extraction_response) and self.backup_model:
                try:
                    interpretation_response = self.backup_model.generate_content(interpretation_prompt)
                    extraction_response = self.backup_model.generate_content(extraction_prompt)
                except Exception as e:
                    logger.error(f"Backup model failed: {str(e)}")
            
            if not (interpretation_response and extraction_response):
                logger.error("Failed to generate responses from both models")
                return None, None
            
            try:
                structured_data = json.loads(extraction_response)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse extraction response: {str(e)}")
                return None, interpretation_response
            
            return structured_data, interpretation_response
            
        except Exception as e:
            logger.error(f"Error analyzing lab report: {str(e)}")
            return None, None

    def display_test_results(self, df):
        """Display test results with enhanced interactive UI"""
        try:
            import streamlit as st
            st.markdown("### 🔬 Detailed Test Results")
            
            if 'Category' in df.columns and not df['Category'].empty:
                categories = df['Category'].unique().tolist()
                selected_category = st.selectbox("Filter by Category", ["All Categories"] + categories)
                
                filtered_df = df.copy()
                if selected_category != "All Categories":
                    filtered_df = filtered_df[filtered_df['Category'] == selected_category]
                
                for category in filtered_df['Category'].unique():
                    with st.expander(f"📊 {category} Panel", expanded=True):
                        category_df = filtered_df[filtered_df['Category'] == category]
                        for _, row in category_df.iterrows():
                            with st.container():
                                col1, col2 = st.columns([1, 1])
                                with col1:
                                    st.markdown(f"### {row['Test']}")
                                    value_color = ('🔴' if row['Status'] == 'High' else '🔵' if row['Status'] == 'Low' else '🟢')
                                    st.markdown(f"{value_color} **Current Value:** {row['Value']}")
                                    st.markdown(f"**Normal Range:** {row['ReferenceRange']}")
                                with col2:
                                    if row['Status'] != 'Normal':
                                        severity = row.get('Severity', 'Moderate')
                                        st.markdown(f"**Severity:** {severity}")
                                        st.markdown("**What this means:**")
                                        interpretation = self._get_generic_interpretation(row['Test'])
                                        st.markdown(interpretation)
                                        st.markdown("**Recommendations:**")
                                        recommendations = self._get_specific_recommendations(row['Test'])
                                        st.markdown(recommendations)
                                    else:
                                        st.markdown("✅ **Result is within normal range**")
                                        st.markdown("Continue maintaining your healthy lifestyle and regular check-ups.")
                                    st.markdown("---")
            else:
                st.dataframe(df, use_container_width=True)
        except Exception as e:
            logger.error(f"Error displaying test results: {str(e)}")
            import streamlit as st
            st.warning("Error displaying detailed test results. Showing basic table instead.")
            st.dataframe(df, use_container_width=True)