"""Report generation for the Deep Research System."""

import logging
import os
import re
from typing import List

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logging.error("reportlab library required but not available")

from ..models.data_models import ResearchResult


class ReportGenerator:
    """Generates research reports and summaries"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_summary(self, research_result: ResearchResult) -> str:
        """Generate a research summary"""
        query = research_result.query
        total_content = research_result.level_1_content + research_result.level_2_content
        relevant_content = [c for c in total_content if c.success and c.relevance_score > 0.1]
        
        if not relevant_content:
            return f"No relevant content found for query: {query}"
        
        # Extract key points from most relevant content
        top_content = sorted(relevant_content, key=lambda x: x.relevance_score, reverse=True)[:5]
        
        summary_parts = [
            f"Research Summary for: {query}",
            f"",
            f"Total sources searched: {len(research_result.initial_results)}",
            f"Total pages crawled: {research_result.total_pages_crawled}",
            f"Relevant sources found: {len(relevant_content)}",
            f"",
            f"Key Findings:"
        ]
        
        for i, content in enumerate(top_content, 1):
            # Extract first meaningful paragraph
            paragraphs = content.content.split('\n')
            meaningful_content = ""
            
            for para in paragraphs:
                if len(para.strip()) > 50 and self._is_meaningful_text(para):
                    meaningful_content = para.strip()[:300] + "..."
                    break
            
            if meaningful_content:
                summary_parts.append(f"{i}. From {content.title or content.url}:")
                summary_parts.append(f"   {meaningful_content}")
                summary_parts.append("")
        
        return "\n".join(summary_parts)
    
    def _is_meaningful_text(self, text: str) -> bool:
        """Check if text contains meaningful content"""
        # Skip navigation, headers, footers, etc.
        skip_patterns = [
            'copyright', 'all rights reserved', 'privacy policy', 'terms of service',
            'navigation', 'menu', 'footer', 'header', 'subscribe', 'login', 'sign up'
        ]
        
        text_lower = text.lower()
        return not any(pattern in text_lower for pattern in skip_patterns)
    
    def extract_key_findings(self, research_result: ResearchResult) -> List[str]:
        """Extract key findings from research content"""
        total_content = research_result.level_1_content + research_result.level_2_content
        relevant_content = [c for c in total_content if c.success and c.relevance_score > 0.2]
        
        findings = []
        query_words = research_result.query.lower().split()
        
        for content in relevant_content[:10]:  # Top 10 most relevant
            # Extract sentences that contain query words
            sentences = re.split(r'[.!?]+', content.content)
            
            for sentence in sentences:
                sentence = sentence.strip()
                if (len(sentence) > 30 and 
                    any(word in sentence.lower() for word in query_words) and
                    self._is_meaningful_text(sentence)):
                    
                    findings.append(f"{sentence} (Source: {content.title or content.url})")
                    
                    if len(findings) >= 10:
                        break
            
            if len(findings) >= 10:
                break
        
        return findings


class PDFGenerator:
    """Generates PDF reports from research results"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_pdf(self, research_result: ResearchResult, output_path: str) -> bool:
        """Generate a comprehensive PDF report"""
        if not PDF_AVAILABLE:
            self.logger.error("ReportLab not available - cannot generate PDF")
            return False
        
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            doc = SimpleDocTemplate(output_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Title page
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1
            )
            
            story.append(Paragraph(f"Deep Research Report", title_style))
            story.append(Spacer(1, 12))
            story.append(Paragraph(f"Query: {research_result.query}", styles['Heading2']))
            story.append(Spacer(1, 12))
            story.append(Paragraph(f"Generated: {research_result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            story.append(PageBreak())
            
            # Executive Summary
            story.append(Paragraph("Executive Summary", styles['Heading1']))
            story.append(Spacer(1, 12))
            
            summary_paragraphs = research_result.summary.split('\n\n')
            for para in summary_paragraphs:
                if para.strip():
                    story.append(Paragraph(para.strip(), styles['Normal']))
                    story.append(Spacer(1, 6))
            
            story.append(PageBreak())
            
            # Research Statistics
            story.append(Paragraph("Research Statistics", styles['Heading1']))
            story.append(Spacer(1, 12))
            
            stats = [
                f"Total initial search results: {len(research_result.initial_results)}",
                f"Level 1 pages crawled: {len(research_result.level_1_content)}",
                f"Level 2 pages crawled: {len(research_result.level_2_content)}",
                f"Total pages crawled: {research_result.total_pages_crawled}",
                f"Total links discovered: {research_result.total_links_found}",
                f"Research time: {research_result.research_time:.1f} seconds"
            ]
            
            for stat in stats:
                story.append(Paragraph(stat, styles['Normal']))
                story.append(Spacer(1, 6))
            
            story.append(PageBreak())
            
            # Key Findings
            if research_result.key_findings:
                story.append(Paragraph("Key Findings", styles['Heading1']))
                story.append(Spacer(1, 12))
                
                for i, finding in enumerate(research_result.key_findings, 1):
                    story.append(Paragraph(f"{i}. {finding}", styles['Normal']))
                    story.append(Spacer(1, 8))
                
                story.append(PageBreak())
            
            # Detailed Sources
            story.append(Paragraph("Detailed Sources", styles['Heading1']))
            story.append(Spacer(1, 12))
            
            all_content = research_result.level_1_content + research_result.level_2_content
            relevant_content = [c for c in all_content if c.success and c.relevance_score > 0.1]
            relevant_content.sort(key=lambda x: x.relevance_score, reverse=True)
            
            for i, content in enumerate(relevant_content[:20], 1):  # Top 20 sources
                story.append(Paragraph(f"Source {i}: {content.title or 'Untitled'}", styles['Heading3']))
                story.append(Paragraph(f"URL: {content.url}", styles['Normal']))
                story.append(Paragraph(f"Relevance Score: {content.relevance_score:.2f}", styles['Normal']))
                
                # Add content excerpt
                excerpt = content.content[:500] + "..." if len(content.content) > 500 else content.content
                story.append(Paragraph("Excerpt:", styles['Heading4']))
                story.append(Paragraph(excerpt, styles['Normal']))
                story.append(Spacer(1, 12))
            
            # Build PDF
            doc.build(story)
            self.logger.info(f"PDF generated successfully: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error generating PDF: {e}")
            return False