"""
Tests for the content analysis framework
"""

import pytest
import asyncio
import re
from unittest.mock import patch, MagicMock

from agent_creator.core.content_analysis import (
    ThematicAnalyzer, SentimentAnalyzer, FactExtractor,
    ContentAnalysisFramework
)
from agent_creator.core.research_models import (
    EnhancedScrapedContent, SourceType, Claim
)

class TestThematicAnalyzer:
    """Test the thematic analyzer"""
    
    def test_initialization(self):
        """Test ThematicAnalyzer initialization"""
        analyzer = ThematicAnalyzer()
        assert analyzer.name == "ThematicAnalyzer"
        assert len(analyzer.stop_words) > 0
        assert 'the' in analyzer.stop_words
        assert 'and' in analyzer.stop_words
    
    @pytest.mark.asyncio
    async def test_analyze_empty_content(self):
        """Test analysis with empty content"""
        analyzer = ThematicAnalyzer()
        result = await analyzer.analyze([])
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_analyze_failed_content(self):
        """Test analysis with failed content items"""
        analyzer = ThematicAnalyzer()
        
        content_items = [
            EnhancedScrapedContent(
                url="https://example.com",
                success=False,
                error="Failed to scrape"
            )
        ]
        
        result = await analyzer.analyze(content_items)
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_basic_topic_identification(self):
        """Test basic topic identification without sklearn"""
        analyzer = ThematicAnalyzer()
        
        texts = [
            "Artificial intelligence and machine learning are transforming software development",
            "AI algorithms help developers write better code faster",
            "Machine learning models can detect bugs and improve software quality"
        ]
        
        topics = await analyzer._basic_topic_identification(texts)
        
        assert len(topics) > 0
        assert all('term' in topic for topic in topics)
        assert all('score' in topic for topic in topics)
        assert all('documents' in topic for topic in topics)
        
        # Check that AI-related terms appear
        topic_terms = [topic['term'] for topic in topics]
        assert any('machine' in term for term in topic_terms)
        assert any('learning' in term for term in topic_terms)
    
    @pytest.mark.asyncio
    async def test_extract_themes(self):
        """Test theme extraction"""
        analyzer = ThematicAnalyzer()
        
        content_items = [
            EnhancedScrapedContent(
                url="https://example1.com",
                title="AI Performance Study",
                clean_text="AI implementation shows significant performance improvement and efficiency gains",
                success=True
            ),
            EnhancedScrapedContent(
                url="https://example2.com", 
                title="Future of Technology",
                clean_text="Future trends indicate emerging technologies will transform the industry",
                success=True
            )
        ]
        
        texts = [item.clean_text for item in content_items]
        themes = await analyzer._extract_themes(texts, content_items)
        
        assert isinstance(themes, list)
        
        # Should find performance and future trends themes
        theme_names = [theme['name'] for theme in themes]
        assert 'performance_impact' in theme_names or 'future_trends' in theme_names
        
        for theme in themes:
            assert 'name' in theme
            assert 'score' in theme
            assert 'keywords' in theme
            assert 'supporting_documents' in theme
    
    @pytest.mark.asyncio
    async def test_basic_clustering(self):
        """Test basic content clustering"""
        analyzer = ThematicAnalyzer()
        
        texts = [
            "Machine learning algorithms improve software development",
            "AI helps developers write better code",
            "Cloud computing enables scalable applications",
            "Distributed systems handle large workloads"
        ]
        
        clusters = await analyzer._basic_clustering(texts)
        
        assert isinstance(clusters, list)
        assert len(clusters) <= len(texts)
        
        # All documents should be assigned to a cluster
        all_docs = set()
        for cluster in clusters:
            all_docs.update(cluster)
        assert len(all_docs) == len(texts)
    
    @pytest.mark.asyncio
    async def test_extract_entities(self):
        """Test entity extraction"""
        analyzer = ThematicAnalyzer()
        
        texts = [
            "Google Inc and Microsoft Corporation are using Python and JavaScript",
            "In 2024, AI technologies like TensorFlow and PyTorch show 50% improvement",
            "React and Node.js frameworks enable modern web development"
        ]
        
        entities = await analyzer._extract_entities(texts)
        
        assert isinstance(entities, list)
        assert len(entities) > 0
        
        for entity in entities:
            assert 'text' in entity
            assert 'type' in entity
            assert 'frequency' in entity
            assert 'contexts' in entity
        
        # Check for expected entity types
        entity_types = set(entity['type'] for entity in entities)
        assert len(entity_types) > 0
    
    def test_find_entity_contexts(self):
        """Test entity context finding"""
        analyzer = ThematicAnalyzer()
        
        texts = [
            "Python is a popular programming language used in AI development",
            "Many companies use Python for machine learning projects"
        ]
        
        contexts = analyzer._find_entity_contexts("Python", texts)
        
        assert isinstance(contexts, list)
        assert len(contexts) <= 3
        assert all("Python" in context for context in contexts)
    
    @pytest.mark.asyncio
    async def test_extract_keywords(self):
        """Test keyword extraction"""
        analyzer = ThematicAnalyzer()
        
        texts = [
            "Machine learning algorithms improve software development efficiency",
            "Artificial intelligence enhances code quality and developer productivity",
            "Software engineering practices benefit from AI-powered tools"
        ]
        
        keywords = await analyzer._extract_keywords(texts)
        
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        
        for keyword in keywords:
            assert 'phrase' in keyword
            assert 'frequency' in keyword
            assert 'importance' in keyword
            assert 'word_count' in keyword
        
        # Keywords should be sorted by importance
        if len(keywords) > 1:
            assert keywords[0]['importance'] >= keywords[1]['importance']

