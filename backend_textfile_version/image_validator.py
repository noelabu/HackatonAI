import requests
from PIL import Image
from io import BytesIO
import imagehash
from typing import List, Dict
from datetime import datetime

class ImageValidator:
    def __init__(self):
        self.image_validation_data = {
            'duplicates': [],
            'suspicious': [],
            'valid': [],
            'metadata_issues': [],
            'processed_at': None
        }
    
    def validate_images(self, image_urls: List[str]) -> Dict:
        """Validates images for authenticity and duplicates"""
        image_hashes = []
        
        for url in image_urls:
            try:
                response = requests.get(url)
                img = Image.open(BytesIO(response.content))
                img_hash = str(imagehash.average_hash(img))
                
                if any(self._is_similar(img_hash, h) for h in image_hashes):
                    self.image_validation_data['duplicates'].append(url)
                else:
                    self.image_validation_data['valid'].append(url)
                    image_hashes.append(img_hash)
                    
            except Exception as e:
                self.image_validation_data['suspicious'].append({'url': url, 'error': str(e)})
        
        self.image_validation_data['processed_at'] = str(datetime.now())
        return self._generate_validation_data()
    
    def _is_similar(self, hash1: str, hash2: str, threshold: int = 8) -> bool:
        """Checks if two image hashes are similar"""
        return sum(c1 != c2 for c1, c2 in zip(hash1, hash2)) < threshold
    
    def _generate_validation_data(self) -> str:
        """Generates the final validation data as a formatted text string"""
        return (
            f"Image Validation Results:\n"
            f"- Valid images: {len(self.image_validation_data['valid'])}\n"
            f"- Duplicate images: {len(self.image_validation_data['duplicates'])}\n"
            f"- Suspicious images: {len(self.image_validation_data['suspicious'])}\n"
            f"- Total images processed: {len(self.image_validation_data['valid']) + len(self.image_validation_data['duplicates']) + len(self.image_validation_data['suspicious'])}\n"
            f"- Processed at: {self.image_validation_data['processed_at']}"
        )