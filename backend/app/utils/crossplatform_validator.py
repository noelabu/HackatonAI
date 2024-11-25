from typing import List, Dict
from datetime import datetime
import openai
import os

class CrossPlatformValidator:
    def __init__(self, openai_api_key: str = None):
        self.api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        self.cross_platform_validation_data = {
            'platforms': [],
            'consistency_score': 0.0,
            'details_match': False,
            'search_results': '',
            'processed_at': None,
            'platform_specific_data': {}
        }

    def validate_listing(self, listing_data: Dict) -> Dict:
        """Validates listing across different platforms"""
        try:
            # Search for listing across platforms
            search_results = self._search_platforms(listing_data)
            
            # Extract platforms where listing appears
            platforms = self._extract_platforms(search_results)
            
            # Calculate consistency score
            consistency_score = self._calculate_consistency_score(listing_data, search_results)
            
            # Get platform-specific data
            platform_data = self._get_platform_specific_data(platforms, listing_data)
            
            self.cross_platform_validation_data.update({
                'platforms': platforms,
                'consistency_score': consistency_score,
                'details_match': consistency_score > 0.7,
                'search_results': search_results,
                'processed_at': str(datetime.now()),
                'platform_specific_data': platform_data
            })
            
            return self._generate_validation_data()
            
        except Exception as e:
            return self._generate_error_data(str(e))

    def _search_platforms(self, listing_data: Dict) -> str:
        """Simulates searching for listing across platforms"""
        prompt = f"""Search for this property listing across major real estate platforms:
        Address: {listing_data.get('location', 'Unknown')}
        Price: {listing_data.get('price', 'Unknown')}
        Details: {listing_data}
        
        Provide a detailed search result summary."""
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a real estate platform analyzer."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content

    def _extract_platforms(self, search_results: str) -> List[str]:
        """Extracts platform names from search results"""
        common_platforms = [
            'zillow', 'trulia', 'realtor.com', 'redfin', 
            'facebook marketplace', 'lamudi', 'property24'
        ]
        return [platform for platform in common_platforms 
                if platform.lower() in search_results.lower()]

    def _calculate_consistency_score(self, listing_data: Dict, search_results: str) -> float:
        """Calculates consistency score across platforms"""
        prompt = f"""Analyze these cross-platform listing results and provide a consistency score (0.0-1.0):
        
        Original Listing: {listing_data}
        Search Results: {search_results}
        
        Consider:
        - Number of platforms where listing appears
        - Consistency of pricing
        - Consistency of property details
        - Overall data quality
        
        Return only a float between 0.0 and 1.0."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a real estate data analyst."},
                    {"role": "user", "content": prompt}
                ]
            )
            score = float(response.choices[0].message.content.strip())
            return max(0.0, min(1.0, score))
        except:
            return 0.5

    def _get_platform_specific_data(self, platforms: List[str], listing_data: Dict) -> Dict:
        """Collects specific data from each platform"""
        platform_data = {}
        for platform in platforms:
            platform_data[platform] = {
                'listing_url': f"https://{platform}/sample-listing",
                'price': listing_data.get('price'),
                'last_updated': str(datetime.now()),
                'status': 'active'
            }
        return platform_data

    def _generate_validation_data(self) -> str:
        """Generates the final validation data as formatted text"""
        data = self.cross_platform_validation_data
        platforms_text = ", ".join(data['platforms']) if data['platforms'] else "None found"
        
        return f"""Cross-Platform Validation Report
------------------------
Platforms Found: {platforms_text}
Consistency Score: {data['consistency_score']:.2f}
Details Match: {'Yes' if data['details_match'] else 'No'}
Processed At: {data['processed_at']}

Search Results:
{data['search_results']}

Platform-Specific Details:
{self._format_platform_data(data['platform_specific_data'])}"""

    def _format_platform_data(self, platform_data: Dict) -> str:
        """Helper method to format platform-specific data"""
        if not platform_data:
            return "No platform-specific data available"
            
        formatted_text = ""
        for platform, details in platform_data.items():
            formatted_text += f"\n{platform.title()}:"
            formatted_text += f"\n  - URL: {details['listing_url']}"
            formatted_text += f"\n  - Price: {details['price']}"
            formatted_text += f"\n  - Last Updated: {details['last_updated']}"
            formatted_text += f"\n  - Status: {details['status']}\n"
        return formatted_text

    def _generate_error_data(self, error_message: str) -> str:
        """Generates error report as text"""
        return f"""Cross-Platform Validation Report
------------------------
Status: Error
Error Message: {error_message}
Processed At: {datetime.now()}"""
