from typing import Dict
from datetime import datetime
import openai
import os

class AgentValidator:
    def __init__(self, openai_api_key: str = None, xai_api_key: str = None):
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        self.xai_api_key = xai_api_key or os.getenv('XAI_API_KEY')
        
        if not self.openai_api_key or not self.xai_api_key:
            raise ValueError("Both OpenAI and X.AI API keys are required")
        
        self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
        self.xai_client = openai.OpenAI(
            api_key=self.xai_api_key,
            base_url="https://api.x.ai/v1"
        )
        
        self.agent_validation_data = {
            'lister_verification': None,
            'verification_source': None,
            'lister_name': None,
            'processed_at': None,
            'additional_checks': {}
        }

    def verify_lister(self, lister_name: str) -> Dict:
        """Verifies lister information across real estate platforms"""
        try:
            # Get verification from X.AI
            xai_verification = self._get_xai_verification(lister_name)
            
            # Get additional verification from OpenAI
            openai_verification = self._get_openai_verification(lister_name)
            
            self.agent_validation_data.update({
                'lister_verification': xai_verification,
                'verification_source': 'X.AI Grok Model + OpenAI',
                'lister_name': lister_name,
                'processed_at': str(datetime.now()),
                'additional_checks': openai_verification
            })
            
            return self._generate_validation_data()
            
        except Exception as e:
            return self._generate_error_data(str(e))

    def _get_xai_verification(self, lister_name: str) -> str:
        system_prompt = """You are a knowledgeable real estate assistant AI, verifying lister information."""
        
        user_prompt = f"""Verify this real estate agent: {lister_name}
        Provide:
        1. Full name and agency
        2. Contact details
        3. Property listings
        4. Platform profiles
        5. Reviews and ratings"""
        
        completion = self.xai_client.chat.completions.create(
            model="grok-beta",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
        )
        
        return completion.choices[0].message.content

    def _get_openai_verification(self, lister_name: str) -> Dict:
        prompt = f"""Analyze this real estate agent's online presence: {lister_name}
        Provide a detailed analysis covering:
        1. Overall credibility (express as a percentage)
        2. Years of experience
        3. Areas of specialization
        4. Any concerning factors or red flags
        
        Format your response as a clear, professional summary."""
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a real estate agent validator. Provide clear, concise assessments."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content

    def _generate_validation_data(self) -> Dict:
        """Generates the final validation data structure"""
        return {
            'agent_verification': self.agent_validation_data
        }

    def _generate_error_data(self, error_message: str) -> Dict:
        return {
            'agent_verification': {
                'lister_verification': 'Verification unavailable',
                'verification_source': 'None',
                'lister_name': 'Unknown',
                'error': error_message,
                'processed_at': str(datetime.now())
            }
        }
