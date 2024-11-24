from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

class ListingStatus(Enum):
    AUTO_APPROVE = "AUTO_APPROVE"
    MANUAL_CHECK = "MANUAL_CHECK"
    AUTO_REJECT = "AUTO_REJECT"

@dataclass
class ImageValidationMetrics:
    valid_count: int
    duplicate_count: int
    suspicious_count: int
    total_count: int

@dataclass
class AgentVerificationMetrics:
    is_verified: bool
    has_license: bool
    has_reviews: bool
    total_checks_passed: int

@dataclass
class CrossPlatformMetrics:
    consistent_count: int
    inconsistent_count: int
    total_platforms: int

class QualitativeTrustScorer:
    def __init__(self):
        self.recent_scores = []
        self.score_window = 100
        
        self.weights = {
            'image_validation': 35,
            'agent_verification': 35,
            'cross_platform': 30
        }
        
        self.thresholds = {
            'auto_approve': 80,
            'manual_check': 40
        }

    def evaluate_listing(self, image_validation: str, agent_verification: Dict, 
                        cross_platform: str) -> Dict:
        """Main entry point for listing evaluation"""
        image_metrics = image_validation
        agent_metrics = self._convert_to_agent_metrics(agent_verification)
        platform_metrics = cross_platform
        
        component_scores = {
            'image_validation': self._calculate_image_score(image_metrics),
            'agent_verification': self._calculate_agent_score(agent_metrics),
            'cross_platform': self._calculate_platform_score(platform_metrics)
        }
        
        total_score = self._calculate_total_score(component_scores)
        status = self._determine_status(total_score)
        
        return {
            'total_score': total_score,
            'status': status,
            'assessment': self._generate_assessment(component_scores),
            'component_evaluations': component_scores,
            'summary': self._generate_summary({'total_score': total_score, 'status': status, 'component_scores': component_scores}),
            'recommendations': self._generate_recommendations({'trust_score': {'total_score': total_score, 'component_scores': component_scores}}),
            'missing_components': self._check_missing_components(image_validation, agent_verification, cross_platform)
        }

    def _calculate_image_score(self, metrics: ImageValidationMetrics) -> Dict:
        """Calculate rule-based image validation score"""
        if metrics.total_count == 0:
            return {'score': 0, 'assessment': 'No images provided'}
            
        valid_ratio = metrics.valid_count / metrics.total_count
        duplicate_penalty = (metrics.duplicate_count / metrics.total_count) * 0.5
        suspicious_penalty = (metrics.suspicious_count / metrics.total_count)
        
        score = (valid_ratio * 100) - (duplicate_penalty * 100) - (suspicious_penalty * 100)
        score = max(0, min(100, score))
        
        assessment = self._get_image_assessment(score, metrics)
        return {'score': score, 'assessment': assessment}

    def _calculate_agent_score(self, metrics: AgentVerificationMetrics) -> Dict:
        """Calculate rule-based agent verification score"""
        base_score = 0
        if metrics.is_verified:
            base_score += 50
        if metrics.has_license:
            base_score += 30
        if metrics.has_reviews:
            base_score += 20
            
        score = min(100, base_score * (metrics.total_checks_passed / 3))
        assessment = self._get_agent_assessment(score, metrics)
        return {'score': score, 'assessment': assessment}

    def _calculate_platform_score(self, metrics: CrossPlatformMetrics) -> Dict:
        """Calculate rule-based cross-platform score"""
        if metrics.total_platforms == 0:
            return {'score': 0, 'assessment': 'No cross-platform data available'}
            
        consistency_ratio = metrics.consistent_count / metrics.total_platforms
        score = consistency_ratio * 100
        
        assessment = self._get_platform_assessment(score, metrics)
        return {'score': score, 'assessment': assessment}

    def _calculate_total_score(self, component_scores: Dict) -> float:
        """Calculate weighted total score using fixed weights"""
        # Filter out components with None or 0 scores
        valid_components = {
            comp: scores for comp, scores in component_scores.items() 
            if scores and scores.get('score') is not None
        }
        
        if not valid_components:
            return 0
        
        # Calculate weighted sum with fixed weights
        total_score = sum(
            self.weights.get(component, 0.25) * scores.get('score', 0)
            for component, scores in valid_components.items()
        )
        
        return round(total_score, 2)

    def _determine_status(self, total_score: float) -> ListingStatus:
        """Determine listing status based on total score"""
        if total_score >= self.thresholds['auto_approve']:
            return ListingStatus.AUTO_APPROVE
        elif total_score >= self.thresholds['manual_check']:
            return ListingStatus.MANUAL_CHECK
        else:
            return ListingStatus.AUTO_REJECT

    def _generate_assessment(self, component_scores: Dict) -> str:
        """Generate detailed safety report based on component scores"""
        assessment = ""
        for component, evaluation in component_scores.items():
            assessment += f"=== {component.replace('_', ' ').title()} ===\n"
            assessment += f"{evaluation['assessment']}\n"
            assessment += f"Score: {evaluation['score']}/100\n\n"
        
        return assessment

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

    def _check_missing_components(self, image_validation: Dict, agent_verification: Dict, 
                        cross_platform: Dict) -> List[str]:
        """Check for missing components and return a list of missing components"""
        missing_components = []
        if not image_validation or 'image_validation_data' not in image_validation:
            missing_components.append("image_validation")
        if not agent_verification or 'agent_verification' not in agent_verification:
            missing_components.append("agent_verification")
        if not cross_platform or 'cross_platform' not in cross_platform:
            missing_components.append("cross_platform")
        
        return missing_components

    def _convert_to_image_metrics(self, data: str) -> ImageValidationMetrics:
        """Convert image validation string output to metrics"""
        try:
            # Default values
            metrics = {'valid': 0, 'duplicates': 0, 'suspicious': 0, 'total': 0}
            
            # Parse the validation string output
            if isinstance(data, str):
                for line in data.split('\n'):
                    if 'Valid images:' in line:
                        metrics['valid'] = int(line.split(':')[1].strip())
                    elif 'Duplicate images:' in line:
                        metrics['duplicates'] = int(line.split(':')[1].strip())
                    elif 'Suspicious images:' in line:
                        metrics['suspicious'] = int(line.split(':')[1].strip())
                    elif 'Total images processed:' in line:
                        metrics['total'] = int(line.split(':')[1].strip())
            
            return ImageValidationMetrics(
                valid_count=metrics['valid'],
                duplicate_count=metrics['duplicates'],
                suspicious_count=metrics['suspicious'],
                total_count=metrics['total'] or sum([metrics['valid'], metrics['duplicates'], metrics['suspicious']])
            )
        except Exception:
            return ImageValidationMetrics(0, 0, 0, 0)

    def _convert_to_agent_metrics(self, data: Dict) -> AgentVerificationMetrics:
        """Convert agent verification data to metrics"""
        try:
            if not data or 'agent_verification' not in data:
                return AgentVerificationMetrics(False, False, False, 0)
            
            verification_data = data['agent_verification']
            verification_text = verification_data.get('lister_verification', '')
            additional_checks = verification_data.get('additional_checks', '')
            
            # Extract metrics from verification text
            is_verified = 'verified' in verification_text.lower() and 'unavailable' not in verification_text.lower()
            has_license = 'license' in verification_text.lower() or 'licensed' in verification_text.lower()
            has_reviews = 'review' in str(additional_checks).lower()
            total_checks = sum([
                is_verified,
                has_license,
                has_reviews,
                'experience' in str(additional_checks).lower(),
                'specialization' in str(additional_checks).lower()
            ])
            
            return AgentVerificationMetrics(
                is_verified=is_verified,
                has_license=has_license,
                has_reviews=has_reviews,
                total_checks_passed=total_checks
            )
        except Exception:
            return AgentVerificationMetrics(False, False, False, 0)

    def _convert_to_platform_metrics(self, data: Dict) -> CrossPlatformMetrics:
        """Convert cross-platform consistency data to metrics"""
        try:
            if not data:
                return CrossPlatformMetrics(0, 0, 0)
            
            # Extract metrics from text/dict data
            consistent = len([k for k, v in data.items() if isinstance(v, (list, dict)) and 'consistent' in k.lower()])
            inconsistent = len([k for k, v in data.items() if isinstance(v, (list, dict)) and 'inconsistent' in k.lower()])
            total = consistent + inconsistent or len(data.keys())
            
            return CrossPlatformMetrics(
                consistent_count=consistent,
                inconsistent_count=inconsistent,
                total_platforms=total
            )
        except Exception:
            return CrossPlatformMetrics(0, 0, 0)

    def _get_image_assessment(self, score: float, metrics: ImageValidationMetrics) -> str:
        """Get image validation assessment based on score and metrics"""
        if metrics.suspicious_count > 0:
            return "CRITICAL: Presence of suspicious images"
        elif metrics.duplicate_count > 0:
            return "Moderate concerns: Presence of duplicates"
        elif metrics.suspicious_count > 0:
            return "Moderate concerns: Presence of suspicious images"
        else:
            return "Good quality with proper validation"

    def _get_agent_assessment(self, score: float, metrics: AgentVerificationMetrics) -> str:
        """Get agent verification assessment based on score and metrics"""
        if not metrics.is_verified:
            return "Failed verification"
        elif not metrics.has_license:
            return "Incomplete verification requiring checks"
        elif not metrics.has_reviews:
            return "Incomplete verification requiring checks"
        else:
            return "Verified with varying degrees of confidence"

    def _get_platform_assessment(self, score: float, metrics: CrossPlatformMetrics) -> str:
        """Get cross-platform consistency assessment based on score and metrics"""
        if metrics.inconsistent_count > 0:
            return "CRITICAL: Major inconsistencies found across platforms"
        elif metrics.inconsistent_count > 0:
            return "Minor inconsistencies requiring verification"
        else:
            return "Consistent across platforms"