class TestSentimentAnalyzer:
    """Test the sentiment analyzer"""
    
    def test_initialization(self):
        """Test SentimentAnalyzer initialization"""
        analyzer = SentimentAnalyzer()
        assert analyzer.name == "SentimentAnalyzer"
        assert len(analyzer.positive_words) > 0
        assert len(analyzer.negative_words) > 0
        assert len(analyzer.intensity_words) > 0
        
        # Check some expected words
        assert 'good' in analyzer.positive_words
        assert 'bad' in analyzer.negative_words
        assert 'very' in analyzer.intensity_words
    
    @pytest.mark.asyncio
    async def test_analyze_text_sentiment_positive(self):
        """Test positive sentiment analysis"""
        analyzer = SentimentAnalyzer()
        
        positive_text = "This is an excellent and amazing breakthrough in technology"
        score = await analyzer._analyze_text_sentiment(positive_text)
        
        assert score > 0, "Should detect positive sentiment"
    
    @pytest.mark.asyncio
    async def test_analyze_text_sentiment_negative(self):
        """Test negative sentiment analysis"""
        analyzer = SentimentAnalyzer()
        
        negative_text = "This is a terrible and problematic approach with many issues"
        score = await analyzer._analyze_text_sentiment(negative_text)
        
        assert score < 0, "Should detect negative sentiment"
    
    @pytest.mark.asyncio
    async def test_analyze_text_sentiment_neutral(self):
        """Test neutral sentiment analysis"""
        analyzer = SentimentAnalyzer()
        
        neutral_text = "This system processes data using standard algorithms and methods"
        score = await analyzer._analyze_text_sentiment(neutral_text)
        
        assert abs(score) < 0.2, "Should detect neutral sentiment"
    
    def test_score_to_label(self):
        """Test sentiment score to label conversion"""
        analyzer = SentimentAnalyzer()
        
        assert analyzer._score_to_label(0.5) == "positive"
        assert analyzer._score_to_label(-0.5) == "negative"
        assert analyzer._score_to_label(0.05) == "neutral"
        assert analyzer._score_to_label(-0.05) == "neutral"
    
    def test_calculate_sentiment_distribution(self):
        """Test sentiment distribution calculation"""
        analyzer = SentimentAnalyzer()
        
        scores = [0.5, -0.3, 0.1, -0.7, 0.0]
        distribution = analyzer._calculate_sentiment_distribution(scores)
        
        assert 'positive' in distribution
        assert 'negative' in distribution
        assert 'neutral' in distribution
        assert sum(distribution.values()) == len(scores)
    
    @pytest.mark.asyncio
    async def test_analyze_content_items(self):
        """Test sentiment analysis on content items"""
        analyzer = SentimentAnalyzer()
        
        content_items = [
            EnhancedScrapedContent(
                url="https://positive.com",
                title="Great News",
                clean_text="This excellent technology shows amazing results and impressive performance",
                success=True
            ),
            EnhancedScrapedContent(
                url="https://negative.com",
                title="Bad News", 
                clean_text="This terrible approach has serious problems and disappointing results",
                success=True
            )
        ]
        
        result = await analyzer.analyze(content_items)
        
        assert 'average_sentiment' in result
        assert 'sentiment_label' in result
        assert 'distribution' in result
        assert 'detailed_analysis' in result
        assert 'content_count' in result
        
        assert result['content_count'] == 2
        assert len(result['detailed_analysis']) == 2

