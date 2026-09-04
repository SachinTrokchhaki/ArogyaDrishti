"""
Medical report text processing utilities
"""
import re

class ReportProcessor:
    """Process medical report text and extract information"""
    
    @staticmethod
    def extract_medical_values(text):
        """
        Extract medical test values from text using dynamic pattern matching
        """
        results = []
        
        if not text:
            return results
        
        # First, fix the text for common OCR errors
        # This is a pre-processing step before pattern matching
        
        # Fix common OCR character errors in the entire text
        text_fixes = {
            # Numbers that got misread as letters
            'I': '1',  # I -> 1
            'O': '0',  # O -> 0
            'S': '5',  # S -> 5
            'B': '8',  # B -> 8
            'G': '6',  # G -> 6
            'Z': '2',  # Z -> 2
            'l': '1',  # l -> 1
            'o': '0',  # o -> 0
            's': '5',  # s -> 5
            'b': '8',  # b -> 8
            'g': '6',  # g -> 6
            'z': '2',  # z -> 2
        }
        
        # Apply fixes carefully - only replace where it makes sense
        # For now, let's use a more targeted approach in the extraction
        
        # Define test patterns with their units and reference ranges
        test_patterns = {
            'Hemoglobin': {
                'patterns': [
                    r'Hemoglobin\s+([^\s]+)\s+([A-Za-z/%]+)?',
                ],
                'unit': 'g/dL',
                'min': 13.0,
                'max': 17.0,
            },
            'Total Leucocyte Count': {
                'patterns': [
                    r'Total Leucocyte Count\s+([\d,.]+)\s+([A-Za-z/%]+)?',
                    r'TLC\s+([\d,.]+)\s+([A-Za-z/%]+)?',
                ],
                'unit': 'cells/cumm',
                'min': 4000,
                'max': 11000,
            },
            'Neutrophils': {
                'patterns': [
                    r'Neutrophils?\s+([\d,.]+)\s+([A-Za-z/%]+)?',
                ],
                'unit': '%',
                'min': 40,
                'max': 70,
            },
            'Lymphocytes': {
                'patterns': [
                    r'Lymphocytes?\s+([\d,.]+)\s+([A-Za-z/%]+)?',
                ],
                'unit': '%',
                'min': 20,
                'max': 40,
            },
            'Eosinophils': {
                'patterns': [
                    r'Eosinophils?\s+([\d,.]+)\s+([A-Za-z/%]+)?',
                ],
                'unit': '%',
                'min': 1,
                'max': 6,
            },
            'Monocytes': {
                'patterns': [
                    r'Monocytes?\s+([\d,.]+)\s+([A-Za-z/%]+)?',
                ],
                'unit': '%',
                'min': 2,
                'max': 8,
            },
            'Basophils': {
                'patterns': [
                    r'Basophils?\s+([\d,.]+)\s+([A-Za-z/%]+)?',
                ],
                'unit': '%',
                'min': 0,
                'max': 2,
            },
            'Platelet Count': {
                'patterns': [
                    r'Platelet Count\s+([^\s]+)\s+([A-Za-z/%]+)?',
                    r'Platelets?\s+([^\s]+)\s+([A-Za-z/%]+)?',
                ],
                'unit': 'Lakh/cumm',
                'min': 1.50,
                'max': 4.50,
            },
            'RBC Count': {
                'patterns': [
                    r'RBC Count\s+([^\s]+)\s+([A-Za-z/%]+)?',
                    r'RBC\s+([^\s]+)\s+([A-Za-z/%]+)?',
                ],
                'unit': 'million/cumm',
                'min': 4.20,
                'max': 5.60,
            },
            'PCV': {
                'patterns': [
                    r'PCV\s+([^\s]+)\s+([A-Za-z/%]+)?',
                    r'PCV \(Hematocrit\)\s+([^\s]+)\s+([A-Za-z/%]+)?',
                ],
                'unit': '%',
                'min': 40,
                'max': 50,
            },
            'MCV': {
                'patterns': [
                    r'MCV\s+([^\s]+)\s+([A-Za-z/%]+)?',
                ],
                'unit': 'fL',
                'min': 80,
                'max': 96,
            },
            'MCH': {
                'patterns': [
                    r'MCH\s+([^\s]+)\s+([A-Za-z/%]+)?',
                ],
                'unit': 'pg',
                'min': 27,
                'max': 32,
            },
            'MCHC': {
                'patterns': [
                    r'MCHC\s+([^\s]+)\s+([A-Za-z/%]+)?',
                ],
                'unit': 'g/dL',
                'min': 32,
                'max': 36,
            },
            'RDW-CV': {
                'patterns': [
                    r'RDW-CV\s+([^\s]+)\s+([A-Za-z/%]+)?',
                    r'RDW\s+([^\s]+)\s+([A-Za-z/%]+)?',
                ],
                'unit': '%',
                'min': 11.5,
                'max': 14.5,
            },
            'Bilirubin Total': {
                'patterns': [
                    r'Bilirubin Total\s+([^\s]+)\s+([A-Za-z/%]+)?',
                ],
                'unit': 'mg/dL',
                'min': 0.20,
                'max': 1.20,
            },
            'Bilirubin Direct': {
                'patterns': [
                    r'Bilirubin Direct\s+([^\s]+)\s+([A-Za-z/%]+)?',
                ],
                'unit': 'mg/dL',
                'min': 0,
                'max': 0.30,
            },
            'Bilirubin Indirect': {
                'patterns': [
                    r'Bilirubin Indirect\s+([^\s]+)\s+([A-Za-z/%]+)?',
                ],
                'unit': 'mg/dL',
                'min': 0.10,
                'max': 1.00,
            },
            'SGOT': {
                'patterns': [
                    r'SGOT\s+([^\s]+)\s+([A-Za-z/%]+)?',
                    r'AST\s+([^\s]+)\s+([A-Za-z/%]+)?',
                ],
                'unit': 'U/L',
                'min': 0,
                'max': 40,
            },
            'SGPT': {
                'patterns': [
                    r'SGPT\s+([^\s]+)\s+([A-Za-z/%]+)?',
                    r'ALT\s+([^\s]+)\s+([A-Za-z/%]+)?',
                ],
                'unit': 'U/L',
                'min': 0,
                'max': 41,
            },
            'Alkaline Phosphatase': {
                'patterns': [
                    r'Alkaline Phosphatase\s+([^\s]+)\s+([A-Za-z/%]+)?',
                    r'ALP\s+([^\s]+)\s+([A-Za-z/%]+)?',
                ],
                'unit': 'U/L',
                'min': 40,
                'max': 129,
            },
            'Total Protein': {
                'patterns': [
                    r'Total Protein\s+([^\s]+)\s+([A-Za-z/%]+)?',
                ],
                'unit': 'g/dL',
                'min': 6.0,
                'max': 8.3,
            },
            'Albumin': {
                'patterns': [
                    r'Albumin\s+([^\s]+)\s+([A-Za-z/%]+)?',
                ],
                'unit': 'g/dL',
                'min': 3.5,
                'max': 5.2,
            },
            'Globulin': {
                'patterns': [
                    r'Globulin\s+([^\s]+)\s+([A-Za-z/%]+)?',
                ],
                'unit': 'g/dL',
                'min': 2.0,
                'max': 3.5,
            },
            'A/G Ratio': {
                'patterns': [
                    r'A/G Ratio\s+([^\s]+)',
                    r'AG Ratio\s+([^\s]+)',
                ],
                'unit': '',
                'min': 1.0,
                'max': 2.0,
            },
            'Blood Urea': {
                'patterns': [
                    r'Blood Urea\s+([^\s]+)\s+([A-Za-z/%]+)?',
                    r'Urea\s+([^\s]+)\s+([A-Za-z/%]+)?',
                ],
                'unit': 'mg/dL',
                'min': 15.0,
                'max': 40.0,
            },
            'Serum Creatinine': {
                'patterns': [
                    r'Serum Creatinine\s+([^\s]+)\s+([A-Za-z/%]+)?',
                    r'Creatinine\s+([^\s]+)\s+([A-Za-z/%]+)?',
                ],
                'unit': 'mg/dL',
                'min': 0.70,
                'max': 1.30,
            },
            'Uric Acid': {
                'patterns': [
                    r'Uric Acid\s+([^\s]+)\s+([A-Za-z/%]+)?',
                ],
                'unit': 'mg/dL',
                'min': 3.5,
                'max': 7.2,
            },
            'eGFR': {
                'patterns': [
                    r'eGFR\s+([^\s]+)\s+([A-Za-z/%]+)?',
                ],
                'unit': 'mL/min/1.73m²',
                'min': 90,
                'max': 999,
            },
            'Total Cholesterol': {
                'patterns': [
                    r'Total Cholesterol\s+([^\s]+)\s+([A-Za-z/%]+)?',
                    r'Cholesterol\s+([^\s]+)\s+([A-Za-z/%]+)?',
                ],
                'unit': 'mg/dL',
                'min': 0,
                'max': 200,
            },
            'Triglycerides': {
                'patterns': [
                    r'Triglycerides\s+([^\s]+)\s+([A-Za-z/%]+)?',
                ],
                'unit': 'mg/dL',
                'min': 0,
                'max': 150,
            },
            'HDL Cholesterol': {
                'patterns': [
                    r'HDL Cholesterol\s+([^\s]+)\s+([A-Za-z/%]+)?',
                    r'HDL\s+([^\s]+)\s+([A-Za-z/%]+)?',
                ],
                'unit': 'mg/dL',
                'min': 40,
                'max': 999,
            },
            'LDL Cholesterol': {
                'patterns': [
                    r'LDL Cholesterol\s+([^\s]+)\s+([A-Za-z/%]+)?',
                    r'LDL\s+([^\s]+)\s+([A-Za-z/%]+)?',
                ],
                'unit': 'mg/dL',
                'min': 0,
                'max': 130,
            },
            'VLDL Cholesterol': {
                'patterns': [
                    r'VLDL Cholesterol\s+([^\s]+)\s+([A-Za-z/%]+)?',
                    r'VLDL\s+([^\s]+)\s+([A-Za-z/%]+)?',
                ],
                'unit': 'mg/dL',
                'min': 10,
                'max': 40,
            },
            'Non-HDL Cholesterol': {
                'patterns': [
                    r'Non-HDL Cholesterol\s+([^\s]+)\s+([A-Za-z/%]+)?',
                    r'Non-HDL\s+([^\s]+)\s+([A-Za-z/%]+)?',
                ],
                'unit': 'mg/dL',
                'min': 0,
                'max': 160,
            },
            'Fasting Blood Sugar': {
                'patterns': [
                    r'Fasting Blood Sugar\s+([^\s]+)\s+([A-Za-z/%]+)?',
                    r'Fasting\s+([^\s]+)\s+([A-Za-z/%]+)?',
                ],
                'unit': 'mg/dL',
                'min': 70,
                'max': 100,
            },
            'HbA1c': {
                'patterns': [
                    r'HbA1c\s+([^\s]+)\s+([A-Za-z/%]+)?',
                ],
                'unit': '%',
                'min': 4.0,
                'max': 5.6,
            },
            'Estimated Average Glucose': {
                'patterns': [
                    r'Estimated Average Glucose\s+([^\s]+)\s+([A-Za-z/%]+)?',
                    r'eAG\s+([^\s]+)\s+([A-Za-z/%]+)?',
                ],
                'unit': 'mg/dL',
                'min': 0,
                'max': 999,
            },
        }
        
        def fix_ocr_value(raw_value):
            """
            Fix OCR errors in values with comprehensive pattern matching
            """
            if not raw_value:
                return None
            
            # Remove commas and spaces
            raw_value = raw_value.replace(',', '').strip()
            
            # Define the mapping for OCR errors
            ocr_map = {
                'I': '1',
                'O': '0', 
                'S': '5',
                'B': '8',
                'G': '6',
                'Z': '2',
                'l': '1',
                'o': '0',
                's': '5',
                'b': '8',
            }
            
            # Try multiple interpretations
            
            # 1. Try fixing specific patterns
            # Pattern: IB.6 -> 13.6 (I→1, B→8)
            if 'I' in raw_value and 'B' in raw_value and '.' in raw_value:
                val = raw_value.replace('I', '1').replace('B', '8')
                clean = re.sub(r'[^0-9.]', '', val)
                if clean:
                    return clean
            
            # Pattern: 24S -> 245 (S→5)
            if raw_value.endswith('S') and len(raw_value) >= 2:
                val = raw_value[:-1] + '5'
                clean = re.sub(r'[^0-9.]', '', val)
                if clean:
                    return clean
            
            # Pattern: 4.6B -> 4.68 (B→8)
            if 'B' in raw_value and '.' in raw_value:
                val = raw_value.replace('B', '8')
                clean = re.sub(r'[^0-9.]', '', val)
                if clean:
                    return clean
            
            # Pattern: I7B -> 178 (I→1, B→8)
            if raw_value.startswith('I') and raw_value.endswith('B'):
                val = raw_value.replace('I', '1').replace('B', '8')
                clean = re.sub(r'[^0-9.]', '', val)
                if clean:
                    return clean
            
            # Pattern: IB2 -> 132 (I→1, B→8)
            if 'I' in raw_value and 'B' in raw_value:
                val = raw_value.replace('I', '1').replace('B', '8')
                clean = re.sub(r'[^0-9.]', '', val)
                if clean:
                    return clean
            
            # Pattern: 4O.2 -> 40.2 (O→0)
            if 'O' in raw_value and '.' in raw_value:
                val = raw_value.replace('O', '0')
                clean = re.sub(r'[^0-9.]', '', val)
                if clean:
                    return clean
            
            # 2. Try simple replacement of all OCR errors
            fixed = raw_value
            for old, new in ocr_map.items():
                fixed = fixed.replace(old, new)
            clean = re.sub(r'[^0-9.]', '', fixed)
            if clean:
                return clean
            
            # 3. Try original with non-numeric removal
            clean = re.sub(r'[^0-9.]', '', raw_value)
            if clean:
                return clean
            
            return None
        
        # Extract each test
        for test_name, config in test_patterns.items():
            value_found = None
            unit_found = config['unit']
            min_range = config['min']
            max_range = config['max']
            
            for pattern_str in config['patterns']:
                match = re.search(pattern_str, text, re.IGNORECASE)
                if match:
                    # Get the raw value
                    raw_value = match.group(1).strip()
                    
                    # Fix OCR errors
                    clean_value = fix_ocr_value(raw_value)
                    
                    if not clean_value:
                        continue
                    
                    # Try to get the unit from the match
                    if len(match.groups()) >= 2 and match.group(2):
                        unit_found = match.group(2).strip()
                    
                    # Try to determine if this value needs scaling
                    try:
                        val = float(clean_value)
                        
                        # Check if the value is outside the expected range
                        if min_range is not None and max_range is not None:
                            # If value is 100x too large, divide by 100
                            if val > max_range * 100 and max_range > 0:
                                val = val / 100
                                clean_value = str(round(val, 2))
                            # If value is 10x too large, divide by 10
                            elif val > max_range * 10 and max_range > 0:
                                val = val / 10
                                clean_value = str(round(val, 2))
                            # If value is 100x too small, multiply by 100
                            elif val < min_range / 100 and min_range > 0:
                                val = val * 100
                                clean_value = str(round(val, 2))
                            # If value is 10x too small, multiply by 10
                            elif val < min_range / 10 and min_range > 0:
                                val = val * 10
                                clean_value = str(round(val, 2))
                    except:
                        pass
                    
                    value_found = clean_value
                    break
            
            if value_found:
                # Determine status
                try:
                    val = float(value_found)
                    if min_range is not None and max_range is not None:
                        if val < min_range:
                            status = 'LOW'
                        elif val > max_range:
                            status = 'HIGH'
                        else:
                            status = 'NORMAL'
                    else:
                        status = 'UNKNOWN'
                except:
                    status = 'UNKNOWN'
                
                # Check for duplicates
                exists = False
                for r in results:
                    if r['test_name'].lower() == test_name.lower():
                        exists = True
                        break
                
                if not exists:
                    results.append({
                        'test_name': test_name,
                        'value': value_found,
                        'unit': unit_found,
                        'min_range': min_range,
                        'max_range': max_range,
                        'status': status
                    })
        
        return results
    
    @staticmethod
    def get_summary(results):
        """Generate summary statistics from test results"""
        if not results:
            return {
                'total_tests': 0,
                'normal': 0,
                'high': 0,
                'low': 0,
                'unknown': 0
            }
        
        total = len(results)
        normal = sum(1 for r in results if r.get('status') == 'NORMAL')
        high = sum(1 for r in results if r.get('status') == 'HIGH')
        low = sum(1 for r in results if r.get('status') == 'LOW')
        unknown = sum(1 for r in results if r.get('status') == 'UNKNOWN')
        
        return {
            'total_tests': total,
            'normal': normal,
            'high': high,
            'low': low,
            'unknown': unknown
        }