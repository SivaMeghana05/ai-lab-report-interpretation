#!/usr/bin/env python3
"""
HealthLensAI: Enhanced OCR Processor

This module provides advanced OCR capabilities for medical documents with
image preprocessing, deskewing, and noise reduction features.
"""

import os
import cv2
import numpy as np
import pytesseract
import logging
import argparse
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("OCRProcessor")

class OCRProcessor:
    """Enhanced OCR processor for medical documents"""
    
    def __init__(self, tesseract_path=None):
        """
        Initialize OCR processor with optional Tesseract path
        
        Args:
            tesseract_path (str, optional): Path to Tesseract executable
        """
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        # Verify Tesseract is available
        try:
            version = pytesseract.get_tesseract_version()
            logger.info(f"Tesseract version: {version}")
        except Exception as e:
            logger.error(f"Tesseract not properly configured: {str(e)}")
            logger.error("Please install Tesseract and ensure it's in your PATH")
            raise
    
    def process_image(self, image_path, output_path=None, preprocess=True):
        """
        Process an image with OCR
        
        Args:
            image_path (str): Path to the image file
            output_path (str, optional): Path to save the extracted text
            preprocess (bool): Whether to preprocess the image for better OCR
            
        Returns:
            str: Extracted text
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            # Preprocess image if requested
            if preprocess:
                processed_image = self._preprocess_image(image)
            else:
                processed_image = image
            
            # Apply OCR with medical-specific configuration
            custom_config = r'--oem 3 --psm 6 -l eng+osd'
            text = pytesseract.image_to_string(processed_image, config=custom_config)
            
            # Save text if output path is provided
            if output_path:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                logger.info(f"Extracted text saved to: {output_path}")
            
            return text
        
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return f"Error: {str(e)}"
    
    def _preprocess_image(self, image):
        """
        Preprocess image for better OCR results
        
        Args:
            image (numpy.ndarray): Input image
            
        Returns:
            numpy.ndarray: Processed image
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Denoise
            denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
            
            # Deskew if needed
            coords = np.column_stack(np.where(denoised > 0))
            angle = cv2.minAreaRect(coords)[-1]
            
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
                
            # Only deskew if angle is significant
            if abs(angle) > 0.5:
                (h, w) = denoised.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                denoised = cv2.warpAffine(
                    denoised, M, (w, h),
                    flags=cv2.INTER_CUBIC,
                    borderMode=cv2.BORDER_REPLICATE
                )
            
            return denoised
            
        except Exception as e:
            logger.warning(f"Image preprocessing failed: {str(e)}")
            return image  # Return original image if preprocessing fails
    
    def process_directory(self, input_dir, output_dir=None, preprocess=True):
        """
        Process all images in a directory
        
        Args:
            input_dir (str): Directory containing images
            output_dir (str, optional): Directory to save extracted text
            preprocess (bool): Whether to preprocess images
            
        Returns:
            dict: Dictionary mapping image paths to extracted text
        """
        results = {}
        
        try:
            # Create output directory if specified
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # Process each image in the directory
            image_extensions = ('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')
            for file in os.listdir(input_dir):
                # Check if file is an image
                if file.lower().endswith(image_extensions):
                    image_path = os.path.join(input_dir, file)
                    
                    # Determine output path if needed
                    output_path = None
                    if output_dir:
                        output_path = os.path.join(output_dir, f"{Path(file).stem}.txt")
                    
                    # Process image
                    logger.info(f"Processing image: {image_path}")
                    text = self.process_image(image_path, output_path, preprocess)
                    
                    results[image_path] = text
            
            if not results:
                logger.warning(f"No valid images found in directory: {input_dir}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing directory: {str(e)}")
            return results

def main():
    """Main function to demonstrate usage"""
    parser = argparse.ArgumentParser(
        description='Process medical documents with enhanced OCR',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('input', help='Input image file or directory')
    parser.add_argument('--output', '-o', help='Output file or directory')
    parser.add_argument('--tesseract', help='Path to Tesseract executable')
    parser.add_argument('--no-preprocess', action='store_true', 
                       help='Disable image preprocessing')
    args = parser.parse_args()
    
    try:
        # Initialize OCR processor
        processor = OCRProcessor(args.tesseract)
        
        # Check if input is a file or directory
        if os.path.isfile(args.input):
            # Process single file
            text = processor.process_image(args.input, args.output, 
                                        not args.no_preprocess)
            if not args.output:
                print(text)
        elif os.path.isdir(args.input):
            # Process directory
            results = processor.process_directory(args.input, args.output, 
                                               not args.no_preprocess)
            if not args.output:
                for path, text in results.items():
                    print(f"\n=== {path} ===")
                    print(text)
        else:
            logger.error(f"Input not found: {args.input}")
            return 1
        
        return 0
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    exit(main()) 