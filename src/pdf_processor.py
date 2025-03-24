#!/usr/bin/env python3
"""
HealthLensAI: Advanced PDF Processor

This module provides enhanced PDF processing capabilities for medical documents,
including text extraction, image extraction, and layout analysis with special
handling for medical report formatting.
"""

import os
import logging
import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, List, Union, Optional
import io
import re
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("PDFProcessor")

class AdvancedPDFProcessor:
    """Advanced PDF processor for medical documents"""
    
    def __init__(self):
        """Initialize the PDF processor"""
        self.supported_image_types = {
            'jpeg': 'jpg',
            'png': 'png',
            'bmp': 'bmp',
            'tiff': 'tiff'
        }
        
        # Define section patterns
        self.section_patterns = {
            'header': r'Health Report -\s*(.*?)\nPage \d+\s*\|\s*Generated on\s*(.*)',
            'patient_info': r'Patient ID\s*Date of Collection\s*([A-Z0-9]+)\s*(\d{2}/\d{2}/\d{2})',
            'basic_info': r'Basic Info\s*Patient ID\s*(.*?)\s*/\s*(\d+)\s*Yrs\s*([A-Z0-9]+)',
            'toc': r'Table of contents(.*?)Disclaimer',
            'sections': {
                'doctor_summary': r'Doctor Summary For(.*?)Wellbeing Index',
                'wellbeing_index': r'Wellbeing Index(.*?)Important Parameters',
                'important_parameters': r'Important Parameters(.*?)Wellness Recommendations',
                'wellness_recommendations': r'Wellness Recommendations(.*?)References',
                'references': r'References(.*?)End of Smart Report'
            }
        }
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """
        Extract text from a PDF file with enhanced layout preservation
        
        Args:
            pdf_file: File object or path to PDF file
            
        Returns:
            str: Extracted text with preserved layout
        """
        try:
            # Handle both file objects and paths
            if isinstance(pdf_file, (str, Path)):
                pdf_path = str(pdf_file)
            else:
                # If it's a file object, read the content
                pdf_content = pdf_file.read()
                # Create a temporary buffer
                buffer = io.BytesIO(pdf_content)
                pdf_path = buffer
            
            doc = fitz.open(pdf_path)
            text_content = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Extract text with layout preservation
                text = page.get_text("text")
                text_content.append(text)
                
                # Log progress for large documents
                if page_num > 0 and page_num % 10 == 0:
                    logger.info(f"Processed {page_num} pages...")
            
            doc.close()
            
            # Join all pages with proper spacing
            full_text = "\n\n".join(text_content)
            
            if not full_text.strip():
                logger.warning("No text content found in PDF")
                return ""
            
            return full_text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            return f"Error: {str(e)}"
    
    def parse_medical_report(self, text: str) -> Dict:
        """
        Parse medical report text into structured sections
        
        Args:
            text (str): Raw text from the medical report
            
        Returns:
            Dict: Structured report data
        """
        try:
            report_data = {
                'header': {},
                'patient_info': {},
                'sections': {},
                'metadata': {
                    'parsed_at': datetime.now().isoformat()
                }
            }
            
            # Extract header information
            header_match = re.search(self.section_patterns['header'], text, re.DOTALL)
            if header_match:
                report_data['header'] = {
                    'patient_name': header_match.group(1).strip(),
                    'generated_date': header_match.group(2).strip()
                }
            
            # Extract patient information
            patient_info_match = re.search(self.section_patterns['patient_info'], text, re.DOTALL)
            if patient_info_match:
                report_data['patient_info'] = {
                    'patient_id': patient_info_match.group(1).strip(),
                    'collection_date': patient_info_match.group(2).strip()
                }
            
            # Extract basic information
            basic_info_match = re.search(self.section_patterns['basic_info'], text, re.DOTALL)
            if basic_info_match:
                report_data['patient_info'].update({
                    'name': basic_info_match.group(1).strip(),
                    'age': basic_info_match.group(2).strip(),
                    'patient_id': basic_info_match.group(3).strip()
                })
            
            # Extract table of contents
            toc_match = re.search(self.section_patterns['toc'], text, re.DOTALL)
            if toc_match:
                toc_text = toc_match.group(1).strip()
                report_data['toc'] = self._parse_toc(toc_text)
            
            # Extract main sections
            for section_name, pattern in self.section_patterns['sections'].items():
                section_match = re.search(pattern, text, re.DOTALL)
                if section_match:
                    section_content = section_match.group(1).strip()
                    report_data['sections'][section_name] = self._clean_section_text(section_content)
            
            return report_data
            
        except Exception as e:
            logger.error(f"Error parsing medical report: {str(e)}")
            return {}
    
    def _parse_toc(self, toc_text: str) -> List[Dict]:
        """Parse table of contents into structured format"""
        toc_entries = []
        for line in toc_text.split('\n'):
            if line.strip():
                match = re.match(r'(\d+)\s+(.*?)\s+(\d+)', line.strip())
                if match:
                    toc_entries.append({
                        'number': match.group(1),
                        'title': match.group(2).strip(),
                        'page': match.group(3)
                    })
        return toc_entries
    
    def _clean_section_text(self, text: str) -> str:
        """Clean and format section text"""
        # Remove multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Remove trailing/leading whitespace from lines
        text = '\n'.join(line.strip() for line in text.split('\n'))
        return text
    
    def process_pdf(self, pdf_path: str, output_dir: str) -> Dict:
        """
        Process a PDF file and extract all relevant information
        
        Args:
            pdf_path (str): Path to the PDF file
            output_dir (str): Directory to save extracted content
            
        Returns:
            Dict: Processing results and extracted information
        """
        try:
            result = {
                'success': False,
                'text_content': '',
                'structured_data': {},
                'stats': {},
                'error': None
            }
            
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Extract text
            logger.info("Extracting text from PDF...")
            text_content = self.extract_text_from_pdf(pdf_path)
            
            if text_content and not text_content.startswith("Error"):
                # Parse medical report
                logger.info("Parsing medical report structure...")
                structured_data = self.parse_medical_report(text_content)
                result['structured_data'] = structured_data
                
                # Save extracted text
                text_output_path = os.path.join(output_dir, 'extracted_text.txt')
                with open(text_output_path, 'w', encoding='utf-8') as f:
                    f.write(text_content)
                result['text_content'] = text_content
                
                # Save structured data
                json_output_path = os.path.join(output_dir, 'structured_report.json')
                import json
                with open(json_output_path, 'w', encoding='utf-8') as f:
                    json.dump(structured_data, f, indent=2, ensure_ascii=False)
                
                # Add files to output files list
                result['output_files'] = [text_output_path, json_output_path]
                
                # Add basic statistics
                doc = fitz.open(pdf_path)
                result['stats'] = {
                    'total_pages': len(doc),
                    'text_length': len(text_content),
                    'sections_extracted': len(structured_data.get('sections', {}))
                }
                doc.close()
                
                result['success'] = True
                logger.info("PDF processing completed successfully")
            else:
                result['error'] = text_content if text_content.startswith("Error") else "No text extracted"
                result['success'] = False
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error processing PDF: {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'details': [
                    "Failed to process PDF file",
                    f"Error message: {error_msg}",
                    f"PDF path: {pdf_path}"
                ]
            }

