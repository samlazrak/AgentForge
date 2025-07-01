"""
Source credibility assessment and bias detection system
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple, Set
from collections import Counter, defaultdict
from urllib.parse import urlparse
import asyncio
from datetime import datetime, timedelta
import json

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logging.warning("Requests not available - credibility assessment limited")

from .research_models import (
    SourceCredibilityScore, BiasAssessment, BiasType, SourceType,
    EnhancedScrapedContent, URLValidationResult
)

class DomainAuthorityDatabase:
    """Database for domain authority scores"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Pre-populated authority scores for common domains
        self.authority_scores = {
            # Academic and Research
            'arxiv.org': 0.95,
            'scholar.google.com': 0.95,
            'pubmed.ncbi.nlm.nih.gov': 0.95,
            'nature.com': 0.9,
            'science.org': 0.9,
            'ieee.org': 0.9,
            'acm.org': 0.9,
            'springer.com': 0.85,
            'elsevier.com': 0.85,
            'wiley.com': 0.85,
            'researchgate.net': 0.75,
            'academia.edu': 0.7,
            
            # Government and Official Organizations
            'gov': 0.9,  # All .gov domains
            'edu': 0.85,  # All .edu domains
            'who.int': 0.9,
            'un.org': 0.85,
            'europa.eu': 0.85,
            'nih.gov': 0.9,
            'nasa.gov': 0.9,
            
            # Major News and Media
            'reuters.com': 0.85,
            'bbc.com': 0.85,
            'ap.org': 0.85,
            'nytimes.com': 0.8,
            'wsj.com': 0.8,
            'economist.com': 0.8,
            'theguardian.com': 0.75,
            'washingtonpost.com': 0.75,
            'cnn.com': 0.7,
            'npr.org': 0.8,
            
            # Technology and Industry
            'techcrunch.com': 0.7,
            'wired.com': 0.75,
            'arstechnica.com': 0.75,
            'stackoverflow.com': 0.8,
            'github.com': 0.8,
            'medium.com': 0.6,
            'dev.to': 0.6,
            'hackernews.ycombinator.com': 0.7,
            
            # Major Tech Companies
            'google.com': 0.8,
            'microsoft.com': 0.8,
            'apple.com': 0.8,
            'amazon.com': 0.75,
            'meta.com': 0.75,
            'facebook.com': 0.75,
            'twitter.com': 0.65,
            'linkedin.com': 0.7,
            
            # Encyclopedias and Reference
            'wikipedia.org': 0.7,
            'britannica.com': 0.8,
            
            # Default scores by TLD
            '.gov': 0.9,
            '.edu': 0.85,
            '.org': 0.6,
            '.com': 0.4,
            '.net': 0.4,
            '.info': 0.3,
            '.blog': 0.3
        }
    
    async def get_domain_authority(self, domain: str) -> float:
        """Get domain authority score"""
        domain = domain.lower()
        
        # Check exact domain match
        if domain in self.authority_scores:
            return self.authority_scores[domain]
        
        # Check subdomain patterns
        for known_domain, score in self.authority_scores.items():
            if domain.endswith('.' + known_domain):
                return score
        
        # Check TLD patterns
        for tld, score in self.authority_scores.items():
            if tld.startswith('.') and domain.endswith(tld):
                return score
        
        # Default score for unknown domains
        return 0.3

