"""
Tests for the core research models
"""

import pytest
from datetime import datetime
import uuid

from agent_creator.core.research_models import (
    ResearchQuery, ResearchType, SourceType, BiasType,
    ExtractedReference, URLValidationResult, BiasAssessment,
    SourceCredibilityScore, Claim, Contradiction, ResearchQualityMetrics,
    ResearchGaps, ThematicAnalysis, ContradictionReport,
    EvidenceSynthesis, EnhancedScrapedContent, EnhancedResearchResult
)

class TestResearchModels:
    """Test cases for research data models"""
    
    def test_research_query_creation(self):
        """Test ResearchQuery creation and defaults"""
        query = ResearchQuery(primary_question="How does AI impact software development?")
        
        assert query.primary_question == "How does AI impact software development?"
        assert isinstance(query.query_id, str)
        assert len(query.query_id) > 0
        assert query.research_type == ResearchType.EXPLORATORY
        assert query.sub_questions == []
        assert query.quality_threshold == 0.7
        assert query.max_sources == 50
        assert isinstance(query.created_at, datetime)
    
    def test_research_query_with_full_params(self):
        """Test ResearchQuery with all parameters"""
        sub_questions = ["What are the benefits?", "What are the risks?"]
        domains = ["software engineering", "AI"]
        
        query = ResearchQuery(
            primary_question="AI impact on software development",
            sub_questions=sub_questions,
            research_type=ResearchType.COMPARATIVE,
            domain_expertise_required=domains,
            time_scope="2020-2025",
            geographical_scope="Global",
            preferred_source_types=[SourceType.ACADEMIC, SourceType.INDUSTRY],
            bias_considerations=["commercial bias", "selection bias"],
            quality_threshold=0.8,
            max_sources=100
        )
        
        assert query.sub_questions == sub_questions
        assert query.research_type == ResearchType.COMPARATIVE
        assert query.domain_expertise_required == domains
        assert query.time_scope == "2020-2025"
        assert query.geographical_scope == "Global"
        assert SourceType.ACADEMIC in query.preferred_source_types
        assert query.quality_threshold == 0.8
        assert query.max_sources == 100
    
    def test_extracted_reference_creation(self):
        """Test ExtractedReference creation"""
        ref = ExtractedReference(
            value="https://example.com/paper.pdf",
            reference_type="url",
            page_number=1,
            context="This paper discusses AI impacts",
            confidence=0.9
        )
        
        assert ref.value == "https://example.com/paper.pdf"
        assert ref.reference_type == "url"
        assert ref.page_number == 1
        assert ref.context == "This paper discusses AI impacts"
        assert ref.confidence == 0.9
        assert ref.resolved_url is None
        assert ref.metadata == {}
    
    def test_url_validation_result(self):
        """Test URLValidationResult"""
        result = URLValidationResult(
            original_url="https://example.com",
            is_accessible=True,
            final_url="https://example.com/redirected",
            status_code=200,
            content_type="text/html"
        )
        
        assert result.original_url == "https://example.com"
        assert result.is_accessible is True
        assert result.final_url == "https://example.com/redirected"
        assert result.status_code == 200
        assert result.content_type == "text/html"
        assert isinstance(result.validation_timestamp, datetime)
    
    def test_bias_assessment_creation(self):
        """Test BiasAssessment creation and properties"""
        bias = BiasAssessment(
            political_bias=0.2,
            commercial_bias=0.7,
            confirmation_bias=0.3,
            language_bias=0.1,
            detected_bias_types=[BiasType.COMMERCIAL, BiasType.POLITICAL],
            confidence=0.85
        )
        
        assert bias.political_bias == 0.2
        assert bias.commercial_bias == 0.7
        assert bias.confirmation_bias == 0.3
        assert bias.language_bias == 0.1
        assert BiasType.COMMERCIAL in bias.detected_bias_types
        assert bias.confidence == 0.85
    
    def test_source_credibility_score_calculation(self):
        """Test SourceCredibilityScore overall calculation"""
        bias = BiasAssessment(overall_bias_score=0.3)
        
        score = SourceCredibilityScore(
            domain_authority=0.8,
            author_expertise=0.9,
            publication_quality=0.7,
            peer_review_status=1.0,
            citation_count=0.6,
            recency=0.8,
            bias_assessment=bias,
            source_type=SourceType.ACADEMIC
        )
        
        # Test calculation
        expected = (0.8 * 0.15 + 0.9 * 0.20 + 0.7 * 0.20 + 
                   1.0 * 0.15 + 0.6 * 0.10 + 0.8 * 0.05) - (0.3 * 0.15)
        
        assert abs(score.overall_credibility - expected) < 0.001
        assert 0 <= score.overall_credibility <= 1
    
    def test_source_credibility_with_high_bias(self):
        """Test that high bias reduces credibility score"""
        high_bias = BiasAssessment(overall_bias_score=0.9)
        low_bias = BiasAssessment(overall_bias_score=0.1)
        
        base_params = {
            'domain_authority': 0.8,
            'author_expertise': 0.8,
            'publication_quality': 0.8,
            'peer_review_status': 0.8,
            'citation_count': 0.8,
            'recency': 0.8
        }
        
        high_bias_score = SourceCredibilityScore(**base_params, bias_assessment=high_bias, source_type=SourceType.ACADEMIC)
        low_bias_score = SourceCredibilityScore(**base_params, bias_assessment=low_bias, source_type=SourceType.ACADEMIC)
        
        assert high_bias_score.overall_credibility < low_bias_score.overall_credibility
    
    def test_claim_creation(self):
        """Test Claim creation"""
        claim = Claim(
            text="AI will increase software development productivity by 50% by 2025",
            source_url="https://example.com/study",
            source_credibility=0.8,
            confidence=0.7,
            claim_type="prediction",
            entities=["AI", "software development", "productivity"]
        )
        
        assert claim.text == "AI will increase software development productivity by 50% by 2025"
        assert isinstance(claim.claim_id, str)
        assert claim.source_url == "https://example.com/study"
        assert claim.source_credibility == 0.8
        assert claim.confidence == 0.7
        assert claim.claim_type == "prediction"
        assert "AI" in claim.entities
        assert isinstance(claim.extracted_at, datetime)
    
    def test_contradiction_creation(self):
        """Test Contradiction between claims"""
        claim1 = Claim(text="AI improves software quality")
        claim2 = Claim(text="AI decreases software quality")
        
        contradiction = Contradiction(
            claim1=claim1,
            claim2=claim2,
            contradiction_type="direct",
            confidence=0.9,
            explanation="Direct opposite claims about AI's impact on quality",
            severity="high"
        )
        
        assert contradiction.claim1 == claim1
        assert contradiction.claim2 == claim2
        assert contradiction.contradiction_type == "direct"
        assert contradiction.confidence == 0.9
        assert contradiction.severity == "high"
    
    def test_research_quality_metrics_calculation(self):
        """Test ResearchQualityMetrics overall calculation"""
        metrics = ResearchQualityMetrics(
            source_diversity=0.8,
            temporal_coverage=0.7,
            expert_validation=0.9,
            cross_validation=0.6,
            bias_assessment=0.8,
            completeness=0.7,
            recency=0.9,
            methodology_adherence=0.8
        )
        
        # Test calculation
        expected = (0.8 * 0.12 + 0.7 * 0.10 + 0.9 * 0.18 + 0.6 * 0.20 + 
                   0.8 * 0.15 + 0.7 * 0.15 + 0.9 * 0.05 + 0.8 * 0.05)
        
        assert abs(metrics.overall_quality - expected) < 0.001
        assert 0 <= metrics.overall_quality <= 1
    
    def test_research_gaps_creation(self):
        """Test ResearchGaps creation"""
        gaps = ResearchGaps(
            unanswered_questions=["What about long-term effects?"],
            missing_source_types=[SourceType.GOVERNMENT],
            temporal_gaps=["Pre-2020 data missing"],
            perspective_gaps=["Industry perspective missing"],
            recommendations=["Conduct longitudinal study"]
        )
        
        assert "What about long-term effects?" in gaps.unanswered_questions
        assert SourceType.GOVERNMENT in gaps.missing_source_types
        assert "Pre-2020 data missing" in gaps.temporal_gaps
        assert "Industry perspective missing" in gaps.perspective_gaps
        assert "Conduct longitudinal study" in gaps.recommendations
    
    def test_enhanced_scraped_content(self):
        """Test EnhancedScrapedContent creation"""
        credibility = SourceCredibilityScore(domain_authority=0.8)
        bias = BiasAssessment(commercial_bias=0.2)
        
        content = EnhancedScrapedContent(
            url="https://example.com/article",
            title="AI in Software Development",
            clean_text="AI is transforming software development...",
            success=True,
            source_type=SourceType.ACADEMIC,
            credibility_score=credibility,
            bias_assessment=bias,
            language="en",
            readability_score=0.7,
            sentiment_score=0.1
        )
        
        assert content.url == "https://example.com/article"
        assert content.title == "AI in Software Development"
        assert content.success is True
        assert content.source_type == SourceType.ACADEMIC
        assert content.credibility_score == credibility
        assert content.bias_assessment == bias
        assert content.language == "en"
        assert content.readability_score == 0.7
        assert isinstance(content.scraped_at, datetime)
    
    def test_enhanced_research_result(self):
        """Test EnhancedResearchResult creation"""
        query = ResearchQuery(primary_question="Test question")
        content = EnhancedScrapedContent(url="https://example.com", success=True)
        quality_metrics = ResearchQualityMetrics(source_diversity=0.8)
        
        result = EnhancedResearchResult(
            query=query,
            methodology_used="rapid_assessment",
            sources=[content],
            quality_metrics=quality_metrics,
            executive_summary="This is a test summary",
            completion_time=45.2
        )
        
        assert result.query == query
        assert result.methodology_used == "rapid_assessment"
        assert len(result.sources) == 1
        assert result.sources[0] == content
        assert result.quality_metrics == quality_metrics
        assert result.executive_summary == "This is a test summary"
        assert result.completion_time == 45.2
        assert isinstance(result.timestamp, datetime)
    
    def test_evidence_synthesis(self):
        """Test EvidenceSynthesis data structure"""
        synthesis = EvidenceSynthesis(
            weighted_evidence={"claim1": 0.8, "claim2": 0.6},
            consensus_positions=["AI improves productivity"],
            uncertainty_assessment={"productivity": 0.2},
            synthesis_text="Based on analysis...",
            confidence_intervals={"productivity": (0.4, 0.8)},
            reliability_score=0.75,
            evidence_strength="moderate"
        )
        
        assert synthesis.weighted_evidence["claim1"] == 0.8
        assert "AI improves productivity" in synthesis.consensus_positions
        assert synthesis.uncertainty_assessment["productivity"] == 0.2
        assert synthesis.reliability_score == 0.75
        assert synthesis.evidence_strength == "moderate"
        assert synthesis.confidence_intervals["productivity"] == (0.4, 0.8)
    
    def test_contradiction_report(self):
        """Test ContradictionReport structure"""
        claim1 = Claim(text="AI is beneficial")
        claim2 = Claim(text="AI is harmful")
        contradiction = Contradiction(claim1=claim1, claim2=claim2)
        
        report = ContradictionReport(
            total_claims=10,
            contradiction_groups=[[contradiction]],
            reliability_assessment={"overall": 0.7},
            consensus_points=["AI has impacts"],
            disputed_points=["Direction of impact"],
            confidence_intervals={"impact": (0.3, 0.9)}
        )
        
        assert report.total_claims == 10
        assert len(report.contradiction_groups) == 1
        assert len(report.contradiction_groups[0]) == 1
        assert report.reliability_assessment["overall"] == 0.7
        assert "AI has impacts" in report.consensus_points
        assert "Direction of impact" in report.disputed_points

if __name__ == "__main__":
    pytest.main([__file__]) 