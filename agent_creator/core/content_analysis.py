"""
Comprehensive content analysis framework for research
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple, Set
from collections import Counter, defaultdict
from dataclasses import dataclass
import asyncio
from datetime import datetime
import math

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logging.warning("NumPy not available - using basic math operations")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn not available - using basic text analysis")

from .research_models import (
    EnhancedScrapedContent, ThematicAnalysis, Claim, Contradiction,
    BiasAssessment, BiasType, SourceType
)

class BaseAnalyzer:
    """Base class for content analyzers"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
    
    async def analyze(self, content_items: List[EnhancedScrapedContent]) -> Dict[str, Any]:
        """Analyze content items"""
        raise NotImplementedError

class ThematicAnalyzer(BaseAnalyzer):
    """Analyzer for identifying themes and topics in content"""
    
    def __init__(self):
        super().__init__("ThematicAnalyzer")
        self.stop_words = self._get_stop_words()
        
    def _get_stop_words(self) -> Set[str]:
        """Get basic stop words"""
        return {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
        }
    
    async def analyze(self, content_items: List[EnhancedScrapedContent]) -> Dict[str, Any]:
        """Perform thematic analysis on content"""
        successful_items = [item for item in content_items if item.success and item.clean_text]
        
        if not successful_items:
            return {"error": "No successful content items to analyze"}
        
        # Extract text for analysis
        texts = [item.clean_text for item in successful_items]
        
        # Perform different types of analysis
        topics = await self._identify_topics(texts)
        themes = await self._extract_themes(texts, successful_items)
        clusters = await self._cluster_content(texts)
        entities = await self._extract_entities(texts)
        keywords = await self._extract_keywords(texts)
        
        return {
            "topics": topics,
            "themes": themes,
            "clusters": clusters,
            "entities": entities,
            "keywords": keywords,
            "content_count": len(successful_items)
        }
    
    async def _identify_topics(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Identify main topics using TF-IDF and clustering"""
        if not SKLEARN_AVAILABLE:
            return await self._basic_topic_identification(texts)
        
        try:
            # Use TF-IDF for topic identification
            vectorizer = TfidfVectorizer(
                max_features=100,
                stop_words='english',
                ngram_range=(1, 3),
                min_df=2
            )
            
            tfidf_matrix = vectorizer.fit_transform(texts)
            feature_names = vectorizer.get_feature_names_out()
            
            # Get top terms for the entire corpus
            tfidf_scores = tfidf_matrix.sum(axis=0).A1
            top_indices = tfidf_scores.argsort()[::-1][:20]
            
            topics = []
            for i, idx in enumerate(top_indices):
                topics.append({
                    "id": i,
                    "term": feature_names[idx],
                    "score": float(tfidf_scores[idx]),
                    "documents": int((tfidf_matrix[:, idx] > 0).sum())
                })
            
            return topics
            
        except Exception as e:
            self.logger.error(f"Error in topic identification: {e}")
            return await self._basic_topic_identification(texts)
    
    async def _basic_topic_identification(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Basic topic identification without sklearn"""
        # Combine all texts
        combined_text = ' '.join(texts).lower()
        
        # Extract words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', combined_text)
        
        # Remove stop words
        filtered_words = [word for word in words if word not in self.stop_words]
        
        # Count word frequencies
        word_counts = Counter(filtered_words)
        
        # Get top 20 terms
        topics = []
        for i, (term, count) in enumerate(word_counts.most_common(20)):
            topics.append({
                "id": i,
                "term": term,
                "score": count,
                "documents": sum(1 for text in texts if term in text.lower())
            })
        
        return topics
    
    async def _extract_themes(self, texts: List[str], content_items: List[EnhancedScrapedContent]) -> List[Dict[str, Any]]:
        """Extract higher-level themes from content"""
        themes = []
        
        # Define theme patterns and keywords
        theme_patterns = {
            "technology_adoption": [
                "adoption", "implementation", "deploy", "integrate", "upgrade",
                "transition", "migrate", "transform", "digital transformation"
            ],
            "performance_impact": [
                "performance", "speed", "efficiency", "productivity", "optimization",
                "improvement", "enhancement", "acceleration", "faster", "slower"
            ],
            "challenges_barriers": [
                "challenge", "barrier", "obstacle", "difficulty", "problem",
                "issue", "constraint", "limitation", "risk", "concern"
            ],
            "future_trends": [
                "future", "trend", "prediction", "forecast", "outlook",
                "evolution", "development", "emerging", "upcoming", "next"
            ],
            "economic_impact": [
                "cost", "savings", "revenue", "profit", "economic", "financial",
                "investment", "budget", "expense", "roi", "return on investment"
            ],
            "human_factors": [
                "human", "people", "user", "employee", "worker", "skill",
                "training", "education", "experience", "interface", "usability"
            ]
        }
        
        combined_text = ' '.join(texts).lower()
        
        for theme_name, keywords in theme_patterns.items():
            # Count keyword occurrences
            keyword_counts = {}
            total_score = 0
            
            for keyword in keywords:
                count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', combined_text))
                if count > 0:
                    keyword_counts[keyword] = count
                    total_score += count
            
            if total_score > 0:
                # Find supporting documents
                supporting_docs = []
                for i, item in enumerate(content_items):
                    text_lower = item.clean_text.lower()
                    doc_score = sum(
                        len(re.findall(r'\b' + re.escape(keyword) + r'\b', text_lower))
                        for keyword in keywords
                    )
                    if doc_score > 0:
                        supporting_docs.append({
                            "index": i,
                            "url": item.url,
                            "title": item.title,
                            "relevance_score": doc_score
                        })
                
                themes.append({
                    "name": theme_name,
                    "score": total_score,
                    "keywords": keyword_counts,
                    "supporting_documents": sorted(supporting_docs, key=lambda x: x["relevance_score"], reverse=True)[:5],
                    "prevalence": len(supporting_docs) / len(content_items) if content_items else 0
                })
        
        # Sort themes by score
        themes.sort(key=lambda x: x["score"], reverse=True)
        return themes
    
    async def _cluster_content(self, texts: List[str]) -> List[List[int]]:
        """Cluster similar content items"""
        if len(texts) < 2:
            return [[i] for i in range(len(texts))]
        
        if not SKLEARN_AVAILABLE:
            return await self._basic_clustering(texts)
        
        try:
            # Use TF-IDF and K-means clustering
            vectorizer = TfidfVectorizer(
                max_features=50,
                stop_words='english',
                min_df=1
            )
            
            tfidf_matrix = vectorizer.fit_transform(texts)
            
            # Determine optimal number of clusters (max 5)
            n_clusters = min(len(texts), 5)
            if n_clusters < 2:
                return [[i] for i in range(len(texts))]
            
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(tfidf_matrix)
            
            # Group documents by cluster
            clusters = [[] for _ in range(n_clusters)]
            for doc_idx, cluster_idx in enumerate(cluster_labels):
                clusters[cluster_idx].append(doc_idx)
            
            # Remove empty clusters
            clusters = [cluster for cluster in clusters if cluster]
            
            return clusters
            
        except Exception as e:
            self.logger.error(f"Error in clustering: {e}")
            return await self._basic_clustering(texts)
    
    async def _basic_clustering(self, texts: List[str]) -> List[List[int]]:
        """Basic clustering using simple similarity measures"""
        if len(texts) <= 1:
            return [[i] for i in range(len(texts))]
        
        # Calculate simple similarity based on common words
        similarity_matrix = []
        
        for i, text1 in enumerate(texts):
            similarities = []
            words1 = set(re.findall(r'\b[a-zA-Z]{3,}\b', text1.lower()))
            words1 = words1 - self.stop_words
            
            for j, text2 in enumerate(texts):
                if i == j:
                    similarities.append(1.0)
                else:
                    words2 = set(re.findall(r'\b[a-zA-Z]{3,}\b', text2.lower()))
                    words2 = words2 - self.stop_words
                    
                    if not words1 or not words2:
                        similarities.append(0.0)
                    else:
                        # Jaccard similarity
                        intersection = len(words1 & words2)
                        union = len(words1 | words2)
                        similarity = intersection / union if union > 0 else 0.0
                        similarities.append(similarity)
            
            similarity_matrix.append(similarities)
        
        # Simple clustering based on similarity threshold
        clusters = []
        assigned = set()
        
        for i in range(len(texts)):
            if i in assigned:
                continue
            
            cluster = [i]
            assigned.add(i)
            
            for j in range(i + 1, len(texts)):
                if j not in assigned and similarity_matrix[i][j] > 0.3:
                    cluster.append(j)
                    assigned.add(j)
            
            clusters.append(cluster)
        
        return clusters
    
    async def _extract_entities(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Extract named entities from texts"""
        # Basic entity patterns (could be enhanced with NLP libraries)
        entity_patterns = {
            "organizations": r'\b[A-Z][a-zA-Z]+ (?:Inc|Corp|LLC|Ltd|Company|Corporation|Technologies|Systems|Solutions|Software|AI|Labs)\b',
            "technologies": r'\b(?:AI|ML|Machine Learning|Artificial Intelligence|Python|JavaScript|React|Node\.js|TensorFlow|PyTorch|Docker|Kubernetes|AWS|Azure|GCP|GitHub|GitLab)\b',
            "programming_languages": r'\b(?:Python|JavaScript|Java|C\+\+|C#|Go|Rust|TypeScript|Ruby|PHP|Swift|Kotlin|Scala|R|MATLAB)\b',
            "metrics": r'\b\d+(?:\.\d+)?%?\s*(?:percent|percentage|times|fold|increase|decrease|improvement|reduction)\b',
            "years": r'\b(?:19|20)\d{2}\b',
            "frameworks": r'\b(?:React|Angular|Vue|Django|Flask|Spring|Laravel|Express|Rails|ASP\.NET)\b'
        }
        
        combined_text = ' '.join(texts)
        entities = []
        
        for entity_type, pattern in entity_patterns.items():
            matches = re.finditer(pattern, combined_text, re.IGNORECASE)
            entity_counts = Counter()
            
            for match in matches:
                entity = match.group(0)
                entity_counts[entity] += 1
            
            for entity, count in entity_counts.most_common(10):
                entities.append({
                    "text": entity,
                    "type": entity_type,
                    "frequency": count,
                    "contexts": self._find_entity_contexts(entity, texts)[:3]
                })
        
        return sorted(entities, key=lambda x: x["frequency"], reverse=True)[:50]
    
    def _find_entity_contexts(self, entity: str, texts: List[str]) -> List[str]:
        """Find contexts where entity appears"""
        contexts = []
        pattern = re.compile(re.escape(entity), re.IGNORECASE)
        
        for text in texts:
            matches = pattern.finditer(text)
            for match in matches:
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end].strip()
                if context not in contexts:
                    contexts.append(context)
                if len(contexts) >= 3:
                    break
            if len(contexts) >= 3:
                break
        
        return contexts
    
    async def _extract_keywords(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Extract important keywords from texts"""
        # Combine all texts
        combined_text = ' '.join(texts).lower()
        
        # Extract potential keywords (2-4 word phrases)
        phrases = []
        for n in range(2, 5):  # 2-grams to 4-grams
            words = re.findall(r'\b[a-zA-Z]{3,}\b', combined_text)
            for i in range(len(words) - n + 1):
                phrase_words = words[i:i+n]
                # Skip if contains stop words
                if not any(word in self.stop_words for word in phrase_words):
                    phrase = ' '.join(phrase_words)
                    phrases.append(phrase)
        
        # Count phrase frequencies
        phrase_counts = Counter(phrases)
        
        keywords = []
        for phrase, count in phrase_counts.most_common(30):
            # Calculate importance score
            word_count = len(phrase.split())
            importance = count * word_count  # Favor longer phrases
            
            keywords.append({
                "phrase": phrase,
                "frequency": count,
                "importance": importance,
                "word_count": word_count
            })
        
        return sorted(keywords, key=lambda x: x["importance"], reverse=True)[:20]

class SentimentAnalyzer(BaseAnalyzer):
    """Analyzer for sentiment and emotional tone"""
    
    def __init__(self):
        super().__init__("SentimentAnalyzer")
        self.positive_words = self._load_positive_words()
        self.negative_words = self._load_negative_words()
        self.intensity_words = self._load_intensity_words()
    
    def _load_positive_words(self) -> Set[str]:
        """Load positive sentiment words"""
        return {
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'awesome',
            'positive', 'beneficial', 'effective', 'successful', 'impressive', 'outstanding',
            'superior', 'valuable', 'useful', 'helpful', 'innovative', 'revolutionary',
            'breakthrough', 'advanced', 'cutting-edge', 'state-of-the-art', 'improved',
            'enhanced', 'optimized', 'efficient', 'powerful', 'robust', 'reliable',
            'stable', 'secure', 'fast', 'quick', 'rapid', 'accelerated', 'increased',
            'growth', 'progress', 'success', 'achievement', 'accomplish', 'benefit',
            'advantage', 'opportunity', 'potential', 'promising', 'bright', 'exciting'
        }
    
    def _load_negative_words(self) -> Set[str]:
        """Load negative sentiment words"""
        return {
            'bad', 'terrible', 'awful', 'horrible', 'poor', 'weak', 'inferior',
            'negative', 'harmful', 'dangerous', 'risky', 'problematic', 'concerning',
            'disappointing', 'frustrating', 'difficult', 'challenging', 'complex',
            'complicated', 'confusing', 'unclear', 'uncertain', 'unstable', 'unreliable',
            'insecure', 'vulnerable', 'slow', 'sluggish', 'decreased', 'decline',
            'reduction', 'loss', 'failure', 'problem', 'issue', 'concern', 'worry',
            'threat', 'risk', 'barrier', 'obstacle', 'limitation', 'constraint',
            'drawback', 'disadvantage', 'criticism', 'critique', 'flaw', 'bug',
            'error', 'mistake', 'costly', 'expensive', 'time-consuming'
        }
    
    def _load_intensity_words(self) -> Dict[str, float]:
        """Load intensity modifiers"""
        return {
            'very': 1.5, 'extremely': 2.0, 'incredibly': 2.0, 'highly': 1.5,
            'significantly': 1.5, 'substantially': 1.5, 'considerably': 1.5,
            'remarkably': 1.5, 'exceptionally': 2.0, 'extraordinarily': 2.0,
            'slightly': 0.5, 'somewhat': 0.7, 'moderately': 0.8, 'fairly': 0.8,
            'rather': 0.8, 'quite': 1.2, 'pretty': 1.1, 'really': 1.3,
            'truly': 1.4, 'absolutely': 2.0, 'completely': 2.0, 'totally': 2.0,
            'not': -1.0, 'never': -1.0, 'hardly': -0.5, 'barely': -0.5,
            'scarcely': -0.5, 'rarely': -0.5, 'seldom': -0.5
        }
    
    async def analyze(self, content_items: List[EnhancedScrapedContent]) -> Dict[str, Any]:
        """Analyze sentiment across content items"""
        successful_items = [item for item in content_items if item.success and item.clean_text]
        
        if not successful_items:
            return {"error": "No successful content items to analyze"}
        
        sentiment_scores = []
        detailed_analysis = []
        
        for item in successful_items:
            score = await self._analyze_text_sentiment(item.clean_text)
            sentiment_scores.append(score)
            
            detailed_analysis.append({
                "url": item.url,
                "title": item.title,
                "sentiment_score": score,
                "sentiment_label": self._score_to_label(score),
                "key_phrases": self._extract_sentiment_phrases_sync(item.clean_text)
            })
        
        # Calculate overall statistics
        if sentiment_scores:
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
            sentiment_distribution = self._calculate_sentiment_distribution(sentiment_scores)
        else:
            avg_sentiment = 0.0
            sentiment_distribution = {"positive": 0, "neutral": 0, "negative": 0}
        
        return {
            "average_sentiment": avg_sentiment,
            "sentiment_label": self._score_to_label(avg_sentiment),
            "distribution": sentiment_distribution,
            "detailed_analysis": detailed_analysis,
            "content_count": len(successful_items)
        }
    
    async def _analyze_text_sentiment(self, text: str) -> float:
        """Analyze sentiment of a single text"""
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        total_score = 0.0
        word_count = 0
        
        i = 0
        while i < len(words):
            word = words[i]
            intensity = 1.0
            
            # Check for intensity modifiers in the previous 2 words
            for j in range(max(0, i-2), i):
                if words[j] in self.intensity_words:
                    intensity *= self.intensity_words[words[j]]
            
            # Calculate word sentiment
            if word in self.positive_words:
                total_score += 1.0 * intensity
                word_count += 1
            elif word in self.negative_words:
                total_score -= 1.0 * abs(intensity)  # Ensure negative impact
                word_count += 1
            
            i += 1
        
        # Normalize score
        if word_count > 0:
            return total_score / word_count
        else:
            return 0.0
    
    def _score_to_label(self, score: float) -> str:
        """Convert sentiment score to label"""
        if score > 0.1:
            return "positive"
        elif score < -0.1:
            return "negative"
        else:
            return "neutral"
    
    def _calculate_sentiment_distribution(self, scores: List[float]) -> Dict[str, int]:
        """Calculate distribution of sentiment labels"""
        distribution = {"positive": 0, "neutral": 0, "negative": 0}
        
        for score in scores:
            label = self._score_to_label(score)
            distribution[label] += 1
        
        return distribution
    
    def _extract_sentiment_phrases_sync(self, text: str) -> List[Dict[str, Any]]:
        """Extract phrases that contribute to sentiment (synchronous version)"""
        sentences = re.split(r'[.!?]+', text)
        sentiment_phrases = []
        
        for sentence in sentences[:5]:  # Analyze first 5 sentences
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
            
            # Use synchronous version of sentiment analysis
            words = re.findall(r'\b[a-zA-Z]+\b', sentence.lower())
            total_score = 0.0
            word_count = 0
            
            for i, word in enumerate(words):
                intensity = 1.0
                # Check for intensity modifiers in the previous 2 words
                for j in range(max(0, i-2), i):
                    if j < len(words) and words[j] in self.intensity_words:
                        intensity *= self.intensity_words[words[j]]
                
                if word in self.positive_words:
                    total_score += 1.0 * intensity
                    word_count += 1
                elif word in self.negative_words:
                    total_score -= 1.0 * abs(intensity)
                    word_count += 1
            
            score = total_score / word_count if word_count > 0 else 0.0
            
            if abs(score) > 0.2:  # Only significant sentiment
                sentiment_phrases.append({
                    "phrase": sentence[:100] + "..." if len(sentence) > 100 else sentence,
                    "sentiment_score": score,
                    "sentiment_label": self._score_to_label(score)
                })
        
        return sorted(sentiment_phrases, key=lambda x: abs(x["sentiment_score"]), reverse=True)[:3]

class FactExtractor(BaseAnalyzer):
    """Analyzer for extracting factual claims"""
    
    def __init__(self):
        super().__init__("FactExtractor")
        self.claim_patterns = self._load_claim_patterns()
    
    def _load_claim_patterns(self) -> List[Dict[str, Any]]:
        """Load patterns for identifying different types of claims"""
        return [
            {
                "type": "statistic",
                "pattern": r'\b\d+(?:\.\d+)?%?\s*(?:percent|percentage|times|fold|increase|decrease|improvement|reduction|faster|slower|more|less)\b',
                "confidence": 0.8
            },
            {
                "type": "comparative", 
                "pattern": r'\b(?:better|worse|faster|slower|more|less|higher|lower|superior|inferior)\s+than\b',
                "confidence": 0.7
            },
            {
                "type": "temporal",
                "pattern": r'\b(?:by|in|since|until|before|after)\s+(?:19|20)\d{2}\b',
                "confidence": 0.6
            },
            {
                "type": "causal",
                "pattern": r'\b(?:because|due to|caused by|results in|leads to|enables|prevents)\b',
                "confidence": 0.7
            },
            {
                "type": "predictive",
                "pattern": r'\b(?:will|would|could|might|expected to|projected to|forecasted to|predicted to)\b',
                "confidence": 0.6
            },
            {
                "type": "capability",
                "pattern": r'\b(?:can|able to|capable of|enables|allows|supports|provides)\b',
                "confidence": 0.5
            }
        ]
    
    async def analyze(self, content_items: List[EnhancedScrapedContent]) -> Dict[str, Any]:
        """Extract factual claims from content"""
        successful_items = [item for item in content_items if item.success and item.clean_text]
        
        if not successful_items:
            return {"error": "No successful content items to analyze"}
        
        all_claims = []
        claims_by_source = {}
        
        for item in successful_items:
            claims = await self._extract_claims_from_text(item.clean_text, item.url)
            all_claims.extend(claims)
            claims_by_source[item.url] = claims
        
        # Analyze claim types
        claim_type_distribution = Counter(claim.claim_type for claim in all_claims)
        
        # Find high-confidence claims
        high_confidence_claims = [claim for claim in all_claims if claim.confidence > 0.7]
        
        return {
            "total_claims": len(all_claims),
            "claims_by_type": dict(claim_type_distribution),
            "high_confidence_claims": [self._claim_to_dict(claim) for claim in high_confidence_claims[:20]],
            "claims_by_source": {url: len(claims) for url, claims in claims_by_source.items()},
            "average_confidence": sum(claim.confidence for claim in all_claims) / len(all_claims) if all_claims else 0.0
        }
    
    async def _extract_claims_from_text(self, text: str, source_url: str) -> List[Claim]:
        """Extract claims from a single text"""
        claims = []
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:  # Skip very short sentences
                continue
            
            for pattern_info in self.claim_patterns:
                if re.search(pattern_info["pattern"], sentence, re.IGNORECASE):
                    claim = Claim(
                        text=sentence,
                        source_url=source_url,
                        confidence=pattern_info["confidence"],
                        claim_type=pattern_info["type"],
                        entities=self._extract_entities_from_sentence(sentence)
                    )
                    claims.append(claim)
                    break  # Only assign one type per sentence
        
        return claims
    
    def _extract_entities_from_sentence(self, sentence: str) -> List[str]:
        """Extract entities from a sentence"""
        # Simple entity extraction
        entities = []
        
        # Numbers and percentages
        numbers = re.findall(r'\b\d+(?:\.\d+)?%?\b', sentence)
        entities.extend(numbers)
        
        # Capitalized words (potential proper nouns)
        proper_nouns = re.findall(r'\b[A-Z][a-zA-Z]+\b', sentence)
        entities.extend(proper_nouns[:5])  # Limit to avoid noise
        
        # Years
        years = re.findall(r'\b(?:19|20)\d{2}\b', sentence)
        entities.extend(years)
        
        return list(set(entities))  # Remove duplicates
    
    def _claim_to_dict(self, claim: Claim) -> Dict[str, Any]:
        """Convert claim to dictionary for serialization"""
        return {
            "text": claim.text,
            "claim_type": claim.claim_type,
            "confidence": claim.confidence,
            "source_url": claim.source_url,
            "entities": claim.entities
        }

class ContentAnalysisFramework:
    """Main framework that coordinates all analyzers"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.analyzers = {
            'thematic': ThematicAnalyzer(),
            'sentiment': SentimentAnalyzer(),
            'fact_extraction': FactExtractor()
        }
    
    async def comprehensive_analysis(self, content_items: List[EnhancedScrapedContent]) -> Dict[str, Any]:
        """Run comprehensive analysis using all analyzers"""
        if not content_items:
            return {"error": "No content items provided"}
        
        successful_items = [item for item in content_items if item.success and item.clean_text]
        if not successful_items:
            return {"error": "No successful content items to analyze"}
        
        self.logger.info(f"Starting comprehensive analysis on {len(successful_items)} content items")
        
        # Run all analyzers in parallel
        analysis_tasks = []
        for name, analyzer in self.analyzers.items():
            task = asyncio.create_task(analyzer.analyze(successful_items))
            analysis_tasks.append((name, task))
        
        # Collect results
        analyses = {}
        for name, task in analysis_tasks:
            try:
                result = await task
                analyses[name] = result
                self.logger.info(f"Completed {name} analysis")
            except Exception as e:
                self.logger.error(f"Error in {name} analysis: {e}")
                analyses[name] = {"error": str(e)}
        
        # Generate synthesis
        synthesis = await self._synthesize_analyses(analyses, successful_items)
        
        return {
            "individual_analyses": analyses,
            "synthesis": synthesis,
            "metadata": {
                "total_content_items": len(content_items),
                "successful_items": len(successful_items),
                "analysis_timestamp": datetime.now().isoformat(),
                "analyzers_used": list(self.analyzers.keys())
            }
        }
    
    async def _synthesize_analyses(self, analyses: Dict[str, Any], content_items: List[EnhancedScrapedContent]) -> Dict[str, Any]:
        """Synthesize results from multiple analyzers"""
        synthesis = {
            "key_insights": [],
            "content_quality_assessment": {},
            "research_themes": [],
            "confidence_assessment": {}
        }
        
        # Extract key insights from thematic analysis
        if 'thematic' in analyses and 'themes' in analyses['thematic']:
            top_themes = analyses['thematic']['themes'][:3]
            for theme in top_themes:
                synthesis["key_insights"].append({
                    "type": "theme",
                    "insight": f"Strong focus on {theme['name'].replace('_', ' ')} (score: {theme['score']})",
                    "supporting_evidence": len(theme.get('supporting_documents', []))
                })
        
        # Extract sentiment insights
        if 'sentiment' in analyses and 'average_sentiment' in analyses['sentiment']:
            sentiment_data = analyses['sentiment']
            synthesis["key_insights"].append({
                "type": "sentiment",
                "insight": f"Overall sentiment is {sentiment_data['sentiment_label']} (score: {sentiment_data['average_sentiment']:.2f})",
                "distribution": sentiment_data.get('distribution', {})
            })
        
        # Extract factual insights
        if 'fact_extraction' in analyses and 'total_claims' in analyses['fact_extraction']:
            fact_data = analyses['fact_extraction']
            synthesis["key_insights"].append({
                "type": "claims",
                "insight": f"Extracted {fact_data['total_claims']} factual claims with {fact_data['average_confidence']:.2f} average confidence",
                "claim_types": fact_data.get('claims_by_type', {})
            })
        
        # Assess content quality
        synthesis["content_quality_assessment"] = {
            "source_diversity": len(set(item.source_type for item in content_items)),
            "average_length": sum(len(item.clean_text) for item in content_items) / len(content_items) if content_items else 0,
            "success_rate": len([item for item in content_items if item.success]) / len(content_items) if content_items else 0
        }
        
        return synthesis 