class TestFactExtractor:
    """Test the fact extractor"""
    
    def test_initialization(self):
        """Test FactExtractor initialization"""
        extractor = FactExtractor()
        assert extractor.name == "FactExtractor"
        assert len(extractor.claim_patterns) > 0
        
        # Check pattern types
        pattern_types = [pattern['type'] for pattern in extractor.claim_patterns]
        assert 'statistic' in pattern_types
        assert 'comparative' in pattern_types
        assert 'temporal' in pattern_types
    
    @pytest.mark.asyncio
    async def test_extract_claims_from_text(self):
        """Test claim extraction from text"""
        extractor = FactExtractor()
        
        text = """
        AI improves productivity by 50% according to recent studies.
        This technology is better than traditional approaches.
        By 2025, most companies will adopt AI solutions.
        Machine learning can identify patterns in data.
        """
        
        claims = await extractor._extract_claims_from_text(text, "https://example.com")
        
        assert len(claims) > 0
        assert all(isinstance(claim, Claim) for claim in claims)
        
        # Check claim types
        claim_types = set(claim.claim_type for claim in claims)
        assert len(claim_types) > 0
        
        # Should find different types of claims
        expected_types = {'statistic', 'comparative', 'temporal', 'capability'}
        assert len(claim_types.intersection(expected_types)) > 0
    
    def test_extract_entities_from_sentence(self):
        """Test entity extraction from sentences"""
        extractor = FactExtractor()
        
        sentence = "Python increased development speed by 25% in 2023 at Google"
        entities = extractor._extract_entities_from_sentence(sentence)
        
        assert isinstance(entities, list)
        assert len(entities) > 0
        
        # Should extract some entities (the exact format may vary)
        assert len(entities) > 0
        # Check that we extract some expected types of entities
        entity_strings = [str(entity) for entity in entities]
        has_number = any(re.search(r'\d', entity_str) for entity_str in entity_strings)
        has_proper_noun = any(entity_str[0].isupper() for entity_str in entity_strings if entity_str)
        assert has_number or has_proper_noun
    
    @pytest.mark.asyncio
    async def test_analyze_content_items(self):
        """Test fact extraction on content items"""
        extractor = FactExtractor()
        
        content_items = [
            EnhancedScrapedContent(
                url="https://stats.com",
                title="Performance Study",
                clean_text="AI reduces development time by 40%. It is better than manual coding. By 2024, adoption will increase.",
                success=True
            ),
            EnhancedScrapedContent(
                url="https://research.com",
                title="Tech Analysis",
                clean_text="Machine learning can process large datasets. This enables faster decision making.",
                success=True
            )
        ]
        
        result = await extractor.analyze(content_items)
        
        assert 'total_claims' in result
        assert 'claims_by_type' in result
        assert 'high_confidence_claims' in result
        assert 'claims_by_source' in result
        assert 'average_confidence' in result
        
        assert result['total_claims'] > 0
        assert len(result['claims_by_source']) == 2

