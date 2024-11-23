from typing import List, Dict
from datetime import datetime
import openai
import os

class ReviewValidator:
    def __init__(self, openai_api_key: str = None):
        self.api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        self.review_validation_data = {
            'sentiment_results': {},
            'reviews': [],
            'processed_at': None,
            'total_reviews': 0
        }

    def analyze_reviews(self, reviews: List[str]) -> Dict:
        """Analyzes sentiment from property reviews"""
        try:
            analysis_prompt = self._create_analysis_prompt(reviews)
            sentiment_results = self._get_sentiment_analysis(analysis_prompt)
            
            self.review_validation_data.update({
                'sentiment_results': sentiment_results,
                'reviews': reviews,
                'total_reviews': len(reviews),
                'processed_at': str(datetime.now())
            })
            
            return self._generate_validation_data()
            
        except Exception as e:
            return self._generate_error_data(str(e))

    def _create_analysis_prompt(self, reviews: List[str]) -> str:
        return f"""Analyze these property reviews and provide a JSON response with:
        1. overall_sentiment_score (0-1)
        2. key_positive_points (list)
        3. key_negative_points (list)
        4. potential_red_flags (list)

        Reviews: {' | '.join(reviews)}"""

    def _get_sentiment_analysis(self, prompt: str) -> Dict:
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a real estate review analyst."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json" }
        )
        return response.choices[0].message.content

    def _generate_validation_data(self) -> Dict:
        """Generates the final validation data structure"""
        return {
            'review_analysis': self.review_validation_data
        }

    def _generate_error_data(self, error_message: str) -> Dict:
        return {
            'review_analysis': {
                'sentiment_results': {},
                'total_reviews': 0,
                'error': error_message,
                'processed_at': str(datetime.now())
            }
        }

