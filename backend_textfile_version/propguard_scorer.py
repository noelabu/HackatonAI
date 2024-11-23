from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
from langchain_openai import ChatOpenAI

class ListingStatus(Enum):
    AUTO_APPROVE = "AUTO_APPROVE"
    MANUAL_CHECK = "MANUAL_CHECK"
    AUTO_REJECT = "AUTO_REJECT"

class QualitativeTrustScorer:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.recent_scores = []  # Track recent scores for dynamic thresholds
        self.score_window = 100  # Keep last 100 scores
        
    def evaluate_listing(self, image_validation: Dict, review_analysis: Dict, 
                        agent_verification: Dict, cross_platform: Dict) -> Dict:
        """Main entry point for listing evaluation"""
        # Convert structured data to formatted strings
        validation_data = {
            'image_validation': self._format_image_validation(image_validation),
            'review_analysis': self._format_review_analysis(review_analysis),
            'agent_verification': self._format_agent_verification(agent_verification),
            'cross_platform': cross_platform  # Already a formatted string from CrossPlatformValidator
        }
        
        # Check for empty or invalid inputs
        missing_components = [comp for comp, value in validation_data.items() 
                            if not value or 'error' in value.lower()]
        
        if missing_components:
            return {
                'total_score': 0,
                'status': ListingStatus.MANUAL_CHECK,
                'assessment': f'Missing or invalid components: {", ".join(missing_components)}',
                'error': 'Incomplete validation data'
            }
        
        try:
            # Format validation data for the prompt
            formatted_data = "\n\n".join([
                f"=== {comp.replace('_', ' ').title()} ===\n{data}" 
                for comp, data in validation_data.items()
            ])
            
            prompt = """Analyze this property listing data and provide a detailed safety report:
            
            {formatted_data}
            
            Provide a detailed safety report including:
            1. Property Details Validation:
               - Property Name and Type (House, Apartment, or Condominium)
               - Location
               - Lot Area and Floor Area measurements
               - Number of Bedrooms and Bathrooms
               - Price reasonability for the given specifications and property type
            2. Image validation assessment
            3. Review sentiment analysis
            4. Lister verification assessment
            5. Overall trust score
            6. Potential red flags
            
            Think through this step-by-step:
            1. First, validate the property details, type, and pricing
            2. Check if the number of bedrooms and bathrooms is reasonable for the floor area
            3. Assess the image validation results
            4. Evaluate the review analysis
            5. Consider the lister verification
            6. Synthesize all information for a final assessment
            """
            
            # Get initial assessment
            assessment = self.llm.invoke(prompt.format(formatted_data=formatted_data))
            
            # Evaluate components
            component_scores = {
                'image_validation': self.evaluate_images(validation_data['image_validation']),
                'review_analysis': self.evaluate_reviews(validation_data['review_analysis']),
                'agent_verification': self.evaluate_agent(validation_data['agent_verification']),
                'cross_platform': self.evaluate_cross_platform(validation_data['cross_platform'])
            }
            
            # Get final status
            final_assessment = self.determine_listing_status(component_scores)
            
            return {
                'total_score': final_assessment['confidence'],
                'status': final_assessment['status'],
                'assessment': final_assessment['assessment'],
                'component_evaluations': component_scores,
                'summary': self._generate_summary(validation_data),
                'recommendations': self._generate_recommendations(validation_data)
            }
        except Exception as e:
            return {
                'total_score': 0,
                'status': ListingStatus.MANUAL_CHECK,
                'assessment': f'Error during evaluation: {str(e)}',
                'error': str(e)
            }

    def evaluate_images(self, image_results: str) -> Dict:
        """Qualitatively evaluate image validation results"""
        prompt = f"""
        Analyze these property listing image validation results:
        {image_results}

        Provide exactly two lines in your response:
        1. A concise assessment (1-2 sentences) focusing on:
           - Ratio of valid to suspicious images
           - Presence of duplicates
           - Image quality and metadata completeness
           - Any critical red flags
        2. A trust score (0-100) where:
           0-29: Critical issues (missing/suspicious images)
           30-69: Moderate concerns (incomplete/low quality)
           70-100: Good quality with proper validation

        Format:
        <assessment>
        score: <number>
        """
        
        response = self.llm.invoke(prompt)
        return self._parse_component_response(response.content)

    def evaluate_reviews(self, review_results: str) -> Dict:
        """Qualitatively evaluate review analysis results"""
        prompt = f"""
        Analyze these property listing review results:
        {review_results}

        Provide exactly two lines in your response:
        1. A concise assessment (1-2 sentences) focusing on:
           - Overall sentiment patterns
           - Review authenticity indicators
           - Specificity of feedback
           - Any critical red flags
        2. A trust score (0-100) where:
           0-29: Critical issues (significant negative patterns)
           30-59: Mixed reviews requiring investigation
           60-100: Predominantly positive legitimate reviews

        Format:
        <assessment>
        score: <number>
        """
        
        response = self.llm.invoke(prompt)
        return self._parse_component_response(response.content)

    def evaluate_agent(self, agent_results: str) -> Dict:
        """Qualitatively evaluate agent verification results"""
        prompt = f"""
        Analyze these agent verification results:
        {agent_results}

        Provide exactly two lines in your response:
        1. A concise assessment (1-2 sentences) focusing on:
           - Verification status across platforms
           - Consistency of professional information
           - Credential validation
           - Any critical red flags
        2. A trust score (0-100) where:
           0: Failed verification
           1-49: Incomplete verification requiring checks
           50-100: Verified with varying degrees of confidence

        Format:
        <assessment>
        score: <number>
        """
        
        response = self.llm.invoke(prompt)
        return self._parse_component_response(response.content)

    def evaluate_cross_platform(self, platform_results: str) -> Dict:
        """Qualitatively evaluate cross-platform consistency"""
        prompt = f"""
        Analyze these cross-platform consistency results:
        {platform_results}

        Provide exactly two lines in your response:
        1. A concise assessment (1-2 sentences) focusing on:
           - Consistency of listing details
           - Platform reputation
           - Data completeness
           - Any critical red flags
        2. A trust score (0-100) where:
           0-29: Critical inconsistencies
           30-49: Minor inconsistencies requiring verification
           50-100: Consistent across platforms

        Format:
        <assessment>
        score: <number>
        """
        
        response = self.llm.invoke(prompt)
        return self._parse_component_response(response.content)

    def determine_listing_status(self, component_scores: Dict) -> Dict:
        """Determine listing status based on qualitative assessments"""
        # First, get weighted total score
        total_score = self._calculate_weighted_score(component_scores)
        
        prompt = f"""
        Based on these component evaluations and computed total score:
        
        Component Assessments:
        {component_scores}
        
        Total Score: {total_score}
        
        Recent Score Distribution:
        {self._get_score_distribution()}
        
        Provide:
        1. Overall trust assessment (2-3 sentences)
        2. Recommended status (AUTO_APPROVE, MANUAL_CHECK, or AUTO_REJECT)
        3. Confidence level in the recommendation (0-100)
        4. Uncertainty assessment (HIGH, MEDIUM, LOW)
        
        Consider:
        - Pattern of component scores
        - Presence of any critical concerns
        - Overall consistency of assessments
        - Distribution of recent scores
        - Level of uncertainty in the assessment
        """
        
        response = self.llm.invoke(prompt)
        result = self._parse_status_response(response.content)
        
        # Update score history
        self._update_score_history(total_score)
        
        # Override status if uncertainty is high
        if result.get('uncertainty') == 'HIGH':
            result['status'] = ListingStatus.MANUAL_CHECK
        
        result['confidence'] = total_score  # Use weighted score as confidence
        return result

    def _calculate_weighted_score(self, component_scores: Dict) -> float:
        """Calculate weighted total score using LLM to determine weights"""
        prompt = f"""
        Given these component scores and their assessments:
        {component_scores}
        
        Determine appropriate weights for each component considering:
        - Relative importance of each factor
        - Severity of any issues found
        - Interdependencies between components
        - Overall risk assessment
        
        Provide weights that sum to 1.0 in this exact format:
        image_validation: <weight>
        review_analysis: <weight>
        agent_verification: <weight>
        cross_platform: <weight>
        """
        
        try:
            response = self.llm.invoke(prompt)
            weights = {}
            for line in response.content.strip().split('\n'):
                component, weight = line.split(':')
                weights[component.strip()] = float(weight.strip())
            
            # Calculate weighted sum
            total_score = sum(
                weights.get(component, 0.25) * scores.get('score', 0)
                for component, scores in component_scores.items()
            )
            
            return round(total_score, 2)
        except Exception as e:
            # Fallback to simple average if weight parsing fails
            scores = [scores.get('score', 0) for scores in component_scores.values()]
            return round(sum(scores) / len(scores), 2) if scores else 0

    def _get_score_distribution(self) -> str:
        """Calculate and format recent score distribution"""
        if not self.recent_scores:
            return "No historical data available"
            
        avg = sum(self.recent_scores) / len(self.recent_scores)
        quartiles = {
            'low': sorted(self.recent_scores)[len(self.recent_scores)//4],
            'med': sorted(self.recent_scores)[len(self.recent_scores)//2],
            'high': sorted(self.recent_scores)[3*len(self.recent_scores)//4]
        }
        
        return f"Average: {avg:.1f}, Quartiles: {quartiles}"
        
    def _update_score_history(self, score: float):
        """Update the rolling window of recent scores"""
        self.recent_scores.append(score)
        if len(self.recent_scores) > self.score_window:
            self.recent_scores.pop(0)

    def _parse_component_response(self, response: str) -> Dict:
        """Parse LLM response for component evaluation"""
        try:
            # Basic parsing - you might want to make this more robust
            lines = response.strip().split('\n')
            assessment = lines[0]
            score = float(lines[1].split(':')[1].strip())
            return {
                'assessment': assessment,
                'score': score
            }
        except Exception as e:
            return {
                'assessment': 'Failed to parse response',
                'score': 0,
                'error': str(e)
            }

    def _parse_status_response(self, response: str) -> Dict:
        """Parse LLM response for status determination"""
        try:
            lines = response.strip().split('\n')
            return {
                'assessment': lines[0],
                'status': ListingStatus[lines[1].strip()],
                'confidence': float(lines[2].split(':')[1].strip()),
                'uncertainty': lines[3].strip()
            }
        except Exception as e:
            return {
                'assessment': 'Failed to parse status response',
                'status': ListingStatus.MANUAL_CHECK,
                'confidence': 0,
                'uncertainty': 'HIGH',
                'error': str(e)
            }

    def calculate_trust_score(self, validation_results: Dict) -> Dict:
        """Calculate overall trust score using LLM-based qualitative assessments"""
        # Evaluate each component
        image_evaluation = self.evaluate_images(validation_results.get('image_validation', {}))
        review_evaluation = self.evaluate_reviews(validation_results.get('review_analysis', {}))
        agent_evaluation = self.evaluate_agent(validation_results.get('agent_verification', {}))
        platform_evaluation = self.evaluate_cross_platform(validation_results.get('cross_platform', {}))
        
        component_scores = {
            'image_validation': image_evaluation,
            'review_analysis': review_evaluation,
            'agent_verification': agent_evaluation,
            'cross_platform': platform_evaluation
        }
        
        # Determine final status and score
        final_assessment = self.determine_listing_status(component_scores)
        
        return {
            'total_score': final_assessment['confidence'],
            'status': final_assessment['status'],
            'assessment': final_assessment['assessment'],
            'component_evaluations': component_scores
        }

    def _generate_recommendations(self, validation_data: Dict) -> List[str]:
        """Generates actionable recommendations based on validation results"""
        recommendations = []
        component_scores = validation_data.get('component_evaluations', {})
        total_score = validation_data.get('total_score', 0)
        
        # Add total score as first recommendation
        recommendations.append(f"Overall Trust Score: {total_score}/100")
        
        # Image validation recommendations
        image_score = component_scores.get('image_validation', {}).get('score', 0)
        if image_score < 30:
            recommendations.append("CRITICAL: Insufficient or suspicious property images. Request complete image set and verify authenticity")
        elif image_score < 70:
            recommendations.append("Request additional high-quality property images and verify their authenticity")
        
        # Review analysis recommendations
        review_score = component_scores.get('review_analysis', {}).get('score', 0)
        if review_score < 30:
            recommendations.append("CRITICAL: Significant negative review patterns detected. Conduct thorough investigation")
        elif review_score < 60:
            recommendations.append("Investigate recent negative reviews and verify their legitimacy")
        
        # Agent verification recommendations
        agent_score = component_scores.get('agent_verification', {}).get('score', 0)
        if agent_score <= 0:
            recommendations.append("URGENT: Agent verification failed. Verify credentials and licensing information immediately")
        elif agent_score < 50:
            recommendations.append("Additional agent verification required. Check professional history and credentials")
        
        # Cross-platform recommendations
        platform_score = component_scores.get('cross_platform', {}).get('score', 0)
        if platform_score < 30:
            recommendations.append("CRITICAL: Major inconsistencies found across platforms. Detailed cross-reference check required")
        elif platform_score < 50:
            recommendations.append("Cross-reference listing details across multiple platforms to verify consistency")
        
        # If all scores are good but not excellent, add a general verification recommendation
        if all(30 <= score.get('score', 0) < 80 for score in component_scores.values()):
            recommendations.append("Perform standard verification procedures before proceeding")
        
        # If no specific recommendations are generated, add a general positive note
        if not recommendations and all(score.get('score', 0) >= 80 for score in component_scores.values()):
            recommendations.append("All validation checks passed. Proceed with standard processing")
        
        return recommendations

    def _generate_summary(self, validation_data: Dict) -> str:
        """Generates a human-readable summary of the validation results"""
        total_score = validation_data.get('total_score', 0)
        status = validation_data.get('status', ListingStatus.MANUAL_CHECK)
        
        summary = f"Trust Score: {total_score}/100 - Status: {status.value}\n\n"
        summary += "Component Scores:\n"
        for component, evaluation in validation_data.get('component_evaluations', {}).items():
            score = evaluation.get('score', 0)
            summary += f"- {component.replace('_', ' ').title()}: {score}/100\n"
        
        return summary

    def _format_image_validation(self, data: Dict) -> str:
        """Format image validation data as string"""
        if not data or 'image_validation_data' not in data:
            return ''
        
        data = data['image_validation_data']
        return f"""Image Validation Summary:
        Valid Images: {len(data['valid'])}
        Duplicate Images: {len(data['duplicates'])}
        Suspicious Images: {len(data['suspicious'])}
        Processed At: {data['processed_at']}"""

    def _format_review_analysis(self, data: Dict) -> str:
        """Format review analysis data as string"""
        if not data or 'review_analysis' not in data:
            return ''
        
        data = data['review_analysis']
        return f"""Review Analysis Summary:
        Total Reviews: {data['total_reviews']}
        Sentiment Results: {data['sentiment_results']}
        Processed At: {data['processed_at']}"""

    def _format_agent_verification(self, data: Dict) -> str:
        """Format agent verification data as string"""
        if not data or 'agent_verification' not in data:
            return ''
        
        data = data['agent_verification']
        return f"""Agent Verification Summary:
        Lister: {data['lister_name']}
        Verification Source: {data['verification_source']}
        Verification Result: {data['lister_verification']}
        Additional Checks: {data['additional_checks']}
        Processed At: {data['processed_at']}"""