class AuthorExpertiseDatabase:
    """Database for author expertise assessment"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Expert patterns and indicators
        self.expertise_indicators = {
            'academic_titles': {
                'patterns': [
                    r'\b(?:Dr\.?|PhD|Ph\.D\.?|Professor|Prof\.?|M\.D\.?|M\.S\.?|M\.A\.?|B\.S\.?|B\.A\.?)\b',
                    r'\b(?:Research(?:er)?|Scientist|Scholar|Fellow)\b'
                ],
                'score': 0.8
            },
            'professional_titles': {
                'patterns': [
                    r'\b(?:CEO|CTO|VP|Director|Manager|Lead|Senior|Principal|Chief)\b',
                    r'\b(?:Engineer|Developer|Architect|Analyst|Consultant)\b'
                ],
                'score': 0.6
            },
            'institutional_affiliation': {
                'patterns': [
                    r'\b(?:University|Institute|Laboratory|Research Center|Department)\b',
                    r'\b(?:Google|Microsoft|Apple|Amazon|Meta|IBM|Intel|NVIDIA)\b'
                ],
                'score': 0.7
            }
        }
    
    async def assess_author_expertise(self, author: str, content: str = "") -> float:
        """Assess author expertise based on name and content"""
        if not author:
            return 0.0
        
        combined_text = f"{author} {content}".lower()
        total_score = 0.0
        indicators_found = 0
        
        for category, info in self.expertise_indicators.items():
            for pattern in info['patterns']:
                if re.search(pattern, combined_text, re.IGNORECASE):
                    total_score += info['score']
                    indicators_found += 1
                    break  # Only count each category once
        
        # Normalize score
        if indicators_found > 0:
            return min(1.0, total_score / max(1, indicators_found))
        else:
            return 0.2  # Default for unknown authors

class BiasDetectionEngine:
    """Engine for detecting various types of bias"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.bias_patterns = self._load_bias_patterns()
    
    def _load_bias_patterns(self) -> Dict[BiasType, Dict[str, Any]]:
        """Load patterns for detecting different types of bias"""
        return {
            BiasType.POLITICAL: {
                'left_indicators': [
                    'progressive', 'liberal', 'democrat', 'left-wing', 'social justice',
                    'equality', 'climate action', 'renewable', 'regulation'
                ],
                'right_indicators': [
                    'conservative', 'republican', 'right-wing', 'traditional values',
                    'free market', 'deregulation', 'small government', 'individual rights'
                ],
                'neutral_indicators': [
                    'bipartisan', 'nonpartisan', 'objective', 'factual', 'balanced'
                ]
            },
            BiasType.COMMERCIAL: {
                'indicators': [
                    'buy now', 'purchase', 'discount', 'sale', 'offer', 'deal',
                    'sponsored', 'advertisement', 'affiliate', 'partner',
                    'recommended product', 'best solution', 'top choice'
                ],
                'commercial_phrases': [
                    'call to action', 'limited time', 'exclusive', 'premium',
                    'upgrade', 'subscription', 'pricing', 'free trial'
                ]
            },
            BiasType.CONFIRMATION: {
                'indicators': [
                    'obviously', 'clearly', 'everyone knows', 'it goes without saying',
                    'undeniably', 'without question', 'certainly', 'definitely',
                    'proves that', 'confirms that', 'validates'
                ]
            },
            BiasType.LANGUAGE: {
                'emotional_language': [
                    'devastating', 'shocking', 'outrageous', 'incredible',
                    'amazing', 'terrible', 'fantastic', 'horrible',
                    'revolutionary', 'groundbreaking', 'catastrophic'
                ],
                'loaded_terms': [
                    'elite', 'establishment', 'mainstream media', 'deep state',
                    'fake news', 'propaganda', 'agenda', 'narrative'
                ]
            }
        }
    
    async def detect_bias(self, content: str, metadata: Dict[str, Any]) -> BiasAssessment:
        """Detect various types of bias in content"""
        assessment = BiasAssessment()
        
        # Detect political bias
        assessment.political_bias = await self._detect_political_bias(content)
        
        # Detect commercial bias
        assessment.commercial_bias = await self._detect_commercial_bias(content, metadata)
        
        # Detect confirmation bias
        assessment.confirmation_bias = await self._detect_confirmation_bias(content)
        
        # Detect language bias
        assessment.language_bias = await self._detect_language_bias(content)
        
        # Detect selection bias (based on source diversity)
        assessment.selection_bias = await self._detect_selection_bias(metadata)
        
        # Calculate overall bias score
        assessment.overall_bias_score = self._calculate_overall_bias(assessment)
        
        # Identify detected bias types
        assessment.detected_bias_types = self._identify_bias_types(assessment)
        
        # Calculate confidence
        assessment.confidence = self._calculate_bias_confidence(assessment, content)
        
        return assessment
    
    async def _detect_political_bias(self, content: str) -> float:
        """Detect political bias (-1 left, 0 neutral, 1 right)"""
        patterns = self.bias_patterns[BiasType.POLITICAL]
        content_lower = content.lower()
        
        left_score = sum(
            len(re.findall(r'\b' + re.escape(indicator) + r'\b', content_lower))
            for indicator in patterns['left_indicators']
        )
        
        right_score = sum(
            len(re.findall(r'\b' + re.escape(indicator) + r'\b', content_lower))
            for indicator in patterns['right_indicators']
        )
        
        neutral_score = sum(
            len(re.findall(r'\b' + re.escape(indicator) + r'\b', content_lower))
            for indicator in patterns['neutral_indicators']
        )
        
        total_political = left_score + right_score + neutral_score
        
        if total_political == 0:
            return 0.0
        
        # Calculate bias score
        if neutral_score > (left_score + right_score):
            return 0.0  # Neutral
        elif left_score > right_score:
            return -min(1.0, (left_score - right_score) / max(1, total_political))
        else:
            return min(1.0, (right_score - left_score) / max(1, total_political))
    
    async def _detect_commercial_bias(self, content: str, metadata: Dict[str, Any]) -> float:
        """Detect commercial bias (0 none, 1 high commercial interest)"""
        patterns = self.bias_patterns[BiasType.COMMERCIAL]
        content_lower = content.lower()
        
        # Count commercial indicators
        indicator_count = sum(
            len(re.findall(r'\b' + re.escape(indicator) + r'\b', content_lower))
            for indicator in patterns['indicators']
        )
        
        phrase_count = sum(
            len(re.findall(r'\b' + re.escape(phrase) + r'\b', content_lower))
            for phrase in patterns['commercial_phrases']
        )
        
        # Check metadata for commercial indicators
        url = metadata.get('url', '').lower()
        title = metadata.get('title', '').lower()
        
        commercial_domains = ['shop', 'store', 'buy', 'sell', 'deal', 'offer']
        domain_score = sum(1 for domain in commercial_domains if domain in url)
        
        title_score = sum(1 for phrase in patterns['indicators'] if phrase in title)
        
        total_commercial = indicator_count + phrase_count + domain_score + title_score
        
        # Normalize score
        word_count = len(content.split())
        if word_count == 0:
            return 0.0
        
        # Calculate commercial bias ratio
        commercial_ratio = total_commercial / max(1, word_count / 100)  # Per 100 words
        
        return min(1.0, commercial_ratio)
    
    async def _detect_confirmation_bias(self, content: str) -> float:
        """Detect confirmation bias (0 none, 1 high confirmation bias)"""
        patterns = self.bias_patterns[BiasType.CONFIRMATION]
        content_lower = content.lower()
        
        confirmation_count = sum(
            len(re.findall(r'\b' + re.escape(indicator) + r'\b', content_lower))
            for indicator in patterns['indicators']
        )
        
        # Count absolute statements
        absolute_patterns = [
            r'\b(?:always|never|all|none|every|no one|everyone)\b',
            r'\b(?:must|should|have to|need to)\b',
            r'\b(?:fact|truth|reality|obvious|clear)\b'
        ]
        
        absolute_count = sum(
            len(re.findall(pattern, content_lower))
            for pattern in absolute_patterns
        )
        
        total_confirmation = confirmation_count + absolute_count
        
        # Normalize by content length
        sentence_count = len(re.split(r'[.!?]+', content))
        if sentence_count == 0:
            return 0.0
        
        confirmation_ratio = total_confirmation / max(1, sentence_count)
        
        return min(1.0, confirmation_ratio)
    
    async def _detect_language_bias(self, content: str) -> float:
        """Detect biased language (0 neutral, 1 highly biased)"""
        patterns = self.bias_patterns[BiasType.LANGUAGE]
        content_lower = content.lower()
        
        emotional_count = sum(
            len(re.findall(r'\b' + re.escape(word) + r'\b', content_lower))
            for word in patterns['emotional_language']
        )
        
        loaded_count = sum(
            len(re.findall(r'\b' + re.escape(term) + r'\b', content_lower))
            for term in patterns['loaded_terms']
        )
        
        # Count excessive punctuation and capitalization
        excessive_punct = len(re.findall(r'[!]{2,}|[?]{2,}|[.]{3,}', content))
        excessive_caps = len(re.findall(r'\b[A-Z]{3,}\b', content))
        
        total_bias_indicators = emotional_count + loaded_count + excessive_punct + excessive_caps
        
        # Normalize by word count
        word_count = len(content.split())
        if word_count == 0:
            return 0.0
        
        bias_ratio = total_bias_indicators / max(1, word_count / 50)  # Per 50 words
        
        return min(1.0, bias_ratio)
    
    async def _detect_selection_bias(self, metadata: Dict[str, Any]) -> float:
        """Detect selection bias based on metadata"""
        # This would typically require more context about the research process
        # For now, return a conservative estimate
        return 0.1
    
    def _calculate_overall_bias(self, assessment: BiasAssessment) -> float:
        """Calculate overall bias score"""
        bias_scores = [
            abs(assessment.political_bias),
            assessment.commercial_bias,
            assessment.confirmation_bias,
            assessment.language_bias,
            assessment.selection_bias
        ]
        
        # Weight different types of bias
        weights = [0.2, 0.3, 0.2, 0.2, 0.1]
        
        weighted_score = sum(score * weight for score, weight in zip(bias_scores, weights))
        
        return min(1.0, weighted_score)
    
    def _identify_bias_types(self, assessment: BiasAssessment) -> List[BiasType]:
        """Identify which types of bias are present"""
        detected_types = []
        
        if abs(assessment.political_bias) > 0.3:
            detected_types.append(BiasType.POLITICAL)
        
        if assessment.commercial_bias > 0.3:
            detected_types.append(BiasType.COMMERCIAL)
        
        if assessment.confirmation_bias > 0.3:
            detected_types.append(BiasType.CONFIRMATION)
        
        if assessment.language_bias > 0.3:
            detected_types.append(BiasType.LANGUAGE)
        
        if assessment.selection_bias > 0.3:
            detected_types.append(BiasType.SELECTION)
        
        return detected_types
    
    def _calculate_bias_confidence(self, assessment: BiasAssessment, content: str) -> float:
        """Calculate confidence in bias assessment"""
        # Base confidence on content length and number of indicators
        word_count = len(content.split())
        
        if word_count < 50:
            base_confidence = 0.3
        elif word_count < 200:
            base_confidence = 0.6
        else:
            base_confidence = 0.8
        
        # Adjust based on number of bias types detected
        bias_types_count = len(assessment.detected_bias_types)
        if bias_types_count == 0:
            return base_confidence * 0.7  # Lower confidence for no bias detected
        else:
            return min(1.0, base_confidence + (bias_types_count * 0.1))

