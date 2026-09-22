"""
AI Explanation utility with multi-provider fallback + retry logic.
Priority: Groq (qwen3.8) → Gemini (3.6-flash) → Local template
"""
import os
import time
from dotenv import load_dotenv

# ===== Groq =====
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("⚠️  Groq library not installed. Run: pip install groq")

# ===== Gemini (new google-genai package) =====
try:
    from google import genai as google_genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  google-genai not installed. Run: pip install google-genai")

load_dotenv()


def is_retryable_error(error_str):
    """Check if an error is worth retrying (temporary issue)."""
    error_lower = error_str.lower()
    retryable_keywords = [
        '503',
        'unavailable',
        'overloaded',
        'timeout',
        'timed out',
        'rate limit',
        '429',
        'high demand',
        'try again',
        'connection',
        'temporarily',
    ]
    return any(keyword in error_lower for keyword in retryable_keywords)


class AIExplainer:
    """Generate non-diagnostic explanations with multi-provider fallback + retry."""
    
    # Groq models to try in order
    GROQ_MODELS = [
        'qwen/qwen3.8-27b',
        'openai/gpt-oss-120b',
        'openai/gpt-oss-20b',
    ]
    
    # Gemini model
    GEMINI_MODEL = 'gemini-3.6-flash'
    
    # Retry configuration
    MAX_RETRIES = 3
    INITIAL_RETRY_DELAY = 2  # seconds
    
    def __init__(self):
        self.groq = None
        self.gemini_client = None
        
        # Setup Groq
        if os.getenv('GROQ_API_KEY') and GROQ_AVAILABLE:
            try:
                self.groq = Groq(api_key=os.getenv('GROQ_API_KEY'))
                print("✅ Groq initialized")
            except Exception as e:
                print(f"❌ Groq init failed: {e}")
        
        # Setup Gemini
        if os.getenv('GEMINI_API_KEY') and GEMINI_AVAILABLE:
            try:
                self.gemini_client = google_genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
                print("✅ Gemini initialized")
            except Exception as e:
                print(f"❌ Gemini init failed: {e}")
        
        if not self.groq and not self.gemini_client:
            print("⚠️  No AI providers available. Will use local fallback template.")
    
    # ============================================================
    # ============ PUBLIC METHODS ============
    # ============================================================
    
    def generate_explanation(self, results, summary, patient_info=None):
        """Generate patient-friendly explanation with provider fallback + retry."""
        prompt = self._build_prompt(results, summary, patient_info)
        failures = []
        
        # Try Groq models (each with retry)
        if self.groq:
            for model_name in self.GROQ_MODELS:
                result = self._try_groq_with_retry(model_name, prompt, failures)
                if result:
                    return result
        
        # Try Gemini (with retry)
        if self.gemini_client:
            result = self._try_gemini_with_retry(prompt, failures)
            if result:
                return result
        
        # All providers failed → local template
        print(f"❌ All AI providers failed. Using local template.")
        print(f"   Failures: {failures}")
        return {
            'success': False,
            'explanation': self._generate_fallback_explanation(results, summary),
            'provider': 'Local template',
            'failures': failures,
        }
    
    def answer_question(self, question, report_data, patient_info=None, chat_history=None, current_user_info=None):
        """
        Answer a specific question about a report.
        
        Args:
            question: user's question string
            report_data: dict with 'results', 'summary', 'document_type'
            patient_info: dict with 'name', 'age', 'gender' (report's patient)
            chat_history: list of {question, answer} for context
            current_user_info: dict with 'name' (logged-in user)
        """
        results = report_data.get('results', [])
        summary = report_data.get('summary', {})
        document_type = report_data.get('document_type', 'Medical Report')
        
        # Format context
        results_text = self._format_results_for_prompt(results)
        summary_text = self._format_summary_for_prompt(summary)
        patient_text = self._format_patient_for_prompt(patient_info)
        
        # Determine names for greeting
        report_patient_name = (patient_info or {}).get('name', 'Unknown')
        logged_in_name = (current_user_info or {}).get('name', 'there')
        
        # Decide how to address the report
        if (
            report_patient_name
            and report_patient_name != 'Unknown'
            and report_patient_name.lower().strip() != logged_in_name.lower().strip()
        ):
            # Different person — mention both names
            report_reference = f"{report_patient_name}'s report"
            context_line = (
                f"The logged-in user is {logged_in_name}. "
                f"The report belongs to {report_patient_name} (a different person). "
                f"Greet {logged_in_name} and refer to the report as "
                f"\"{report_patient_name}'s report\"."
            )
        else:
            # Same person or unknown — just use the user's name
            report_reference = "your report"
            context_line = (
                f"The logged-in user is {logged_in_name} and this is their own report. "
                f"Greet {logged_in_name} warmly."
            )
        
        # Build chat history context
        history_text = ""
        if chat_history:
            history_lines = []
            for msg in chat_history[-5:]:  # last 5 messages
                history_lines.append(f"User: {msg['question']}")
                history_lines.append(f"Assistant: {msg['answer']}")
            if history_lines:
                history_text = "\n\nPREVIOUS CONVERSATION:\n" + "\n".join(history_lines)
        
        prompt = f"""You are a friendly medical AI assistant helping a user understand a medical report.

CONTEXT:
{context_line}
The report is referred to as: "{report_reference}"

{patient_text}

REPORT TYPE: {document_type}

SUMMARY:
{summary_text}

DETAILED RESULTS:
{results_text}
{history_text}

The user asks: "{question}"

Write a warm, helpful answer.

STRICT RULES:
- Start your FIRST reply with a brief friendly greeting using the name "{logged_in_name}"
- When referring to the report, say "{report_reference}"
- Answer ONLY based on the report data above
- Use plain 6th-grade English
- Keep the answer under 120 words
- NEVER use the word "diagnosis"
- If the question is about a value not in this report, politely say so
- If the question requires medical judgment, recommend consulting a doctor
- If the question is off-topic, gently redirect
- Use markdown bullets for lists when helpful
- Be warm and reassuring
- Address the user as "you"

Answer:"""
        
        failures = []
        
        # Try Groq
        if self.groq:
            for model_name in self.GROQ_MODELS:
                try:
                    print(f"🤖 Q&A Groq: {model_name}")
                    response = self.groq.chat.completions.create(
                        model=model_name,
                        messages=[
                            {'role': 'system', 'content': 'You are a helpful medical assistant. Answer based only on the given report data.'},
                            {'role': 'user', 'content': prompt},
                        ],
                        temperature=0.3,
                        max_tokens=500,
                    )
                    answer = response.choices[0].message.content
                    if answer and len(answer.strip()) > 10:
                        print(f"✅ Q&A Groq success: {model_name}")
                        return {
                            'success': True,
                            'answer': answer,
                            'provider': f'Groq ({model_name})',
                        }
                except Exception as e:
                    failures.append({'provider': 'Groq', 'model': model_name, 'error': str(e)})
                    continue
        
        # Try Gemini
        if self.gemini_client:
            try:
                print(f"🤖 Q&A Gemini: {self.GEMINI_MODEL}")
                response = self.gemini_client.models.generate_content(
                    model=self.GEMINI_MODEL,
                    contents=prompt,
                )
                answer = response.text
                if answer and len(answer.strip()) > 10:
                    print(f"✅ Q&A Gemini success: {self.GEMINI_MODEL}")
                    return {
                        'success': True,
                        'answer': answer,
                        'provider': f'Gemini ({self.GEMINI_MODEL})',
                    }
            except Exception as e:
                failures.append({'provider': 'Gemini', 'error': str(e)})
        
        # Fallback
        return {
            'success': False,
            'answer': f"Hi {logged_in_name}, I'm unable to answer right now. Please try again in a moment.",
            'provider': 'unavailable',
            'failures': failures,
        }
    
    # ============================================================
    # ============ PRIVATE METHODS ============
    # ============================================================
    
    def _try_groq_with_retry(self, model_name, prompt, failures):
        """Try a Groq model with retry logic. Returns result dict or None."""
        retry_delay = self.INITIAL_RETRY_DELAY
        
        for attempt in range(self.MAX_RETRIES):
            try:
                print(f"🤖 Trying Groq: {model_name} (attempt {attempt + 1}/{self.MAX_RETRIES})")
                response = self.groq.chat.completions.create(
                    model=model_name,
                    messages=[
                        {'role': 'system', 'content': 'Explain medical reports without diagnosing. Be empathetic and clear.'},
                        {'role': 'user', 'content': prompt},
                    ],
                    temperature=0.3,
                    max_tokens=2000,
                )
                explanation = response.choices[0].message.content
                
                if explanation and len(explanation.strip()) > 50:
                    print(f"✅ Groq success: {model_name}")
                    return {
                        'success': True,
                        'explanation': explanation,
                        'provider': f'Groq ({model_name})',
                        'failures': failures,
                    }
                else:
                    failures.append({
                        'provider': 'Groq',
                        'model': model_name,
                        'error': 'Empty or too-short response',
                    })
                    return None
                    
            except Exception as error:
                error_str = str(error)
                
                if is_retryable_error(error_str) and attempt < self.MAX_RETRIES - 1:
                    print(f"   ⏳ Groq busy/rate-limited, retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    failures.append({
                        'provider': 'Groq',
                        'model': model_name,
                        'error': error_str,
                    })
                    return None
        
        return None
    
    def _try_gemini_with_retry(self, prompt, failures):
        """Try Gemini with retry logic. Returns result dict or None."""
        retry_delay = self.INITIAL_RETRY_DELAY
        
        for attempt in range(self.MAX_RETRIES):
            try:
                print(f"🤖 Trying Gemini: {self.GEMINI_MODEL} (attempt {attempt + 1}/{self.MAX_RETRIES})")
                response = self.gemini_client.models.generate_content(
                    model=self.GEMINI_MODEL,
                    contents=prompt,
                )
                explanation = response.text
                
                if explanation and len(explanation.strip()) > 50:
                    print(f"✅ Gemini success: {self.GEMINI_MODEL}")
                    return {
                        'success': True,
                        'explanation': explanation,
                        'provider': f'Gemini ({self.GEMINI_MODEL})',
                        'failures': failures,
                    }
                else:
                    failures.append({
                        'provider': 'Gemini',
                        'model': self.GEMINI_MODEL,
                        'error': 'Empty or too-short response',
                    })
                    return None
                    
            except Exception as error:
                error_str = str(error)
                
                if is_retryable_error(error_str) and attempt < self.MAX_RETRIES - 1:
                    print(f"   ⏳ Gemini busy (503/high demand), retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    failures.append({
                        'provider': 'Gemini',
                        'model': self.GEMINI_MODEL,
                        'error': error_str,
                    })
                    return None
        
        return None
    
    def _build_prompt(self, results, summary, patient_info):
        """Build a structured prompt that produces scannable output."""
        results_text = self._format_results_for_prompt(results)
        summary_text = self._format_summary_for_prompt(summary)
        patient_text = self._format_patient_for_prompt(patient_info)
        
        # Extract first name for personalization
        patient_name = patient_info.get('name', 'there') if patient_info else 'there'
        first_name = patient_name.split()[0] if patient_name and patient_name != 'Unknown' else 'there'
        
        return f"""
You are a friendly medical AI explaining lab results to a patient.

{patient_text}

SUMMARY:
{summary_text}

DETAILED RESULTS:
{results_text}

Write a patient-friendly explanation using EXACTLY this format. Do NOT deviate.

Start with one short warm greeting using the first name "{first_name}".

Then use these EXACT section headings (with emojis):

## 🎯 Key Findings
Write ONE short sentence summarizing the overall picture. If everything is normal, say so clearly. If not, mention how many values need attention.

## 📊 What Each Value Means
For EACH abnormal value (HIGH or LOW), use this exact format:

**<Test Name>: <Value> <Unit>** <⬆️ or ⬇️>

<1-2 sentence explanation in very simple language>

→ What to do: <1 short actionable sentence>

If there are no abnormal values, just write: "All your test values are within the normal range. Great news!"

## 💡 What You Can Do
Use 3 to 4 bullet points, each starting with an emoji:
✅ <actionable tip based on the results>
💧 <hydration or rest tip>
🥗 <diet tip>
🏃 <lifestyle tip>

## ⚠️ Important Note
One sentence reminder that this is educational information and not medical advice. Recommend consulting a doctor.

STRICT RULES:
- Use plain 6th-grade level English
- Total length: under 220 words
- NEVER use the word "diagnosis"
- Do NOT use markdown like ** inside the explanation sentences (only for test names as shown)
- Do NOT wrap headings in # symbols (just use ## as shown)
- Do NOT add extra sections
- Address the patient directly as "you"
- Be warm, reassuring, and clear
- If a value is very abnormal, gently suggest seeing a doctor soon
"""
    
    def _format_results_for_prompt(self, results):
        if not results:
            return "No test results found."
        
        lines = []
        for r in results:
            status = r.get('status', 'UNKNOWN')
            status_emoji = {
                'NORMAL': '✅', 'HIGH': '⬆️', 'LOW': '⬇️', 'UNKNOWN': '❓'
            }.get(status, '❓')
            
            lines.append(
                f"- {r.get('test_name', 'Unknown')}: {r.get('value', '?')} {r.get('unit', '')} "
                f"(Reference: {r.get('min_range', '?')} - {r.get('max_range', '?')} {r.get('unit', '')}) "
                f"{status_emoji} {status}"
            )
        return '\n'.join(lines)
    
    def _format_summary_for_prompt(self, summary):
        if not summary:
            return "No summary available."
        return f"""
- Total Tests: {summary.get('total_tests', 0)}
- Normal: {summary.get('normal', 0)}
- High: {summary.get('high', 0)}
- Low: {summary.get('low', 0)}
"""
    
    def _format_patient_for_prompt(self, patient_info):
        if not patient_info:
            return "Patient information not available."
        
        info = f"Patient: {patient_info.get('name', 'Patient')}"
        if patient_info.get('age'):
            info += f", Age: {patient_info['age']}"
        if patient_info.get('gender'):
            info += f", Gender: {patient_info['gender']}"
        return info
    
    def _generate_fallback_explanation(self, results, summary):
        """Local template explanation (no AI needed)."""
        if not results:
            return """
## 🎯 Key Findings
No test results were found in the uploaded report. Please ensure the report is clearly visible and try again.

## ⚠️ Important Note
This tool provides analysis for educational purposes only. Always consult a qualified healthcare professional for medical advice.
"""
        
        total = summary.get('total_tests', 0)
        normal = summary.get('normal', 0)
        high = summary.get('high', 0)
        low = summary.get('low', 0)
        abnormal = [r for r in results if r.get('status') in ['HIGH', 'LOW']]
        
        explanation = f"""
## 🎯 Key Findings
Your report shows {total} test results: {normal} normal, {high} high, and {low} low.

"""
        
        if abnormal:
            explanation += "## 📊 What Each Value Means\n\n"
            for r in abnormal:
                status = r.get('status', 'UNKNOWN')
                arrow = '⬆️' if status == 'HIGH' else '⬇️'
                explanation += f"""**{r.get('test_name', 'Unknown')}: {r.get('value', '?')} {r.get('unit', '')}** {arrow}

This value is {status.lower()} compared to the normal range.

→ What to do: Consult your doctor for proper interpretation.

"""
        
        explanation += """## 💡 What You Can Do
✅ Discuss abnormal results with a qualified healthcare professional
💧 Stay hydrated and get adequate rest
🥗 Maintain a balanced diet with fresh fruits and vegetables
🏃 Regular light exercise is beneficial

## ⚠️ Important Note
This explanation is for educational purposes only and is not a medical diagnosis. Always consult a qualified healthcare professional.
"""
        return explanation