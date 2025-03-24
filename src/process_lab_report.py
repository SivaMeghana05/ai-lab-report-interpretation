#!/usr/bin/env python3
"""
HealthLensAI Example: Process a medical lab report

This script provides functionality to process medical lab reports using the
EnhancedPDFProcessor, with improved path handling and Windows compatibility.
"""

import os
import logging
from enhanced_pdf_processor import EnhancedPDFProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("HealthLensAI.Example")

def process_lab_report(pdf_path, output_dir="output"):
    """
    Process a lab report PDF and generate analysis
    
    Args:
        pdf_path (str): Path to the PDF file to process
        output_dir (str): Directory to store output files (default: "output")
        
    Returns:
        bool: True if processing was successful, False otherwise
    """
    try:
        # Normalize path (fix Windows backslash issues)
        pdf_path = os.path.normpath(pdf_path)
        
        # Validate input file
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return False
            
        if not pdf_path.lower().endswith('.pdf'):
            logger.error(f"File is not a PDF: {pdf_path}")
            return False
        
        # Initialize processor
        logger.info("Initializing PDF processor...")
        processor = EnhancedPDFProcessor()
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Process the PDF
        logger.info(f"Processing PDF: {pdf_path}")
        result = processor.process_pdf(pdf_path, output_dir)
        
        if result["success"]:
            logger.info("PDF processed successfully!")
            
            # Log additional information if available
            if "stats" in result:
                logger.info("Processing statistics:")
                for key, value in result["stats"].items():
                    logger.info(f"  {key}: {value}")
                    
            if "output_files" in result:
                logger.info("Generated output files:")
                for file_path in result["output_files"]:
                    logger.info(f"  - {file_path}")
            
            return True
        else:
            error_msg = result.get('error', 'Unknown error')
            logger.error(f"PDF processing failed: {error_msg}")
            
            # Log additional error details if available
            if "details" in result:
                logger.error("Error details:")
                for detail in result["details"]:
                    logger.error(f"  - {detail}")
            
            return False
            
    except Exception as e:
        logger.error(f"Error processing lab report: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    # Example usage - use raw string for Windows paths
    pdf_path = r"C:\Users\nsmeg\Downloads\Deepa-24-12-2024.pdf"  # Note the 'r' prefix
    process_lab_report(pdf_path)

    # Custom output directory
    process_lab_report(r"C:\Users\nsmeg\Downloads\Deepa-24-12-2024.pdf", output_dir="custom_output")