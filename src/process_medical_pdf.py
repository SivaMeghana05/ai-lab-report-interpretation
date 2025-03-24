#!/usr/bin/env python3
"""
Medical PDF Processing Script
This script provides functionality to process medical PDF files using the AdvancedPDFProcessor.
It extracts text, analyzes document structure, and identifies abnormal values.
"""

import logging
import io
import os
import sys
from pathlib import Path

# Add parent directory to path to allow imports from sibling modules
sys.path.append(str(Path(__file__).parent))

from pdf_processor import AdvancedPDFProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('medical_pdf_processing.log')
    ]
)

logger = logging.getLogger("MedicalPDFProcessor")

class MedicalPDFProcessor:
    """Wrapper class for processing medical PDFs with enhanced error handling and logging"""
    
    def __init__(self):
        """Initialize the processor with the AdvancedPDFProcessor"""
        try:
            self.processor = AdvancedPDFProcessor()
            logger.info("Medical PDF Processor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Medical PDF Processor: {str(e)}")
            raise

    def process_medical_pdf(self, pdf_path):
        """
        Process a medical PDF file and extract relevant information
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            dict: Document structure containing patient info, test sections, and abnormal flags
            None: If processing fails
        """
        try:
            # Validate file exists
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            # Validate file is a PDF
            if not pdf_path.lower().endswith('.pdf'):
                raise ValueError("File must be a PDF")
            
            logger.info(f"Processing medical PDF: {pdf_path}")
            
            # Open and process the PDF
            with open(pdf_path, 'rb') as pdf_file:
                # Extract text from the PDF
                extracted_text = self.processor.extract_text_from_pdf(pdf_file)
                
                if not extracted_text or extracted_text.startswith("Error"):
                    logger.error(f"Failed to extract text from PDF: {extracted_text}")
                    return None
                
                # Log first 500 characters of extracted text
                preview = extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text
                logger.info("=== EXTRACTED TEXT PREVIEW ===\n%s", preview)
                
                # Analyze document structure
                doc_structure = self.processor.analyze_document_structure(extracted_text)
                
                # Log patient information
                if doc_structure["patient_info"]:
                    logger.info("=== PATIENT INFORMATION ===")
                    for key, value in doc_structure["patient_info"].items():
                        logger.info("%s: %s", key.replace('_', ' ').title(), value)
                
                # Log abnormal flags
                if doc_structure["abnormal_flags"]:
                    logger.info("=== ABNORMAL VALUES ===")
                    for flag in doc_structure["abnormal_flags"]:
                        logger.info(
                            "%s: %s (%s) - Reference: %s",
                            flag['test'],
                            flag['value'],
                            flag['status'],
                            flag['reference']
                        )
                
                return doc_structure
                
        except FileNotFoundError as e:
            logger.error(f"File not found error: {str(e)}")
        except ValueError as e:
            logger.error(f"Value error: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}", exc_info=True)
        
        return None

def main():
    """Main function to demonstrate usage"""
    try:
        # Initialize processor
        processor = MedicalPDFProcessor()
        
        # Get PDF path from command line argument or use default
        pdf_path = sys.argv[1] if len(sys.argv) > 1 else "sample_lab_report.pdf"
        
        logger.info("Starting medical PDF processing...")
        result = processor.process_medical_pdf(pdf_path)
        
        if result:
            logger.info("Processing completed successfully!")
            return 0
        else:
            logger.error("Processing failed.")
            return 1
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 