class TestContentAnalysisFramework:
    """Test the main content analysis framework"""
    
    def test_initialization(self):
        """Test framework initialization"""
        framework = ContentAnalysisFramework()
        assert len(framework.analyzers) == 3
        assert 'thematic' in framework.analyzers
        assert 'sentiment' in framework.analyzers
        assert 'fact_extraction' in framework.analyzers
    
    @pytest.mark.asyncio
    async def test_comprehensive_analysis_empty(self):
        """Test comprehensive analysis with empty content"""
        framework = ContentAnalysisFramework()
        result = await framework.comprehensive_analysis([])
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_comprehensive_analysis_success(self):
        """Test successful comprehensive analysis"""
        framework = ContentAnalysisFramework()
        
        content_items = [
            EnhancedScrapedContent(
                url="https://example1.com",
                title="AI Technology Review",
                clean_text="Artificial intelligence shows excellent performance improvements. AI reduces development time by 30%. This technology is better than traditional methods.",
                success=True,
                source_type=SourceType.ACADEMIC
            ),
            EnhancedScrapedContent(
                url="https://example2.com",
                title="Future Trends",
                clean_text="By 2025, machine learning will transform software development. These emerging technologies show promising results.",
                success=True,
                source_type=SourceType.INDUSTRY
            )
        ]
        
        result = await framework.comprehensive_analysis(content_items)
        
        assert 'individual_analyses' in result
        assert 'synthesis' in result
        assert 'metadata' in result
        
        # Check individual analyses
        analyses = result['individual_analyses']
        assert 'thematic' in analyses
        assert 'sentiment' in analyses
        assert 'fact_extraction' in analyses
        
        # Check synthesis
        synthesis = result['synthesis']
        assert 'key_insights' in synthesis
        assert 'content_quality_assessment' in synthesis
        assert 'research_themes' in synthesis
        assert 'confidence_assessment' in synthesis
        
        # Check metadata
        metadata = result['metadata']
        assert metadata['total_content_items'] == 2
        assert metadata['successful_items'] == 2
        assert 'analysis_timestamp' in metadata
        assert 'analyzers_used' in metadata
    
    @pytest.mark.asyncio
    async def test_analyzer_error_handling(self):
        """Test error handling when analyzer fails"""
        framework = ContentAnalysisFramework()
        
        # Mock one analyzer to fail
        with patch.object(framework.analyzers['thematic'], 'analyze', side_effect=Exception("Test error")):
            content_items = [
                EnhancedScrapedContent(
                    url="https://example.com",
                    title="Test",
                    clean_text="Test content",
                    success=True
                )
            ]
            
            result = await framework.comprehensive_analysis(content_items)
            
            assert 'individual_analyses' in result
            assert 'error' in result['individual_analyses']['thematic']
            assert result['individual_analyses']['thematic']['error'] == "Test error"
    
    @pytest.mark.asyncio
    async def test_synthesize_analyses(self):
        """Test analysis synthesis"""
        framework = ContentAnalysisFramework()
        
        content_items = [
            EnhancedScrapedContent(
                url="https://example.com",
                clean_text="Test content",
                success=True,
                source_type=SourceType.ACADEMIC
            )
        ]
        
        # Mock analysis results
        analyses = {
            'thematic': {
                'themes': [
                    {'name': 'technology_adoption', 'score': 10, 'supporting_documents': [1, 2, 3]}
                ]
            },
            'sentiment': {
                'average_sentiment': 0.5,
                'sentiment_label': 'positive',
                'distribution': {'positive': 1, 'neutral': 0, 'negative': 0}
            },
            'fact_extraction': {
                'total_claims': 5,
                'average_confidence': 0.8,
                'claims_by_type': {'statistic': 2, 'comparative': 3}
            }
        }
        
        synthesis = await framework._synthesize_analyses(analyses, content_items)
        
        assert 'key_insights' in synthesis
        assert 'content_quality_assessment' in synthesis
        
        # Should have insights from all analyzers
        insights = synthesis['key_insights']
        insight_types = [insight['type'] for insight in insights]
        assert 'theme' in insight_types
        assert 'sentiment' in insight_types
        assert 'claims' in insight_types

class TestIntegration:
    """Integration tests for content analysis"""
    
    @pytest.mark.asyncio
    async def test_full_analysis_pipeline(self):
        """Test the complete analysis pipeline"""
        # Create realistic test content
        content_items = [
            EnhancedScrapedContent(
                url="https://techreview.com/ai-study",
                title="AI Performance Analysis",
                clean_text="""
                Recent studies show that artificial intelligence dramatically improves software development productivity.
                AI-powered tools reduce coding time by 45% compared to traditional methods.
                By 2025, experts predict that 80% of developers will use AI assistants.
                The technology shows excellent results in code generation and bug detection.
                However, some developers worry about the reliability of AI-generated code.
                Machine learning algorithms can identify patterns that humans miss.
                """,
                success=True,
                source_type=SourceType.ACADEMIC
            ),
            EnhancedScrapedContent(
                url="https://devnews.io/future-coding",
                title="The Future of Coding",
                clean_text="""
                The software development landscape is rapidly evolving with AI integration.
                New frameworks like GitHub Copilot enable faster development cycles.
                Performance improvements are significant across different programming languages.
                Python and JavaScript developers report the highest satisfaction rates.
                Cloud computing platforms are adopting AI-first approaches.
                This transformation represents a fundamental shift in how we build software.
                """,
                success=True,
                source_type=SourceType.INDUSTRY
            )
        ]
        
        # Run full analysis
        framework = ContentAnalysisFramework()
        result = await framework.comprehensive_analysis(content_items)
        
        # Validate complete result structure
        assert 'individual_analyses' in result
        assert 'synthesis' in result
        assert 'metadata' in result
        
        # Validate each analysis component
        analyses = result['individual_analyses']
        
        # Thematic analysis should find AI/technology themes
        if 'thematic' in analyses and 'themes' in analyses['thematic']:
            themes = analyses['thematic']['themes']
            theme_names = [theme['name'] for theme in themes]
            assert any('technology' in name or 'performance' in name for name in theme_names)
        
        # Sentiment should be generally positive
        if 'sentiment' in analyses and 'average_sentiment' in analyses['sentiment']:
            sentiment = analyses['sentiment']
            assert sentiment['average_sentiment'] >= -0.5  # Not strongly negative
        
        # Should extract multiple claims
        if 'fact_extraction' in analyses and 'total_claims' in analyses['fact_extraction']:
            claims = analyses['fact_extraction']
            assert claims['total_claims'] > 0
        
        # Synthesis should provide insights
        synthesis = result['synthesis']
        assert len(synthesis['key_insights']) > 0

if __name__ == "__main__":
    pytest.main([__file__]) 