class SourceCredibilityAssessor:
    """Main class for assessing source credibility"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.domain_authority_db = DomainAuthorityDatabase()
        self.author_expertise_db = AuthorExpertiseDatabase()
        self.bias_detector = BiasDetectionEngine()
    
    async def assess_source(self, content: EnhancedScrapedContent) -> SourceCredibilityScore:
        """Assess credibility of a source"""
        if not content.success:
            return SourceCredibilityScore()
        
        # Extract domain from URL
        domain = urlparse(content.url).netloc.lower()
        
        # Assess different credibility factors
        domain_authority = await self.domain_authority_db.get_domain_authority(domain)
        
        author_expertise = await self.author_expertise_db.assess_author_expertise(
            content.metadata.get('author', ''),
            content.clean_text
        )
        
        publication_quality = await self._assess_publication_quality(content)
        peer_review_status = await self._assess_peer_review_status(content, domain)
        citation_count = await self._assess_citation_count(content)
        recency = await self._assess_recency(content)
        
        # Detect bias
        bias_assessment = await self.bias_detector.detect_bias(
            content.clean_text,
            {**content.metadata, 'url': content.url, 'title': content.title}
        )
        
        # Determine source type
        source_type = self._determine_source_type(domain, content.metadata)
        
        return SourceCredibilityScore(
            domain_authority=domain_authority,
            author_expertise=author_expertise,
            publication_quality=publication_quality,
            peer_review_status=peer_review_status,
            citation_count=citation_count,
            recency=recency,
            bias_assessment=bias_assessment,
            source_type=source_type
        )
    
    async def _assess_publication_quality(self, content: EnhancedScrapedContent) -> float:
        """Assess publication quality based on content characteristics"""
        text = content.clean_text
        
        if not text:
            return 0.0
        
        quality_score = 0.0
        
        # Length indicator (longer articles often more thorough)
        word_count = len(text.split())
        if word_count > 2000:
            quality_score += 0.4
        elif word_count > 1000:
            quality_score += 0.3
        elif word_count > 500:
            quality_score += 0.2
        elif word_count > 100:
            quality_score += 0.1
        
        # Structure indicators (academic structure)
        structure_terms = ['abstract', 'introduction', 'methodology', 'method', 'results', 'conclusion', 'references', 'discussion']
        structure_count = sum(1 for term in structure_terms if re.search(r'\b' + term + r'\b', text, re.IGNORECASE))
        quality_score += min(0.4, structure_count * 0.1)
        
        # Citation indicators
        citation_patterns = [
            r'\[\d+\]',  # [1], [2], etc.
            r'\([A-Za-z]+(?:\s+et\s+al\.?)?,?\s*\d{4}\)',  # (Author, 2020)
            r'doi:', r'https?://doi\.org/'
        ]
        
        citation_found = False
        for pattern in citation_patterns:
            if re.search(pattern, text):
                citation_found = True
                break
        
        if citation_found:
            quality_score += 0.2
        
        # Technical depth indicators
        technical_terms = ['algorithm', 'methodology', 'analysis', 'research', 'study', 'experiment', 'data', 'results', 'statistical', 'empirical']
        technical_count = sum(1 for term in technical_terms if term.lower() in text.lower())
        quality_score += min(0.3, technical_count * 0.05)
        
        return min(1.0, quality_score)
    
    async def _assess_peer_review_status(self, content: EnhancedScrapedContent, domain: str) -> float:
        """Assess likelihood of peer review"""
        # Academic domains likely have peer review
        academic_domains = [
            'arxiv.org', 'pubmed.ncbi.nlm.nih.gov', 'nature.com', 'science.org',
            'ieee.org', 'acm.org', 'springer.com', 'elsevier.com'
        ]
        
        if any(domain.endswith(d) for d in academic_domains):
            return 0.9
        
        if domain.endswith('.edu'):
            return 0.7
        
        # Check for peer review indicators in content
        peer_review_indicators = [
            'peer reviewed', 'peer-reviewed', 'reviewed article',
            'journal', 'conference', 'proceedings'
        ]
        
        text_lower = content.clean_text.lower()
        for indicator in peer_review_indicators:
            if indicator in text_lower:
                return 0.8
        
        return 0.1  # Default low probability
    
    async def _assess_citation_count(self, content: EnhancedScrapedContent) -> float:
        """Assess citation count (placeholder - would need external APIs)"""
        # In a real implementation, this would query Google Scholar, CrossRef, etc.
        # For now, return a basic estimate based on content quality
        
        # Check for DOI (articles with DOIs are more likely to be cited)
        if re.search(r'doi:', content.clean_text, re.IGNORECASE):
            return 0.6
        
        # Check for academic indicators
        academic_indicators = ['research', 'study', 'analysis', 'experiment']
        indicator_count = sum(1 for indicator in academic_indicators 
                            if indicator in content.clean_text.lower())
        
        return min(0.8, indicator_count * 0.2)
    
    async def _assess_recency(self, content: EnhancedScrapedContent) -> float:
        """Assess content recency"""
        # Try to extract date from metadata
        pub_date_str = content.metadata.get('published_date', '')
        
        if pub_date_str:
            try:
                # Parse various date formats
                date_formats = [
                    '%Y-%m-%dT%H:%M:%SZ',
                    '%Y-%m-%dT%H:%M:%S',
                    '%Y-%m-%d'
                ]
                
                pub_date = None
                for date_format in date_formats:
                    try:
                        # Extract the portion that matches the format
                        if 'T' in date_format and 'T' in pub_date_str:
                            if pub_date_str.endswith('Z'):
                                date_str = pub_date_str
                            else:
                                date_str = pub_date_str.split('.')[0]  # Remove microseconds
                        else:
                            date_str = pub_date_str[:10]  # Just the date part
                        
                        pub_date = datetime.strptime(date_str, date_format)
                        break
                    except (ValueError, IndexError):
                        continue
                
                if pub_date:
                    days_old = (datetime.now() - pub_date).days
                    
                    if days_old < 30:
                        return 1.0
                    elif days_old < 90:
                        return 0.9
                    elif days_old < 365:
                        return 0.7
                    elif days_old < 1095:  # 3 years
                        return 0.5
                    else:
                        return 0.2
            
            except Exception as e:
                self.logger.warning(f"Error parsing date {pub_date_str}: {e}")
        
        # If no date available, return default
        return 0.5
    
    def _determine_source_type(self, domain: str, metadata: Dict[str, Any]) -> SourceType:
        """Determine the type of source"""
        domain = domain.lower()
        
        # Academic sources
        academic_domains = [
            'arxiv.org', 'pubmed.ncbi.nlm.nih.gov', 'scholar.google.com',
            'nature.com', 'science.org', 'ieee.org', 'acm.org',
            'springer.com', 'elsevier.com', 'researchgate.net'
        ]
        
        if any(domain.endswith(d) for d in academic_domains) or domain.endswith('.edu'):
            return SourceType.ACADEMIC
        
        # Government sources
        if domain.endswith('.gov') or domain in ['who.int', 'un.org', 'europa.eu']:
            return SourceType.GOVERNMENT
        
        # News sources
        news_domains = [
            'reuters.com', 'bbc.com', 'ap.org', 'nytimes.com', 'wsj.com',
            'cnn.com', 'npr.org', 'theguardian.com', 'washingtonpost.com'
        ]
        
        if any(domain.endswith(d) for d in news_domains):
            return SourceType.NEWS
        
        # Tech industry
        tech_domains = [
            'google.com', 'microsoft.com', 'apple.com', 'amazon.com',
            'github.com', 'stackoverflow.com', 'techcrunch.com'
        ]
        
        if any(domain.endswith(d) for d in tech_domains):
            return SourceType.INDUSTRY
        
        # Blog platforms
        blog_domains = ['medium.com', 'dev.to', 'wordpress.com', 'blogger.com']
        
        if any(domain.endswith(d) for d in blog_domains):
            return SourceType.EXPERT_BLOG
        
        # Social media
        social_domains = ['twitter.com', 'facebook.com', 'linkedin.com', 'reddit.com']
        
        if any(domain.endswith(d) for d in social_domains):
            return SourceType.SOCIAL_MEDIA
        
        # Default to industry
        return SourceType.INDUSTRY 