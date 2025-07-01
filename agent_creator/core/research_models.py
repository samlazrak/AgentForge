"""
Core data models for the enhanced research system
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
from enum import Enum
import uuid

class ResearchType(Enum):
    """Types of research methodologies"""
    EXPLORATORY = "exploratory"
    COMPARATIVE = "comparative"
    CAUSAL = "causal"
    DESCRIPTIVE = "descriptive"
    SYSTEMATIC_REVIEW = "systematic_review"
    RAPID_ASSESSMENT = "rapid_assessment"

class SourceType(Enum):
    """Types of information sources"""
    ACADEMIC = "academic"
    NEWS = "news"
    GOVERNMENT = "government"
    INDUSTRY = "industry"
    EXPERT_BLOG = "expert_blog"
    SOCIAL_MEDIA = "social_media"
    REPOSITORY = "repository"
    DOCUMENTATION = "documentation"

class BiasType(Enum):
    """Types of bias that can be detected"""
    POLITICAL = "political"
    COMMERCIAL = "commercial"
    CONFIRMATION = "confirmation"
    LANGUAGE = "language"
    SELECTION = "selection"
    TEMPORAL = "temporal"

@dataclass
class ResearchQuery:
    """Structured research query with methodology"""
    primary_question: str
    query_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sub_questions: List[str] = field(default_factory=list)
    research_type: ResearchType = ResearchType.EXPLORATORY
    domain_expertise_required: List[str] = field(default_factory=list)
    time_scope: Optional[str] = None  # "recent", "historical", "2020-2025"
    geographical_scope: Optional[str] = None
    preferred_source_types: List[SourceType] = field(default_factory=list)
    bias_considerations: List[str] = field(default_factory=list)
    quality_threshold: float = 0.7
    max_sources: int = 50
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ExtractedReference:
    """Enhanced reference extracted from documents"""
    value: str
    reference_type: str  # "url", "doi", "citation", "isbn"
    page_number: int = 0
    context: str = ""
    confidence: float = 0.0
    resolved_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    extraction_method: str = ""
    bbox: Optional[Tuple[float, float, float, float]] = None

@dataclass
class URLValidationResult:
    """Result of URL validation and enhancement"""
    original_url: str
    is_accessible: bool = False
    final_url: Optional[str] = None
    status_code: Optional[int] = None
    content_type: Optional[str] = None
    last_modified: Optional[str] = None
    redirect_chain: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    validation_timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class BiasAssessment:
    """Assessment of bias in content"""
    political_bias: float = 0.0  # -1 (left) to 1 (right)
    commercial_bias: float = 0.0  # 0 (none) to 1 (high commercial interest)
    confirmation_bias: float = 0.0  # 0 (none) to 1 (high confirmation bias)
    language_bias: float = 0.0  # 0 (neutral) to 1 (highly biased language)
    selection_bias: float = 0.0  # 0 (none) to 1 (high selection bias)
    temporal_bias: float = 0.0  # 0 (current) to 1 (outdated perspective)
    overall_bias_score: float = 0.0  # 0 (unbiased) to 1 (highly biased)
    detected_bias_types: List[BiasType] = field(default_factory=list)
    confidence: float = 0.0

@dataclass
class SourceCredibilityScore:
    """Comprehensive source credibility assessment"""
    domain_authority: float = 0.0  # 0-1
    author_expertise: float = 0.0  # 0-1
    publication_quality: float = 0.0  # 0-1
    peer_review_status: float = 0.0  # 0-1
    citation_count: float = 0.0  # 0-1 (normalized)
    recency: float = 0.0  # 0-1
    bias_assessment: BiasAssessment = field(default_factory=BiasAssessment)
    source_type: SourceType = SourceType.INDUSTRY
    
    @property
    def overall_credibility(self) -> float:
        """Calculate overall credibility score"""
        weights = {
            'domain_authority': 0.15,
            'author_expertise': 0.20,
            'publication_quality': 0.20,
            'peer_review_status': 0.15,
            'citation_count': 0.10,
            'recency': 0.05,
        }
        
        score = sum(getattr(self, metric) * weight 
                   for metric, weight in weights.items())
        
        # Apply bias penalty
        bias_penalty = self.bias_assessment.overall_bias_score * 0.15
        score = max(0, score - bias_penalty)
        
        return min(1.0, score)

@dataclass
class Claim:
    """Factual claim extracted from content"""
    text: str
    claim_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_url: str = ""
    source_credibility: float = 0.0
    confidence: float = 0.0
    claim_type: str = "factual"  # factual, opinion, prediction, statistic
    temporal_context: Optional[str] = None
    supporting_evidence: List[str] = field(default_factory=list)
    contradicting_evidence: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    extracted_at: datetime = field(default_factory=datetime.now)

@dataclass
class Contradiction:
    """Detected contradiction between claims"""
    claim1: Claim
    claim2: Claim
    contradiction_type: str = "direct"  # direct, semantic, temporal, contextual
    confidence: float = 0.0
    explanation: str = ""
    evidence: List[str] = field(default_factory=list)
    severity: str = "medium"  # low, medium, high, critical
    resolution_suggestion: Optional[str] = None

@dataclass
class ResearchQualityMetrics:
    """Comprehensive research quality assessment"""
    source_diversity: float = 0.0  # 0-1, diversity of source types
    temporal_coverage: float = 0.0  # 0-1, how well time scope is covered
    expert_validation: float = 0.0  # 0-1, presence of expert/authoritative sources
    cross_validation: float = 0.0  # 0-1, how well claims are cross-validated
    bias_assessment: float = 0.0  # 0-1, bias detection and mitigation
    completeness: float = 0.0  # 0-1, coverage of research questions
    recency: float = 0.0  # 0-1, relevance of temporal information
    methodology_adherence: float = 0.0  # 0-1, adherence to research methodology
    
    @property
    def overall_quality(self) -> float:
        """Calculate overall quality score"""
        weights = {
            'source_diversity': 0.12,
            'temporal_coverage': 0.10,
            'expert_validation': 0.18,
            'cross_validation': 0.20,
            'bias_assessment': 0.15,
            'completeness': 0.15,
            'recency': 0.05,
            'methodology_adherence': 0.05
        }
        
        return sum(getattr(self, metric) * weight 
                  for metric, weight in weights.items())

@dataclass
class ResearchGaps:
    """Identified gaps in research coverage"""
    unanswered_questions: List[str] = field(default_factory=list)
    missing_source_types: List[SourceType] = field(default_factory=list)
    temporal_gaps: List[str] = field(default_factory=list)
    perspective_gaps: List[str] = field(default_factory=list)
    evidence_gaps: List[str] = field(default_factory=list)
    geographical_gaps: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

@dataclass
class ThematicAnalysis:
    """Results of thematic analysis"""
    topics: List[Dict[str, Any]] = field(default_factory=list)
    themes: List[Dict[str, Any]] = field(default_factory=list)
    clusters: List[List[int]] = field(default_factory=list)
    topic_evolution: Dict[str, Any] = field(default_factory=dict)
    contradictions: List[Contradiction] = field(default_factory=list)
    sentiment_analysis: Dict[str, float] = field(default_factory=dict)
    key_entities: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class ContradictionReport:
    """Report of detected contradictions"""
    total_claims: int = 0
    contradiction_groups: List[List[Contradiction]] = field(default_factory=list)
    reliability_assessment: Dict[str, float] = field(default_factory=dict)
    consensus_points: List[str] = field(default_factory=list)
    disputed_points: List[str] = field(default_factory=list)
    confidence_intervals: Dict[str, Tuple[float, float]] = field(default_factory=dict)

@dataclass
class EvidenceSynthesis:
    """Synthesized evidence from multiple sources"""
    weighted_evidence: Dict[str, float] = field(default_factory=dict)
    consensus_positions: List[str] = field(default_factory=list)
    uncertainty_assessment: Dict[str, float] = field(default_factory=dict)
    synthesis_text: str = ""
    confidence_intervals: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    reliability_score: float = 0.0
    evidence_strength: str = "weak"  # weak, moderate, strong, very_strong

@dataclass
class EnhancedScrapedContent:
    """Enhanced version of scraped content with analysis"""
    url: str
    title: str = ""
    clean_text: str = ""
    raw_text: str = ""
    images: List[str] = field(default_factory=list)
    links: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    success: bool = False
    error: Optional[str] = None
    
    # Enhanced fields
    source_type: SourceType = SourceType.INDUSTRY
    credibility_score: SourceCredibilityScore = field(default_factory=SourceCredibilityScore)
    bias_assessment: BiasAssessment = field(default_factory=BiasAssessment)
    extracted_claims: List[Claim] = field(default_factory=list)
    entities: List[Dict[str, Any]] = field(default_factory=list)
    language: str = "en"
    readability_score: float = 0.0
    sentiment_score: float = 0.0
    scraped_at: datetime = field(default_factory=datetime.now)

@dataclass
class EnhancedResearchResult:
    """Comprehensive research result with full analysis"""
    query: ResearchQuery
    methodology_used: str = ""
    sources: List[EnhancedScrapedContent] = field(default_factory=list)
    thematic_analysis: ThematicAnalysis = field(default_factory=ThematicAnalysis)
    credibility_scores: Dict[str, SourceCredibilityScore] = field(default_factory=dict)
    contradictions: ContradictionReport = field(default_factory=ContradictionReport)
    evidence_synthesis: EvidenceSynthesis = field(default_factory=EvidenceSynthesis)
    quality_metrics: ResearchQualityMetrics = field(default_factory=ResearchQualityMetrics)
    research_gaps: ResearchGaps = field(default_factory=ResearchGaps)
    recommendations: List[str] = field(default_factory=list)
    executive_summary: str = ""
    full_report: str = ""
    completion_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now) 