def main():
    """Main function to demonstrate usage"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Process medical PDF reports with advanced features',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('input', help='Input PDF file')
    parser.add_argument('--output', '-o', default='output',
                       help='Output directory')
    parser.add_argument('--format', choices=['text', 'json', 'both'],
                       default='both', help='Output format')
    args = parser.parse_args()
    
    try:
        processor = AdvancedPDFProcessor()
        result = processor.process_pdf(args.input, args.output)
        
        if result['success']:
            print("\nProcessing completed successfully!")
            print("\nStatistics:")
            for key, value in result['stats'].items():
                print(f"  {key}: {value}")
            
            if result.get('structured_data'):
                print("\nExtracted Report Structure:")
                print("  Sections:")
                for section in result['structured_data'].get('sections', {}):
                    print(f"    - {section}")
            
            # Access structured data
            structured_data = result['structured_data']
            
            # Print patient info
            print(f"\nPatient: {structured_data['patient_info']['name']}")
            print(f"Age: {structured_data['patient_info']['age']}")
            
            # Access specific sections
            doctor_summary = structured_data['sections']['doctor_summary']
            wellbeing_index = structured_data['sections']['wellbeing_index']
        else:
            print("\nProcessing failed!")
            print(f"\nError: {result['error']}")
            if 'details' in result:
                print("\nError details:")
                for detail in result['details']:
                    print(f"  {detail}")
        
        return 0 if result['success'] else 1
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    exit(main())