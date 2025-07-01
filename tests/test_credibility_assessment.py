"""
Tests for the credibility assessment and bias detection system
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from agent_creator.core.credibility_assessment import (
    DomainAuthorityDatabase, AuthorExpertiseDatabase, BiasDetectionEngine,
    SourceCredibilityAssessor
)
from agent_creator.core.research_models import (
    EnhancedScrapedContent, SourceType, BiasType, BiasAssessment,
    SourceCredibilityScore
)

class TestDomainAuthorityDatabase:
    """Test the domain authority database"""
    
    def test_initialization(self):
        """Test database initialization"""
        db = DomainAuthorityDatabase()
        assert len(db.authority_scores) > 0
        assert 'arxiv.org' in db.authority_scores
        assert 'google.com' in db.authority_scores
    
    @pytest.mark.asyncio
    async def test_get_domain_authority_exact_match(self):
        """Test exact domain match"""
        db = DomainAuthorityDatabase()
        
        score = await db.get_domain_authority('arxiv.org')
        assert score == 0.95
        
        score = await db.get_domain_authority('google.com')
        assert score == 0.8
    
    @pytest.mark.asyncio
    async def test_get_domain_authority_subdomain(self):
        """Test subdomain matching"""
        db = DomainAuthorityDatabase()
        
        score = await db.get_domain_authority('www.google.com')
        assert score == 0.8
        
        score = await db.get_domain_authority('scholar.google.com')
        assert score == 0.95  # Exact match takes precedence
    
    @pytest.mark.asyncio
    async def test_get_domain_authority_tld(self):
        """Test TLD pattern matching"""
        db = DomainAuthorityDatabase()
        
        score = await db.get_domain_authority('example.gov')
        assert score == 0.9
        
        score = await db.get_domain_authority('university.edu')
        assert score == 0.85
    
    @pytest.mark.asyncio
    async def test_get_domain_authority_unknown(self):
        """Test unknown domain"""
        db = DomainAuthorityDatabase()
        
        score = await db.get_domain_authority('unknown-domain.xyz')
        assert score == 0.3  # Default score

class TestAuthorExpertiseDatabase:
    """Test the author expertise database"""
    
    def test_initialization(self):
        """Test database initialization"""
        db = AuthorExpertiseDatabase()
        assert 'academic_titles' in db.expertise_indicators
        assert 'professional_titles' in db.expertise_indicators
        assert 'institutional_affiliation' in db.expertise_indicators
    
    @pytest.mark.asyncio
    async def test_assess_author_expertise_empty(self):
        """Test assessment with empty author"""
        db = AuthorExpertiseDatabase()
        
        score = await db.assess_author_expertise("", "")
        assert score == 0.0
    
    @pytest.mark.asyncio
    async def test_assess_author_expertise_academic(self):
        """Test assessment with academic credentials"""
        db = AuthorExpertiseDatabase()
        
        author = "Dr. Jane Smith, PhD"
        content = "Research conducted at Stanford University"
        
        score = await db.assess_author_expertise(author, content)
        assert score > 0.5  # Should detect academic credentials
    
    @pytest.mark.asyncio
    async def test_assess_author_expertise_professional(self):
        """Test assessment with professional titles"""
        db = AuthorExpertiseDatabase()
        
        author = "John Doe, Senior Engineer at Google"
        content = "Technical analysis from industry perspective"
        
        score = await db.assess_author_expertise(author, content)
        assert score > 0.4  # Should detect professional credentials
    
    @pytest.mark.asyncio
    async def test_assess_author_expertise_unknown(self):
        """Test assessment with unknown author"""
        db = AuthorExpertiseDatabase()
        
        author = "Anonymous User"
        content = "Some random content"
        
        score = await db.assess_author_expertise(author, content)
        assert score == 0.2  # Default score

class TestBiasDetectionEngine:
    """Test the bias detection engine"""
    
    def test_initialization(self):
        """Test engine initialization"""
        engine = BiasDetectionEngine()
        assert BiasType.POLITICAL in engine.bias_patterns
        assert BiasType.COMMERCIAL in engine.bias_patterns
        assert BiasType.CONFIRMATION in engine.bias_patterns
        assert BiasType.LANGUAGE in engine.bias_patterns
    
    @pytest.mark.asyncio
    async def test_detect_political_bias_left(self):
        """Test detection of left-leaning political bias"""
        engine = BiasDetectionEngine()
        
        content = "This progressive policy promotes social justice and equality for all citizens"
        bias = await engine._detect_political_bias(content)
        
        assert bias < 0  # Should detect left bias
    
    @pytest.mark.asyncio
    async def test_detect_political_bias_right(self):
        """Test detection of right-leaning political bias"""
        engine = BiasDetectionEngine()
        
        content = "Conservative free market policies support individual rights and small government"
        bias = await engine._detect_political_bias(content)
        
        assert bias > 0  # Should detect right bias
    
    @pytest.mark.asyncio
    async def test_detect_political_bias_neutral(self):
        """Test detection of neutral political content"""
        engine = BiasDetectionEngine()
        
        content = "This bipartisan objective analysis presents factual information"
        bias = await engine._detect_political_bias(content)
        
        assert abs(bias) < 0.2  # Should be relatively neutral
    
    @pytest.mark.asyncio
    async def test_detect_commercial_bias_high(self):
        """Test detection of high commercial bias"""
        engine = BiasDetectionEngine()
        
        content = "Buy now with our exclusive discount offer! Limited time deal on this amazing product."
        metadata = {"url": "https://shop.example.com", "title": "Best Product Sale"}
        
        bias = await engine._detect_commercial_bias(content, metadata)
        
        assert bias > 0.5  # Should detect high commercial bias
    
    @pytest.mark.asyncio
    async def test_detect_commercial_bias_low(self):
        """Test detection of low commercial bias"""
        engine = BiasDetectionEngine()
        
        content = "Technical analysis of software architecture patterns and their applications"
        metadata = {"url": "https://research.example.org", "title": "Technical Analysis"}
        
        bias = await engine._detect_commercial_bias(content, metadata)
        
        assert bias < 0.3  # Should detect low commercial bias
    
    @pytest.mark.asyncio
    async def test_detect_confirmation_bias_high(self):
        """Test detection of high confirmation bias"""
        engine = BiasDetectionEngine()
        
        content = "Obviously, this clearly proves that everyone knows the truth about this fact"
        bias = await engine._detect_confirmation_bias(content)
        
        assert bias > 0.5  # Should detect confirmation bias
    
    @pytest.mark.asyncio
    async def test_detect_confirmation_bias_low(self):
        """Test detection of low confirmation bias"""
        engine = BiasDetectionEngine()
        
        content = "The study suggests that there may be some correlation, though more research is needed"
        bias = await engine._detect_confirmation_bias(content)
        
        assert bias < 0.3  # Should detect low confirmation bias
    
    @pytest.mark.asyncio
    async def test_detect_language_bias_high(self):
        """Test detection of biased language"""
        engine = BiasDetectionEngine()
        
        content = "This SHOCKING revelation is absolutely DEVASTATING!!! The elite establishment spreads fake news!"
        bias = await engine._detect_language_bias(content)
        
        assert bias > 0.5  # Should detect language bias
    
    @pytest.mark.asyncio
    async def test_detect_language_bias_low(self):
        """Test detection of neutral language"""
        engine = BiasDetectionEngine()
        
        content = "The research indicates moderate improvements in performance metrics"
        bias = await engine._detect_language_bias(content)
        
        assert bias < 0.3  # Should detect neutral language
    
    @pytest.mark.asyncio
    async def test_comprehensive_bias_detection(self):
        """Test comprehensive bias detection"""
        engine = BiasDetectionEngine()
        
        content = "This conservative approach shows amazing results! Buy our solution now!"
        metadata = {"url": "https://shop.conservative.com", "title": "Amazing Conservative Solution"}
        
        assessment = await engine.detect_bias(content, metadata)
        
        assert isinstance(assessment, BiasAssessment)
        assert assessment.political_bias > 0  # Right bias
        assert assessment.commercial_bias > 0.5  # Commercial bias
        assert assessment.language_bias > 0  # Emotional language
        assert assessment.overall_bias_score > 0.3
        assert len(assessment.detected_bias_types) > 0
        assert assessment.confidence > 0

class TestSourceCredibilityAssessor:
    """Test the main source credibility assessor"""
    
    def test_initialization(self):
        """Test assessor initialization"""
        assessor = SourceCredibilityAssessor()
        assert assessor.domain_authority_db is not None
        assert assessor.author_expertise_db is not None
        assert assessor.bias_detector is not None
    
    @pytest.mark.asyncio
    async def test_assess_source_failed_content(self):
        """Test assessment of failed content"""
        assessor = SourceCredibilityAssessor()
        
        content = EnhancedScrapedContent(
            url="https://example.com",
            success=False,
            error="Failed to scrape"
        )
        
        score = await assessor.assess_source(content)
        
        assert isinstance(score, SourceCredibilityScore)
        assert score.overall_credibility == 0.0
    
    @pytest.mark.asyncio
    async def test_assess_source_academic(self):
        """Test assessment of academic source"""
        assessor = SourceCredibilityAssessor()
        
        content = EnhancedScrapedContent(
            url="https://arxiv.org/paper123",
            title="Machine Learning Research Paper",
            clean_text="""
            Abstract: This research presents a novel algorithm for machine learning optimization.
            
            Introduction: Recent advances in AI have shown promising results...
            
            Methodology: We conducted experiments using standard datasets...
            
            Results: Our algorithm achieved 95% accuracy on benchmark tests...
            
            References: [1] Smith et al. (2020) doi:10.1234/example
            """,
            success=True,
            metadata={
                "author": "Dr. Jane Smith, PhD, Stanford University",
                "published_date": "2024-01-15T10:00:00Z"
            }
        )
        
        score = await assessor.assess_source(content)
        
        assert score.domain_authority >= 0.9  # arxiv.org high authority
        assert score.author_expertise >= 0.7  # Academic credentials
        assert score.publication_quality >= 0.5  # Good structure and citations
        assert score.peer_review_status >= 0.8  # Academic domain
        assert score.source_type == SourceType.ACADEMIC
        assert score.overall_credibility >= 0.6
    
    @pytest.mark.asyncio
    async def test_assess_source_commercial(self):
        """Test assessment of commercial source"""
        assessor = SourceCredibilityAssessor()
        
        content = EnhancedScrapedContent(
            url="https://shop.example.com/product",
            title="Best AI Tool - Buy Now!",
            clean_text="""
            Amazing AI solution! Buy now and get 50% discount!
            
            Our revolutionary product is the best in the market.
            Limited time offer - don't miss out!
            
            Click here to purchase and transform your business today!
            """,
            success=True,
            metadata={
                "author": "Marketing Team",
                "published_date": "2024-12-01T10:00:00Z"
            }
        )
        
        score = await assessor.assess_source(content)
        
        assert score.domain_authority <= 0.5  # Commercial domain
        assert score.author_expertise <= 0.3  # No clear expertise
        assert score.publication_quality <= 0.3  # Poor quality content
        assert score.bias_assessment.commercial_bias >= 0.5  # High commercial bias
        assert score.overall_credibility <= 0.4
    
    @pytest.mark.asyncio
    async def test_assess_publication_quality_high(self):
        """Test assessment of high-quality publication"""
        assessor = SourceCredibilityAssessor()
        
        content = EnhancedScrapedContent(
            url="https://example.com",
            clean_text="""
            Abstract: This comprehensive study analyzes machine learning algorithms.
            
            Introduction: The field of artificial intelligence has rapidly evolved...
            
            Methodology: We employed a rigorous experimental approach using validated datasets...
            
            Results: Statistical analysis revealed significant improvements (p < 0.05)...
            
            Conclusion: Our research demonstrates the effectiveness of the proposed algorithm...
            
            References: [1] Anderson et al. (2020) doi:10.1000/182
            [2] Brown, J. (2019) "Machine Learning Advances"
            """,
            success=True
        )
        
        quality = await assessor._assess_publication_quality(content)
        
        assert quality >= 0.6  # High quality due to structure, length, citations
    
    @pytest.mark.asyncio
    async def test_assess_publication_quality_low(self):
        """Test assessment of low-quality publication"""
        assessor = SourceCredibilityAssessor()
        
        content = EnhancedScrapedContent(
            url="https://example.com",
            clean_text="AI is good. It helps people. Very useful technology.",
            success=True
        )
        
        quality = await assessor._assess_publication_quality(content)
        
        assert quality <= 0.3  # Low quality due to short length, no structure
    
    @pytest.mark.asyncio
    async def test_assess_peer_review_status_academic(self):
        """Test peer review assessment for academic domains"""
        assessor = SourceCredibilityAssessor()
        
        content = EnhancedScrapedContent(
            url="https://nature.com/article",
            clean_text="This peer-reviewed journal article presents research findings",
            success=True
        )
        
        peer_review = await assessor._assess_peer_review_status(content, "nature.com")
        
        assert peer_review >= 0.8  # High probability for academic domain
    
    @pytest.mark.asyncio
    async def test_assess_peer_review_status_non_academic(self):
        """Test peer review assessment for non-academic domains"""
        assessor = SourceCredibilityAssessor()
        
        content = EnhancedScrapedContent(
            url="https://blog.example.com",
            clean_text="Personal blog post about technology trends",
            success=True
        )
        
        peer_review = await assessor._assess_peer_review_status(content, "blog.example.com")
        
        assert peer_review <= 0.3  # Low probability for blog
    
    @pytest.mark.asyncio
    async def test_assess_recency_recent(self):
        """Test recency assessment for recent content"""
        assessor = SourceCredibilityAssessor()
        
        recent_date = (datetime.now() - timedelta(days=10)).isoformat()
        
        content = EnhancedScrapedContent(
            url="https://example.com",
            clean_text="Recent article",
            success=True,
            metadata={"published_date": recent_date}
        )
        
        recency = await assessor._assess_recency(content)
        
        assert recency >= 0.7  # High recency score
    
    @pytest.mark.asyncio
    async def test_assess_recency_old(self):
        """Test recency assessment for old content"""
        assessor = SourceCredibilityAssessor()
        
        old_date = (datetime.now() - timedelta(days=2000)).isoformat()
        
        content = EnhancedScrapedContent(
            url="https://example.com",
            clean_text="Old article",
            success=True,
            metadata={"published_date": old_date}
        )
        
        recency = await assessor._assess_recency(content)
        
        assert recency <= 0.5  # Low recency score
    
    def test_determine_source_type_academic(self):
        """Test source type determination for academic sources"""
        assessor = SourceCredibilityAssessor()
        
        source_type = assessor._determine_source_type("arxiv.org", {})
        assert source_type == SourceType.ACADEMIC
        
        source_type = assessor._determine_source_type("university.edu", {})
        assert source_type == SourceType.ACADEMIC
    
    def test_determine_source_type_government(self):
        """Test source type determination for government sources"""
        assessor = SourceCredibilityAssessor()
        
        source_type = assessor._determine_source_type("nih.gov", {})
        assert source_type == SourceType.GOVERNMENT
        
        source_type = assessor._determine_source_type("who.int", {})
        assert source_type == SourceType.GOVERNMENT
    
    def test_determine_source_type_news(self):
        """Test source type determination for news sources"""
        assessor = SourceCredibilityAssessor()
        
        source_type = assessor._determine_source_type("reuters.com", {})
        assert source_type == SourceType.NEWS
        
        source_type = assessor._determine_source_type("bbc.com", {})
        assert source_type == SourceType.NEWS
    
    def test_determine_source_type_industry(self):
        """Test source type determination for industry sources"""
        assessor = SourceCredibilityAssessor()
        
        source_type = assessor._determine_source_type("google.com", {})
        assert source_type == SourceType.INDUSTRY
        
        source_type = assessor._determine_source_type("github.com", {})
        assert source_type == SourceType.INDUSTRY

class TestIntegration:
    """Integration tests for credibility assessment"""
    
    @pytest.mark.asyncio
    async def test_full_credibility_assessment_pipeline(self):
        """Test the complete credibility assessment pipeline"""
        assessor = SourceCredibilityAssessor()
        
        # Test with multiple content types
        content_items = [
            # High credibility academic source
            EnhancedScrapedContent(
                url="https://nature.com/articles/s41586-024-07123-4",
                title="Advances in Machine Learning: A Comprehensive Study",
                clean_text="""
                Abstract: This peer-reviewed study examines recent advances in machine learning algorithms.
                
                Introduction: The rapid development of AI technologies has led to significant improvements...
                
                Methodology: We conducted a systematic review of 150 research papers published between 2020-2024...
                
                Results: Our analysis reveals three key trends in algorithm performance...
                
                Discussion: These findings have important implications for future research directions...
                
                References: [1] Smith, J. et al. (2023) Nature Machine Intelligence
                [2] doi:10.1038/s42256-023-00123-4
                """,
                success=True,
                metadata={
                    "author": "Dr. Sarah Johnson, PhD, MIT Computer Science Department",
                    "published_date": "2024-01-15T10:00:00Z"
                }
            ),
            
            # Low credibility commercial source
            EnhancedScrapedContent(
                url="https://ai-miracle-solutions.biz/revolutionary-ai",
                title="REVOLUTIONARY AI BREAKTHROUGH - 1000x Performance!!!",
                clean_text="""
                AMAZING breakthrough in AI technology! Our proprietary algorithm is 1000x faster than anything else!
                
                BUY NOW and get EXCLUSIVE access to this game-changing technology!
                Limited time offer - 90% discount only today!
                
                Don't let your competitors get ahead - this is obviously the best solution ever created!
                
                Click here to purchase immediately and transform your business overnight!
                """,
                success=True,
                metadata={
                    "author": "AI Solutions Team",
                    "published_date": "2024-12-01T10:00:00Z"
                }
            )
        ]
        
        # Assess both sources
        scores = []
        for content in content_items:
            score = await assessor.assess_source(content)
            scores.append(score)
        
        academic_score, commercial_score = scores
        
        # Academic source should have high credibility
        assert academic_score.domain_authority >= 0.8
        assert academic_score.publication_quality >= 0.5
        assert academic_score.peer_review_status >= 0.8
        assert academic_score.source_type == SourceType.ACADEMIC
        assert academic_score.overall_credibility >= 0.6
        
        # Commercial source should have low credibility
        assert commercial_score.domain_authority <= 0.4
        assert commercial_score.publication_quality <= 0.3
        assert commercial_score.bias_assessment.commercial_bias >= 0.5
        assert commercial_score.bias_assessment.language_bias >= 0.5
        assert commercial_score.overall_credibility <= 0.4
        
        # Academic should be significantly more credible than commercial
        assert academic_score.overall_credibility > commercial_score.overall_credibility + 0.2

if __name__ == "__main__":
    pytest.main([__file__]) 