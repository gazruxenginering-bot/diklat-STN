"""
Groq API Integration - Primary AI Provider
Groq menyediakan free tier yang generous: 1000+ requests/hari
Model: llama-3.3-70b-versatile - latest Groq model yang tersedia
"""

import os
import json
from typing import Optional, Dict
from datetime import datetime

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("⚠️  Groq SDK not available")


class GroqChatManager:
    """Manager untuk Groq API integration (FREE & RELIABLE)"""
    
    def __init__(self, api_key: str = None):
        # Get API key dari environment atau file
        self.api_key = api_key or os.getenv('GROQ_API_KEY') or self._get_api_key_from_credentials()
        
        # Model untuk Groq
        self.model = "llama-3.3-70b-versatile"  # Latest Groq model, free tier
        
        self.initialized = False
        self.client = None
        
        if self.api_key and GROQ_AVAILABLE:
            try:
                self.client = Groq(api_key=self.api_key)
                self.initialized = True
                print(f"✅ Groq API configured")
                print(f"   Model: {self.model}")
                print(f"   Free tier: 1000 requests/day")
            except Exception as e:
                print(f"❌ Error initializing Groq: {e}")
        elif not GROQ_AVAILABLE:
            print("⚠️  Groq SDK not installed")
        else:
            print("⚠️  Groq API key not found")
    
    @staticmethod
    def _get_api_key_from_credentials() -> Optional[str]:
        """Get Groq API key dari credentials.json"""
        try:
            possible_paths = [
                os.path.join(os.path.dirname(__file__), '..', 'credentials.json'),
                os.path.join(os.getcwd(), 'credentials.json'),
                '/workspaces/diklat-STN/credentials.json'
            ]
            
            for credentials_path in possible_paths:
                abs_path = os.path.abspath(credentials_path)
                if os.path.exists(abs_path):
                    with open(abs_path, 'r') as f:
                        creds = json.load(f)
                        api_key = creds.get('groq_api_key')
                        if api_key:
                            print(f"✅ Groq API key loaded from credentials.json")
                            return api_key
        except Exception as e:
            pass
        return None
    
    def _build_system_prompt(self) -> str:
        """Build system prompt untuk Groq"""
        return """Kamu adalah asisten teknis yang membantu mekanik Indonesia.

INSTRUKSI:
1. Jawab dalam Bahasa Indonesia yang jelas dan praktis
2. Gunakan istilah teknis yang mudah dipahami
3. Sertakan langkah-langkah praktis jika relevan
4. Selalu rujuk ke dokumen sumber yang diberikan
5. Jika tidak yakin, katakan "Saya tidak menemukan informasi yang cukup"
6. Jawab dengan singkat dan to-the-point

TONE: Profesional, ramah, dan praktis untuk mekanik."""
    
    def generate_answer(self,
                       query: str,
                       context: str = "",
                       include_sources: bool = True) -> Dict:
        """
        Generate jawaban menggunakan Groq API (FAST & FREE)
        
        Args:
            query: Pertanyaan dari user
            context: Context dari dokumen
            include_sources: Include sumber rujukan
        
        Returns:
            {
                'success': bool,
                'answer': str,
                'model': str,
                'generated_at': str,
                'error': str (jika ada)
            }
        """
        if not self.initialized or not self.client:
            return {
                'success': False,
                'error': 'Groq API tidak diinisialisasi. Pastikan GROQ_API_KEY tersedia.',
                'answer': None,
                'model': None
            }
        
        try:
            # Build prompt
            if context:
                prompt = f"""Berdasarkan dokumen berikut, jawab pertanyaan:

---DOKUMEN---
{context}
---AKHIR DOKUMEN---

Pertanyaan: {query}

Jawab dalam Bahasa Indonesia yang praktis dan jelas."""
            else:
                prompt = f"Pertanyaan: {query}\n\nJawab dalam Bahasa Indonesia yang praktis dan jelas."
            
            # Call Groq API
            message = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": self._build_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=1024,
                top_p=0.95
            )
            
            answer = message.choices[0].message.content.strip()
            
            return {
                'success': True,
                'answer': answer,
                'model': self.model,
                'generated_at': datetime.utcnow().isoformat(),
                'provider': 'Groq',
                'usage': {
                    'input_tokens': message.usage.prompt_tokens,
                    'output_tokens': message.usage.completion_tokens
                }
            }
        
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Groq generation error: {error_msg}")
            return {
                'success': False,
                'error': f'Groq error: {error_msg}',
                'answer': None,
                'model': self.model
            }
    
    def check_api_availability(self) -> bool:
        """Check if Groq API is available"""
        if not self.initialized:
            return False
        
        try:
            # Simple test
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": "Hi"}],
                model=self.model,
                max_tokens=10
            )
            return response is not None
        except Exception as e:
            print(f"⚠️  Groq health check failed: {e}")
            return False
