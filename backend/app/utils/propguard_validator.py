import requests
from langchain_community.utilities import GoogleSearchAPIWrapper
from langchain_community.tools import Tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from typing import Dict, List
import json

from PIL import Image
from io import BytesIO
import imagehash
from openai import OpenAI
from app.utils.propguard_scorer import QualitativeTrustScorer
from datetime import datetime

class RealEstateSafetyAgent:
    def __init__(self, openai_api_key: str, google_api_key: str, google_cse_id: str, xai_api_key: str):
        # Initialize the LLM
        self.llm = ChatOpenAI(
            temperature=0,
            model="gpt-4",
            openai_api_key=openai_api_key
        )
        
        # Initialize tools
        self.search = GoogleSearchAPIWrapper(
            google_api_key=google_api_key,
            google_cse_id=google_cse_id
        )
        
        # Add XAI client initialization
        self.xai_client = OpenAI(
            api_key=xai_api_key,
            base_url="https://api.x.ai/v1",
        )
        
        # Create tools list
        self.tools = [
            Tool(
                name="Search",
                func=self.search.run,
                description="Useful for searching information about properties and listings online"
            ),
            Tool(
                name="ValidateImages",
                func=self.validate_images,
                description="Validates property images for authenticity"
            ),
            Tool(
                name="AnalyzeSentiment",
                func=self.analyze_sentiment,
                description="Analyzes sentiment from property reviews"
            ),
            Tool(
                name="VerifyLister",
                func=self.verify_lister,
                description="Verifies real estate lister information across platforms"
            )
        ]
        
        # Create the agent
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self._create_prompt()
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3
        )
        
        # Update scorer initialization with error handling
        try:
            self.scorer = QualitativeTrustScorer(self.llm)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize scorer: {str(e)}")

    def validate_listing(self, listing_data: Dict) -> Dict:
        """Main method to validate a real estate listing"""
        try:
            # Input validation
            valid_property_types = ["house", "apartment", "condominium"]
            if listing_data.get('property_type') not in valid_property_types:
                raise ValueError(f"Property type must be one of: {', '.join(valid_property_types)}")
            
            required_fields = [
                'property_name', 'property_type', 'location', 'lot_area', 
                'floor_area', 'bedrooms', 'bathrooms', 'price', 'lister_name'
            ]
            
            missing_fields = [field for field in required_fields if field not in listing_data]
            if missing_fields:
                raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
            
            # Get agent results
            input_data = f"Please analyze this property listing: {json.dumps(listing_data)}"
            agent_result = self.agent_executor.invoke({"input": input_data})
            
            # Transform agent output for scorer
            validation_data = self._transform_agent_output(agent_result)
            
            # Add validation data safety checks
            if not self._is_validation_data_complete(validation_data):
                validation_data = self._fill_missing_validation_data(validation_data)
            
            # Get scored results with error handling
            try:
                scored_results = self.scorer.evaluate_listing(validation_data)
            except Exception as e:
                print(f"Scoring error: {str(e)}")
                scored_results = self._generate_fallback_score()
            
            return {
                'input_data': listing_data,
                'validation_data': validation_data,
                'trust_assessment': scored_results,
                'timestamp': str(datetime.now()),
                'status': 'SUCCESS'
            }
        except Exception as e:
            return {
                'error': str(e),
                'status': 'FAILED',
                'timestamp': str(datetime.now()),
                'partial_data': locals().get('validation_data', {})
            }

    def validate_images(self, image_urls: List[str]) -> Dict:
        """Validates images for authenticity and duplicates"""
        results = {
            'duplicates': [],
            'suspicious': [],
            'valid': [],
            'metadata_issues': []
        }
        
        image_hashes = []
        
        for url in image_urls:
            try:
                response = requests.get(url)
                img = Image.open(BytesIO(response.content))
                img_hash = str(imagehash.average_hash(img))
                
                # Check for duplicates
                if any(self._is_similar(img_hash, h) for h in image_hashes):
                    results['duplicates'].append(url)
                else:
                    results['valid'].append(url)
                    image_hashes.append(img_hash)
                    
            except Exception as e:
                results['suspicious'].append({'url': url, 'error': str(e)})
                
        return results

    def analyze_sentiment(self, reviews: List[str]) -> Dict:
        """Analyzes sentiment from property reviews"""
        analysis_prompt = """
        Analyze the sentiment of these reviews and provide:
        1. Overall sentiment score (0-1)
        2. Key positive points
        3. Key negative points
        4. Potential red flags
        
        Reviews: {reviews}
        """
        
        result = self.llm.invoke(analysis_prompt.format(reviews=reviews))
        return json.loads(result.content)

    def verify_lister(self, lister_name: str) -> Dict:
        """Verifies lister information across real estate platforms"""
        system_prompt = """You are a knowledgeable and efficient real estate assistant AI, designed to help users verify and gather detailed information about real estate listers. Users will input the name of a lister, and your role is to search across multiple trusted real estate websites, such as Lamudi, to provide comprehensive details about the lister."""

        user_prompt = f"""
        I'm looking for information about a real estate lister named {lister_name}. Can you search across real estate websites and provide:
        1. Full name and associated agency
        2. Contact details
        3. Property listings
        4. Platform profile links
        5. Reviews and ratings
        Please provide concrete, verifiable data.
        """

        completion = self.xai_client.chat.completions.create(
            model="grok-beta",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
        )

        return {
            'lister_verification': completion.choices[0].message.content,
            'verification_source': 'X.AI Grok Model'
        }

    def _is_similar(self, hash1: str, hash2: str, threshold: int = 8) -> bool:
        """Checks if two image hashes are similar"""
        return sum(c1 != c2 for c1, c2 in zip(hash1, hash2)) < threshold

    def _extract_platforms(self, search_results: str) -> List[str]:
        """Extracts platform names from search results"""
        common_platforms = ['zillow', 'trulia', 'realtor.com', 'redfin', 'facebook marketplace']
        found_platforms = []
        
        for platform in common_platforms:
            if platform.lower() in search_results.lower():
                found_platforms.append(platform)
                
        return found_platforms

    def _create_prompt(self) -> PromptTemplate:
        """Creates the agent prompt template"""
        return PromptTemplate.from_template(
            """You are a real estate safety expert AI agent. Your goal is to validate property 
            listings and identify potential fraud or suspicious activity.
            
            You have access to the following tools:
            {tools}
            
            Available tool names: {tool_names}
            
            Analyze the given property listing using the available tools and collect the following data:
            1. Property Details:
               - Property Name and Type verification
               - Location verification
               - Area measurements verification
               - Room count verification
               - Price data
            2. Image analysis results
            3. Review analysis
            4. Lister verification results
            
            Property listing: {input}
            
            Think through this step-by-step:
            1. Collect and verify property details
            2. Run image validation
            3. Analyze available reviews
            4. Verify lister information
            5. Return all collected data
            
            Return your response in the following JSON format:s
            {{
                "images": [...],
                "reviews": [...],
                "lister_name": "...",
                "search_results": "...",
                "price_variations": [...],
                "detail_mismatches": [...]
            }}
            
            {agent_scratchpad}
            """
        )

    def _transform_agent_output(self, agent_result: Dict) -> Dict:
        """Transform agent output into scorer-compatible format"""
        try:
            # Parse agent output if it's a string
            if isinstance(agent_result, str):
                agent_result = json.loads(agent_result)
            
            # Extract relevant data
            images = agent_result.get('images', [])
            reviews = agent_result.get('reviews', [])
            lister_name = agent_result.get('lister_name', '')
            search_results = agent_result.get('search_results', '')
            
            # Format data for scorer
            validation_data = {
                'image_validation': {
                    'valid_count': len(self.validate_images(images).get('valid', [])),
                    'duplicate_count': len(self.validate_images(images).get('duplicates', [])),
                    'suspicious_count': len(self.validate_images(images).get('suspicious', [])),
                    'total_images': len(images),
                    'processed_at': str(datetime.now()),
                    'validation_results': self.validate_images(images)  # Add full results
                },
                'review_analysis': {
                    'sentiment_results': self.analyze_sentiment(reviews),
                    'total_reviews': len(reviews),
                    'source_platforms': self._extract_platforms(search_results),
                    'reviews': reviews  # Add original reviews
                },
                'agent_verification': {
                    **self.verify_lister(lister_name),
                    'lister_name': lister_name  # Add original name
                },
                'cross_platform': {
                    'platforms': self._extract_platforms(search_results),
                    'consistency_score': self._calculate_consistency_score(agent_result),
                    'details_match': True,
                    'search_results': search_results  # Add original search results
                }
            }
            return validation_data
        except Exception as e:
            print(f"Error transforming agent output: {str(e)}")
            return {}

    def _calculate_consistency_score(self, agent_result: Dict) -> float:
        """Calculates a consistency score based on cross-platform data"""
        prompt = f"""
        Analyze these cross-platform listing results and provide a consistency score (0.0-1.0):
        
        Search Results: {agent_result.get('search_results', '')}
        Price Variations: {agent_result.get('price_variations', [])}
        Detail Mismatches: {agent_result.get('detail_mismatches', [])}
        
        Consider:
        - Number of platforms where listing appears
        - Consistency of pricing across platforms
        - Consistency of property details
        - Overall data quality
        
        Provide a single float value between 0.0 and 1.0 representing the consistency score.
        """
        
        try:
            response = self.llm.invoke(prompt)
            score = float(response.content.strip())
            return max(0.0, min(1.0, score))  # Ensure score is between 0 and 1
        except Exception as e:
            print(f"Error calculating consistency score: {str(e)}")
            return 0.5  # Return moderate score on error

    def _is_validation_data_complete(self, data: Dict) -> bool:
        """Verifies if all required validation data fields are present"""
        required_sections = {
            'image_validation': ['valid_count', 'duplicate_count', 'suspicious_count', 'total_images'],
            'review_analysis': ['sentiment_results', 'total_reviews'],
            'agent_verification': ['lister_verification', 'lister_name'],
            'cross_platform': ['consistency_score', 'details_match']
        }
        
        try:
            for section, fields in required_sections.items():
                if section not in data:
                    return False
                for field in fields:
                    if field not in data[section]:
                        return False
            return True
        except Exception:
            return False

    def _fill_missing_validation_data(self, data: Dict) -> Dict:
        """Fills in missing validation data with safe default values"""
        default_structure = {
            'image_validation': {
                'valid_count': 0,
                'duplicate_count': 0,
                'suspicious_count': 0,
                'total_images': 0,
                'processed_at': str(datetime.now()),
                'validation_results': {}
            },
            'review_analysis': {
                'sentiment_results': {},
                'total_reviews': 0,
                'source_platforms': [],
                'reviews': []
            },
            'agent_verification': {
                'lister_verification': 'Verification unavailable',
                'verification_source': 'None',
                'lister_name': 'Unknown'
            },
            'cross_platform': {
                'platforms': [],
                'consistency_score': 0.0,
                'details_match': False,
                'search_results': ''
            }
        }

        # Merge existing data with defaults
        for section in default_structure:
            if section not in data:
                data[section] = default_structure[section]
            else:
                for field in default_structure[section]:
                    if field not in data[section]:
                        data[section][field] = default_structure[section][field]

        return data

    def _generate_fallback_score(self) -> Dict:
        """Generates a fallback score when scoring fails"""
        return {
            'trust_score': 0.0,
            'confidence': 'LOW',
            'warning': 'Fallback score generated due to scoring error',
            'timestamp': str(datetime.now())
        }

