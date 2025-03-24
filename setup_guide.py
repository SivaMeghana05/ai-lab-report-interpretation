#!/usr/bin/env python3
"""
HealthLensAI Setup Guide

This script helps set up the required dependencies for HealthLensAI.
It checks Python version, installs required packages, and provides
instructions for setting up OCR and table extraction capabilities.
"""

import os
import sys
import subprocess
import platform
import logging
from pathlib import Path

# Configure logging
file_handler = logging.FileHandler('healthlens_setup.log', encoding='utf-8')
console_handler = logging.StreamHandler()

# Use different success markers for file and console
class CustomFormatter(logging.Formatter):
    def format(self, record):
        # Replace Unicode checkmark with [OK] for console output
        if isinstance(record.msg, str) and '✓' in record.msg:
            record.msg = record.msg.replace('✓', '[OK]')
        return super().format(record)

formatter = CustomFormatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)

logger = logging.getLogger("HealthLensSetup")

def check_python_version():
    """Check if Python version is compatible"""
    logger.info("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        logger.warning(f"Python {version.major}.{version.minor} detected. HealthLensAI works best with Python 3.8+")
        return False
    else:
        logger.info(f"Python {version.major}.{version.minor} detected - Compatible ✓")
        return True

def run_pip_install(package):
    """Run pip install with proper error handling"""
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(f"Successfully installed {package} ✓")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install {package}: {e.stderr}")
        return False

def install_dependencies():
    """Install required Python packages"""
    logger.info("Installing core dependencies...")
    
    # Core packages required for basic functionality
    core_packages = [
        "PyPDF2>=3.0.0",
        "PyMuPDF>=1.20.0",
        "python-docx>=0.8.11",
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "opencv-python>=4.5.0",
        "pdfplumber>=0.7.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "reportlab>=3.6.0",
        "streamlit>=1.10.0"
    ]
    
    failed_packages = []
    for package in core_packages:
        logger.info(f"Installing {package}...")
        if not run_pip_install(package):
            failed_packages.append(package)
    
    if failed_packages:
        logger.warning("Failed to install the following packages:")
        for package in failed_packages:
            logger.warning(f"  - {package}")
        logger.warning("Please try installing them manually or check your internet connection")
    else:
        logger.info("Core dependencies installed successfully ✓")

def check_java():
    """Check if Java is installed and configured"""
    try:
        result = subprocess.run(
            ['java', '-version'],
            capture_output=True,
            text=True,
            stderr=subprocess.STDOUT
        )
        if 'version' in result.stdout:
            logger.info("Java is installed ✓")
            return True
    except:
        pass
    
    logger.warning("Java not found in PATH")
    return False

def check_tesseract():
    """Check if Tesseract is installed and configured"""
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        logger.info(f"Tesseract version {version} found ✓")
        return True
    except:
        logger.warning("Tesseract not found or not properly configured")
        return False

def setup_ocr():
    """Setup OCR dependencies"""
    logger.info("Setting up OCR capabilities...")
    
    # Install Python packages for OCR
    ocr_packages = [
        "pytesseract>=0.3.8",
        "pdf2image>=1.16.0"
    ]
    
    for package in ocr_packages:
        logger.info(f"Installing {package}...")
        run_pip_install(package)
    
    # Check system and provide appropriate instructions
    system = platform.system()
    
    logger.info("\nTo enable OCR functionality:")
    
    if system == "Windows":
        logger.info("""
Windows Installation Instructions:
1. Download Tesseract installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer and note the installation path
3. Add the Tesseract installation directory to your PATH environment variable
4. Download poppler from: https://github.com/oschwartz10612/poppler-windows/releases
5. Extract poppler and add the bin directory to your PATH
""")
    elif system == "Linux":
        logger.info("""
Linux Installation Instructions:
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install poppler-utils
""")
    elif system == "Darwin":  # macOS
        logger.info("""
macOS Installation Instructions:
brew install tesseract
brew install poppler
""")
    
    # Verify OCR setup
    if check_tesseract():
        logger.info("OCR setup verified successfully ✓")
    else:
        logger.warning("OCR setup needs manual configuration")

def setup_table_extraction():
    """Setup table extraction dependencies"""
    logger.info("Setting up table extraction capabilities...")
    
    # Install Python packages for table extraction
    table_packages = [
        "camelot-py[cv]>=0.10.0",
        "tabula-py>=2.3.0"
    ]
    
    for package in table_packages:
        logger.info(f"Installing {package}...")
        run_pip_install(package)
    
    # Check Java installation
    if not check_java():
        system = platform.system()
        logger.info("\nTo enable table extraction, please install Java:")
        
        if system == "Windows":
            logger.info("""
Windows Java Installation:
1. Download JDK from: https://www.oracle.com/java/technologies/downloads/
2. Run the installer
3. Set JAVA_HOME environment variable to your Java installation directory
4. Add %JAVA_HOME%\\bin to your PATH
""")
        elif system == "Linux":
            logger.info("""
Linux Java Installation:
sudo apt-get update
sudo apt-get install default-jre
export JAVA_HOME=/usr/lib/jvm/default-java
""")
        elif system == "Darwin":
            logger.info("""
macOS Java Installation:
brew install java
export JAVA_HOME=$(/usr/libexec/java_home)
""")

def create_requirements_file():
    """Create requirements.txt file"""
    requirements = [
        "PyPDF2>=3.0.0",
        "PyMuPDF>=1.20.0",
        "python-docx>=0.8.11",
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "opencv-python>=4.5.0",
        "pdfplumber>=0.7.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "reportlab>=3.6.0",
        "streamlit>=1.10.0",
        "pytesseract>=0.3.8",
        "pdf2image>=1.16.0",
        "camelot-py[cv]>=0.10.0",
        "tabula-py>=2.3.0"
    ]
    
    try:
        with open('requirements.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(requirements))
        logger.info("Created requirements.txt ✓")
    except Exception as e:
        logger.error(f"Failed to create requirements.txt: {str(e)}")

def main():
    """Main setup function"""
    try:
        logger.info("=" * 50)
        logger.info("HealthLensAI Setup Assistant")
        logger.info("=" * 50)
        
        # Check Python version first
        if not check_python_version():
            if not input("Continue anyway? (y/n): ").lower().startswith('y'):
                sys.exit(1)
        
        # Create requirements.txt
        create_requirements_file()
        
        # Install dependencies
        install_dependencies()
        
        # Setup OCR
        setup_ocr()
        
        # Setup table extraction
        setup_table_extraction()
        
        logger.info("\n" + "=" * 50)
        logger.info("Setup complete! You can now run HealthLensAI.")
        logger.info("=" * 50)
        
        logger.info("""
Troubleshooting Tips:
1. Ensure all external dependencies (Tesseract, Poppler, Java) are properly installed
2. Check that environment variables (PATH, JAVA_HOME) are correctly set
3. Restart your terminal/command prompt after making environment changes
4. Check healthlens_setup.log for detailed installation information
5. If issues persist, try installing packages manually using requirements.txt:
   pip install -r requirements.txt
""")
        
        return 0
        
    except Exception as e:
        logger.error(f"Setup failed: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 