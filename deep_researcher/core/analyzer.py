"""Content analyzer for the Deep Research System."""

import logging
from typing import List

from ..models.data_models import ScrapedContent


class ContentAnalyzer:
    """Analyzes content for relevance to research query"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_relevance(self, content: str, query: str) -> float:
        """Calculate how relevant content is to the research query"""
        if not content or not query:
            return 0.0
        
        content_lower = content.lower()
        query_words = [word.lower().strip() for word in query.split() if len(word) > 2]
        
        if not query_words:
            return 0.0
        
        # Count exact word matches
        exact_matches = sum(1 for word in query_words if word in content_lower)
        
        # Count partial matches (word stems)
        partial_matches = 0
        for word in query_words:
            if len(word) > 4:
                stem = word[:4]
                if stem in content_lower:
                    partial_matches += 0.5
        
        # Calculate phrase matches
        phrase_matches = 0
        for i in range(len(query_words) - 1):
            phrase = f"{query_words[i]} {query_words[i+1]}"
            if phrase in content_lower:
                phrase_matches += 2
        
        total_score = exact_matches + partial_matches + phrase_matches
        max_possible_score = len(query_words) * 2  # Arbitrary scaling
        
        relevance = min(1.0, total_score / max_possible_score) if max_possible_score > 0 else 0.0
        
        return relevance
    
    def filter_relevant_content(self, content_list: List[ScrapedContent], 
                              query: str, min_relevance: float = 0.1) -> List[ScrapedContent]:
        """Filter content list to only include relevant items"""
        relevant_content = []
        
        for content in content_list:
            if content.success and content.content:
                relevance = self.calculate_relevance(content.content, query)
                content.relevance_score = relevance
                
                if relevance >= min_relevance:
                    relevant_content.append(content)
                    self.logger.info(f"Relevant content found: {content.url} (score: {relevance:.2f})")
        
        # Sort by relevance score
        relevant_content.sort(key=lambda x: x.relevance_score, reverse=True)
        return relevant_content