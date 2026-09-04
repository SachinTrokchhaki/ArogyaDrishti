"""
OCR utilities for extracting text from images and PDFs
"""
import os
import tempfile
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import PyPDF2
import cv2
import numpy as np
import re

class OCRProcessor:
    """Handle OCR operations for medical reports"""
    
    @staticmethod
    def clean_ocr_text(text):
        """Clean common OCR errors from extracted text"""
        if not text:
            return text
        
        # Fix common OCR errors (0 → O, 1 → I, etc.)
        replacements = {
            '0': 'O',
            '1': 'I',
            '3': 'B',
            '5': 'S',
            '8': 'B',
            '©': 'c',
            '®': 'r',
            '¢': 'c',
            '°': '',
            'µ': 'u',
            '²': '2',
            '|': '',
            '—': '-',
            '–': '-',
            '*': '',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Fix OCR errors in medical terms
        medical_fixes = {
            'Hemog1obin': 'Hemoglobin',
            'Totat': 'Total',
            'Loucocyte': 'Leucocyte',
            'Ditferentia1': 'Differential',
            'Leucocyte': 'Leucocyte',
            'Neutrophits': 'Neutrophils',
            'Lymphocytes': 'Lymphocytes',
            'Eosinophi': 'Eosinophils',
            'Monocytes': 'Monocytes',
            'Basophi1s': 'Basophils',
            'P1ate1et': 'Platelet',
            'Lakhicumm': 'Lakh/cumm',
            'mitfionfeumm': 'million/cumm',
            'ofa': 'g/dL',
            'vA': 'U/L',
            'uA': 'U/L',
            'moet': 'mg/dL',
            'mofd1': 'mg/dL',
            'gid': 'g/dL',
            'gid1': 'g/dL',
            'id1': 'g/dL',
            'me/d1': 'mg/dL',
            'mo/di': 'mg/dL',
            'mg/d1': 'mg/dL',
            'mUmin': 'mL/min',
            'Catcutated': 'Calculated',
            'Chotesterot': 'Cholesterol',
            'Cho1estero1': 'Cholesterol',
            'Trig1ycerides': 'Triglycerides',
            'A1bumin': 'Albumin',
            'G1obu1in': 'Globulin',
            'B1ood': 'Blood',
            'Unie': 'Uric',
            'Creatining': 'Creatinine',
            'Bi1irubin': 'Bilirubin',
            'Bi11nabin': 'Bilirubin',
            'SG0T': 'SGOT',
            'SGPT': 'SGPT',
            'A1ka1ine': 'Alkaline',
            'Phosphatase': 'Phosphatase',
            'Tota1': 'Total',
            'Prote1n': 'Protein',
            'Chotesterot': 'Cholesterol',
            'HDL': 'HDL',
            'LDL': 'LDL',
            'VLDL': 'VLDL',
            'HbAIc': 'HbA1c',
            'G1ucose': 'Glucose',
            'Avorage': 'Average',
            'GURGA0N': 'GURGAON',
            'Deth1': 'Delhi',
            '0tfice': 'Office',
            'Co11ected': 'Collected',
            'Finat': 'Final',
            'A1e': 'A/c',
        }
        
        for old, new in medical_fixes.items():
            text = text.replace(old, new)
        
        # Fix common patterns
        text = re.sub(r'(\d+)\s*[-–—]\s*(\d+)', r'\1 - \2', text)
        text = re.sub(r'(\d+)\s*=\s*(\d+)', r'\1 - \2', text)
        text = re.sub(r'(\d+)\s*\+\s*(\d+)', r'\1 - \2', text)
        text = re.sub(r'(\d+)\s*\.\s*(\d+)', r'\1.\2', text)  # Fix decimal points
        
        return text
    
    @staticmethod
    def preprocess_image(image_path):
        """
        Advanced preprocessing for better OCR accuracy
        """
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                return None
            
            # Resize image for better OCR (if too small or too large)
            height, width = img.shape[:2]
            if width < 1000:
                scale = 2.0
                new_width = int(width * scale)
                new_height = int(height * scale)
                img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            elif width > 3000:
                scale = 2000 / width
                new_width = int(width * scale)
                new_height = int(height * scale)
                img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Apply morphological operations to clean up text
            kernel = np.ones((1, 1), np.uint8)
            morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            # Denoise
            denoised = cv2.fastNlMeansDenoising(morph)
            
            # Increase contrast
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            sharpened = cv2.filter2D(denoised, -1, kernel)
            
            return sharpened
        except Exception as e:
            print(f"Preprocessing error: {e}")
            return None
    
    @staticmethod
    def extract_text_from_image(image_file):
        """
        Extract text from image file using Tesseract with multiple attempts
        """
        # After extracting text, apply cleaning
        if extracted_text:
        # Apply OCR cleaning
            extracted_text = OCRProcessor.clean_ocr_text(extracted_text)
    
        # Also try to fix table formatting
        lines = extracted_text.split('\n')
        cleaned_lines = []
        for line in lines:
            # Remove extra spaces between table columns
            line = re.sub(r'\s{2,}', ' ', line)
            # Fix common test name OCR errors
            line = line.replace('Hemog1obin', 'Hemoglobin')
            line = line.replace('Bilirubin', 'Bilirubin')
            line = line.replace('Creatinine', 'Creatinine')
            line = line.replace('Cholesterol', 'Cholesterol')
            cleaned_lines.append(line)
        extracted_text = '\n'.join(cleaned_lines)
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                for chunk in image_file.chunks():
                    tmp_file.write(chunk)
                tmp_path = tmp_file.name
            
            extracted_text = ""
            
            # Approach 1: Advanced preprocessing
            processed_img = OCRProcessor.preprocess_image(tmp_path)
            if processed_img is not None:
                processed_path = tmp_path.replace('.png', '_processed.png')
                cv2.imwrite(processed_path, processed_img)
                
                # Try different PSM modes for table extraction
                configs = [
                    ('--psm 6 --oem 3', 'Block of text'),
                    ('--psm 4 --oem 3', 'Single column'),
                    ('--psm 3 --oem 3', 'Automatic'),
                    ('--psm 11 --oem 3', 'Sparse text'),
                    ('--psm 12 --oem 3', 'Sparse with OSD'),
                ]
                
                best_text = ""
                for config, desc in configs:
                    try:
                        text = pytesseract.image_to_string(
                            processed_path,
                            lang='eng',
                            config=config
                        )
                        if text and len(text.strip()) > len(best_text.strip()):
                            best_text = text.strip()
                    except Exception as e:
                        print(f"OCR error with {desc}: {e}")
                        continue
                
                if best_text:
                    extracted_text = best_text
                
                os.unlink(processed_path)
            
            # Approach 2: Try without preprocessing (PIL with enhancements)
            if not extracted_text or len(extracted_text) < 100:
                try:
                    img = Image.open(tmp_path)
                    
                    # Enhance image
                    enhancer = ImageEnhance.Contrast(img)
                    img = enhancer.enhance(2.5)
                    enhancer = ImageEnhance.Sharpness(img)
                    img = enhancer.enhance(3.0)
                    enhancer = ImageEnhance.Brightness(img)
                    img = enhancer.enhance(1.5)
                    
                    # Convert to grayscale
                    img = img.convert('L')
                    
                    # Try OCR with different configs
                    configs = ['--psm 6 --oem 3', '--psm 4 --oem 3', '--psm 3 --oem 3']
                    for config in configs:
                        text = pytesseract.image_to_string(img, lang='eng', config=config)
                        if text and len(text.strip()) > len(extracted_text):
                            extracted_text = text.strip()
                except Exception as e:
                    print(f"PIL OCR error: {e}")
            
            # Approach 3: Try with image segmentation
            if not extracted_text or len(extracted_text) < 100:
                try:
                    img = cv2.imread(tmp_path)
                    if img is not None:
                        # Convert to grayscale
                        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                        # Apply threshold
                        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
                        
                        # Save processed image
                        seg_path = tmp_path.replace('.png', '_seg.png')
                        cv2.imwrite(seg_path, thresh)
                        
                        text = pytesseract.image_to_string(seg_path, lang='eng', config='--psm 6 --oem 3')
                        if text and len(text.strip()) > len(extracted_text):
                            extracted_text = text.strip()
                        
                        os.unlink(seg_path)
                except Exception as e:
                    print(f"Segmentation OCR error: {e}")
            
            # Clean up temp file
            os.unlink(tmp_path)
            
            # Post-process extracted text
            if extracted_text:
                # Remove excessive whitespace
                extracted_text = re.sub(r'\n\s*\n', '\n', extracted_text)
                # Remove non-ASCII characters (keep only readable text)
                extracted_text = re.sub(r'[^\x00-\x7F\n\r]', ' ', extracted_text)
                # Remove multiple spaces
                extracted_text = re.sub(r' +', ' ', extracted_text)
            
            # APPLY THE CLEANING FUNCTION HERE
            if extracted_text:
                extracted_text = OCRProcessor.clean_ocr_text(extracted_text)
            
            return extracted_text.strip()
                
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""
    
    @staticmethod
    def extract_text_from_pdf(pdf_file):
        """
        Extract text from PDF file
        """
        try:
            text = ""
            
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                for chunk in pdf_file.chunks():
                    tmp_file.write(chunk)
                tmp_path = tmp_file.name
            
            # Extract text from PDF
            with open(tmp_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"--- Page {page_num + 1} ---\n"
                        text += page_text + "\n\n"
            
            # Clean up
            os.unlink(tmp_path)
            
            # Apply cleaning to PDF text too
            if text:
                text = OCRProcessor.clean_ocr_text(text)
            
            return text.strip()
            
        except Exception as e:
            print(f"PDF Extraction Error: {e}")
            return ""
    
    @staticmethod
    def extract_text(file):
        """
        Extract text from file (image or PDF) based on file extension
        """
        file_extension = file.name.split('.')[-1].lower()
        
        if file_extension == 'pdf':
            return OCRProcessor.extract_text_from_pdf(file)
        elif file_extension in ['png', 'jpg', 'jpeg']:
            return OCRProcessor.extract_text_from_image(file)
        else:
            return "Unsupported file format"