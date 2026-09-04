"""
AI Explanation utility using Groq API (Free & Fast)
"""
import os
import json
from dotenv import load_dotenv

# Try to import groq
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("❌ Groq library not installed. Run: pip install groq")

load_dotenv()

class AIExplainer:
    """Generate patient-friendly explanations using Groq AI"""
    
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        self.client = None
        self.is_available = False
        self.model = "qwen/qwen3.8-27b"   # Free model
        
        if self.api_key and GROQ_AVAILABLE:
            try:
                self.client = Groq(api_key=self.api_key)
                self.is_available = True
                print("✅ Groq API initialized successfully")
            except Exception as e:
                print(f"❌ Groq API initialization failed: {e}")
        elif not GROQ_AVAILABLE:
            print("❌ Groq library not installed. Run: pip install groq")
        else:
            print("❌ GROQ_API_KEY not found in environment variables")
    
    def generate_explanation(self, results, summary, patient_info=None):
        """
        Generate patient-friendly explanation from test results
        """
        if not self.is_available:
            return self._generate_fallback_explanation(results, summary)
        
        try:
            # Prepare the data for the prompt
            results_text = self._format_results_for_prompt(results)
            summary_text = self._format_summary_for_prompt(summary)
            patient_text = self._format_patient_for_prompt(patient_info)
            
            # Build the prompt
            prompt = f"""
You are a medical AI assistant explaining lab results to a patient in simple, clear, and empathetic language.

{patient_text}

SUMMARY OF RESULTS:
{summary_text}

DETAILED TEST RESULTS:
{results_text}

Please provide a patient-friendly explanation with the following sections:

1. **Overall Summary** (2-3 sentences): Give an overall assessment of the report in simple terms.

2. **Abnormal Values Analysis** (if any): For each abnormal value, explain:
   - What the test measures in simple terms
   - What the value means
   - Possible reasons for being high/low
   - Simple lifestyle recommendations

3. **Normal Values**: Briefly mention that most values are normal.

4. **Recommendations**: Provide 3-4 actionable health recommendations.

5. **Important Disclaimer**: Add a disclaimer that this is not medical advice.

Guidelines:
- Use simple, non-technical language (6th-grade reading level)
- Be empathetic and reassuring
- Use bullet points for easy reading
- Keep it concise but informative
- Never use the word "diagnosis"
- Always recommend consulting a doctor for abnormal results

FORMAT: Use markdown with clear headings (##, ###) and bullet points.
"""
            
            # Generate response using Groq
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful medical assistant that explains lab results in simple language."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000,
            )
            
            explanation = response.choices[0].message.content
            
            return {
                'success': True,
                'explanation': explanation,
                'provider': 'Groq AI (Mixtral)'
            }
            
        except Exception as e:
            print(f"AI Explanation error: {e}")
            return {
                'success': False,
                'explanation': self._generate_fallback_explanation(results, summary),
                'provider': 'Fallback (AI unavailable)',
                'error': str(e)
            }
    
    def _format_results_for_prompt(self, results):
        """Format test results for the prompt"""
        if not results:
            return "No test results found."
        
        lines = []
        for r in results:
            status = r.get('status', 'UNKNOWN')
            test_name = r.get('test_name', 'Unknown')
            value = r.get('value', '?')
            unit = r.get('unit', '')
            min_range = r.get('min_range', '?')
            max_range = r.get('max_range', '?')
            
            status_emoji = {
                'NORMAL': '✅',
                'HIGH': '⬆️',
                'LOW': '⬇️',
                'UNKNOWN': '❓'
            }.get(status, '❓')
            
            lines.append(
                f"- {test_name}: {value} {unit} "
                f"(Reference: {min_range} - {max_range} {unit}) "
                f"{status_emoji} {status}"
            )
        
        return '\n'.join(lines)
    
    def _format_summary_for_prompt(self, summary):
        """Format summary for the prompt"""
        if not summary:
            return "No summary available."
        
        total = summary.get('total_tests', 0)
        normal = summary.get('normal', 0)
        high = summary.get('high', 0)
        low = summary.get('low', 0)
        
        return f"""
- Total Tests: {total}
- Normal: {normal}
- High: {high}
- Low: {low}
"""
    
    def _format_patient_for_prompt(self, patient_info):
        """Format patient info for the prompt"""
        if not patient_info:
            return "Patient information not available."
        
        name = patient_info.get('name', 'Patient')
        age = patient_info.get('age', '')
        gender = patient_info.get('gender', '')
        
        info = f"Patient: {name}"
        if age:
            info += f", Age: {age}"
        if gender:
            info += f", Gender: {gender}"
        
        return info
    
    def _generate_fallback_explanation(self, results, summary):
        """Generate a fallback explanation without AI"""
        if not results:
            return """
## Overall Summary
No test results were found in the uploaded report. Please ensure the report is clearly visible and try again.

## Important
This tool provides analysis and explanations for educational purposes only. Always consult a qualified healthcare professional for medical advice.
"""
        
        total = summary.get('total_tests', 0)
        normal = summary.get('normal', 0)
        high = summary.get('high', 0)
        low = summary.get('low', 0)
        
        abnormal = [r for r in results if r.get('status') in ['HIGH', 'LOW']]
        
        explanation = f"""
## Overall Summary
Your medical report shows {total} test results. 
- {normal} values are within normal range ✅
- {high} values are above normal range ⬆️
- {low} values are below normal range ⬇️

"""
        
        if abnormal:
            explanation += "## Abnormal Values Analysis\n\n"
            for r in abnormal:
                test_name = r.get('test_name', 'Unknown')
                value = r.get('value', '?')
                unit = r.get('unit', '')
                status = r.get('status', 'UNKNOWN')
                min_range = r.get('min_range', '?')
                max_range = r.get('max_range', '?')
                
                if status == 'HIGH':
                    explanation += f"""
### {test_name}
- Value: {value} {unit}
- Reference Range: {min_range} - {max_range} {unit}
- **Status: HIGH** ⬆️

This value is above the normal range. This may indicate various conditions. Please consult your doctor for proper interpretation.

"""
                else:
                    explanation += f"""
### {test_name}
- Value: {value} {unit}
- Reference Range: {min_range} - {max_range} {unit}
- **Status: LOW** ⬇️

This value is below the normal range. This may indicate various conditions. Please consult your doctor for proper interpretation.

"""
        
        explanation += """
## Recommendations

1. **Discuss abnormal results with a qualified healthcare professional**
2. **Keep this report for future reference**
3. **Follow any instructions provided by your doctor**
4. **Maintain a healthy lifestyle with balanced diet and regular exercise**

## Important Disclaimer

⚠️ This explanation is generated for educational purposes only and is **not** a medical diagnosis. Always consult a qualified healthcare professional for proper medical advice, diagnosis, and treatment.
"""
        
        return explanation