# Initialize the agent
# agent = RealEstateSafetyAgent(
#     openai_api_key="", 
#     google_api_key="", 
#     google_cse_id="", 
#     xai_api_key=""
# )

# listing_data = {
#     "property_name": "4 STOREY TOWNHOUSE FOR SALE IN KAMUNING QUEZON CITY",
#     "property_type": "House",  # Must be one of: House, Apartment, Condominium
#     "location": "Kamuning, Quezon City",
#     "lot_area": 80,  # in square meters
#     "floor_area": 121,  # in square meters
#     "bedrooms": 4,
#     "bathrooms": 5,
#     "price": 17000000,
#     "images": ["https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.rocketmortgage.com%2Flearn%2Freal-property&psig=AOvVaw3P5J9i0k4hWIYzhf5qc4Dh&ust=1732362923708000&source=images&cd=vfe&opi=89978449&ved=0CBQQjRxqFwoTCJCp7ffw74kDFQAAAAAdAAAAABAE"],
#     "reviews": ["Professional and responsive, Jeffrey provided detailed answers to my inquiries and accommodated multiple viewing schedules. Highly recommended!!", "Good listings, but some negotiations took longer than expected. Otherwise, a smooth transaction."],
#     "lister_name": "Jeffrey Lock"
# }

# # Validate the listing
# results = agent.validate_listing(listing_data)
# print(results)