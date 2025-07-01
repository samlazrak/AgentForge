import asyncio
import logging
import os
import re
import time
from datetime import datetime
from typing import List, Dict, Any, Set, Optional
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass, field
import json

try:
    import requests
    from requests.adapters import HTTPAdapter
    try:
        from urllib3.util.retry import Retry
    except ImportError:
        from requests.packages.urllib3.util.retry import Retry
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logging.error("requests library required but not available")

try:
    from bs4 import BeautifulSoup
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False
    logging.error("beautifulsoup4 library required but not available")

try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False
    logging.error("duckduckgo-search library required but not available")

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logging.error("reportlab library required but not available")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@dataclass
class SearchResult:
    """Represents a search result from DuckDuckGo"""
    title: str
    url: str
    snippet: str
    rank: int

@dataclass
class ScrapedContent:
    """Represents scraped content from a webpage"""
    url: str
    title: str = ""
    content: str = ""
    links: List[str] = field(default_factory=list)
    relevance_score: float = 0.0
    success: bool = False
    error: Optional[str] = None
    scraped_at: datetime = field(default_factory=datetime.now)

@dataclass
class ResearchResult:
    """Final research result with all findings"""
    query: str
    initial_results: List[SearchResult] = field(default_factory=list)
    level_1_content: List[ScrapedContent] = field(default_factory=list)
    level_2_content: List[ScrapedContent] = field(default_factory=list)
    summary: str = ""
    key_findings: List[str] = field(default_factory=list)
    total_pages_crawled: int = 0
    total_links_found: int = 0
    research_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

class WebCrawler:
    """Robust web crawler for deep research"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = None
        self.crawled_urls: Set[str] = set()
        
        if REQUESTS_AVAILABLE:
            self._setup_session()
    
    def _setup_session(self):
        """Setup requests session with retries and proper headers"""
        self.session = requests.Session()
        
        # Setup retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def search_duckduckgo(self, query: str, max_results: int = 20) -> List[SearchResult]:
        """Search DuckDuckGo for initial results"""
        if not DDGS_AVAILABLE:
            self.logger.error("DuckDuckGo search not available")
            return []
        
        results = []
        try:
            self.logger.info(f"Searching DuckDuckGo for: {query}")
            
            with DDGS() as ddgs:
                search_results = ddgs.text(query, max_results=max_results)
                
                for i, result in enumerate(search_results):
                    search_result = SearchResult(
                        title=result.get('title', ''),
                        url=result.get('href', ''),
                        snippet=result.get('body', ''),
                        rank=i + 1
                    )
                    results.append(search_result)
                    
            self.logger.info(f"Found {len(results)} search results")
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching DuckDuckGo: {e}")
            return []

    def scrape_url(self, url: str, timeout: int = 10) -> ScrapedContent:
        """Scrape content from a single URL"""
        if not REQUESTS_AVAILABLE or not BEAUTIFULSOUP_AVAILABLE:
            return ScrapedContent(url=url, error="Required libraries not available")
        
        if url in self.crawled_urls:
            return ScrapedContent(url=url, error="Already crawled")
        
        self.crawled_urls.add(url)
        
        try:
            self.logger.info(f"Scraping: {url}")
            
            if not self.session:
                return ScrapedContent(url=url, error="Session not available")
            
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract title
            title = ""
            if soup.title and soup.title.string:
                title = soup.title.string.strip()
            
            # Extract main content
            content = soup.get_text()
            lines = (line.strip() for line in content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            content = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Extract links
            links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                absolute_url = urljoin(url, href)
                
                # Filter out non-HTTP links and common non-content links
                if (absolute_url.startswith(('http://', 'https://')) and 
                    not any(skip in absolute_url.lower() for skip in [
                        'javascript:', 'mailto:', '#', '.pdf', '.doc', '.jpg', 
                        '.png', '.gif', 'facebook.com', 'twitter.com', 'linkedin.com'
                    ])):
                    links.append(absolute_url)
            
            # Remove duplicates
            links = list(set(links))
            
            return ScrapedContent(
                url=url,
                title=title,
                content=content,
                links=links,
                success=True
            )
            
        except requests.RequestException as e:
            self.logger.warning(f"Request error for {url}: {e}")
            return ScrapedContent(url=url, error=f"Request error: {str(e)}")
        except Exception as e:
            self.logger.warning(f"Error scraping {url}: {e}")
            return ScrapedContent(url=url, error=f"Scraping error: {str(e)}")

    def scrape_multiple_urls(self, urls: List[str], delay: float = 1.0) -> List[ScrapedContent]:
        """Scrape multiple URLs with delay between requests"""
        results = []
        
        for i, url in enumerate(urls):
            result = self.scrape_url(url)
            results.append(result)
            
            # Add delay between requests to be respectful
            if i < len(urls) - 1:
                time.sleep(delay)
        
        return results

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

class DeepResearcher:
    """Main deep research orchestrator"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.crawler = WebCrawler()
        self.analyzer = ContentAnalyzer()
        self.report_generator = ReportGenerator()
        self.pdf_generator = PDFGenerator()
    
    def research(self, query: str, max_initial_results: int = 20, 
                max_level2_per_page: int = 10) -> ResearchResult:
        """Perform comprehensive deep research"""
        start_time = time.time()
        self.logger.info(f"Starting deep research for: {query}")
        
        # Initialize result
        result = ResearchResult(query=query)
        
        try:
            # Step 1: Search DuckDuckGo for initial results
            self.logger.info("Step 1: Searching DuckDuckGo...")
            result.initial_results = self.crawler.search_duckduckgo(query, max_initial_results)
            
            if not result.initial_results:
                self.logger.error("No initial search results found")
                return result
            
            # Step 2: Crawl level 1 pages (initial search results)
            self.logger.info("Step 2: Crawling level 1 pages...")
            level1_urls = [r.url for r in result.initial_results]
            result.level_1_content = self.crawler.scrape_multiple_urls(level1_urls)
            
            # Filter for relevant content
            result.level_1_content = self.analyzer.filter_relevant_content(
                result.level_1_content, query
            )
            
            # Step 3: Extract all links from level 1 pages
            self.logger.info("Step 3: Extracting links from level 1 pages...")
            all_level2_links = []
            for content in result.level_1_content:
                if content.success and content.links:
                    # Limit links per page
                    page_links = content.links[:max_level2_per_page]
                    all_level2_links.extend(page_links)
            
            # Remove duplicates and limit total
            all_level2_links = list(set(all_level2_links))
            if len(all_level2_links) > 100:  # Reasonable limit
                all_level2_links = all_level2_links[:100]
            
            result.total_links_found = len(all_level2_links)
            
            # Step 4: Crawl level 2 pages (links from level 1)
            if all_level2_links:
                self.logger.info(f"Step 4: Crawling {len(all_level2_links)} level 2 pages...")
                result.level_2_content = self.crawler.scrape_multiple_urls(all_level2_links)
                
                # Filter for relevant content
                result.level_2_content = self.analyzer.filter_relevant_content(
                    result.level_2_content, query
                )
            
            # Step 5: Generate summary and key findings
            self.logger.info("Step 5: Generating summary and findings...")
            result.summary = self.report_generator.generate_summary(result)
            result.key_findings = self.report_generator.extract_key_findings(result)
            
            # Calculate final statistics
            result.total_pages_crawled = len([c for c in result.level_1_content + result.level_2_content if c.success])
            result.research_time = time.time() - start_time
            
            self.logger.info(f"Research completed in {result.research_time:.1f} seconds")
            self.logger.info(f"Total pages crawled: {result.total_pages_crawled}")
            self.logger.info(f"Relevant sources found: {len([c for c in result.level_1_content + result.level_2_content if c.relevance_score > 0.1])}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error during research: {e}")
            result.research_time = time.time() - start_time
            return result
    
    def research_and_generate_pdf(self, query: str, output_dir: str = "research_output") -> tuple[ResearchResult, str]:
        """Perform research and generate PDF report"""
        # Perform research
        result = self.research(query)
        
        # Generate PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_query = re.sub(r'[^a-zA-Z0-9\s]', '', query)[:50]
        safe_query = re.sub(r'\s+', '_', safe_query)
        
        pdf_filename = f"deep_research_{safe_query}_{timestamp}.pdf"
        pdf_path = os.path.join(output_dir, pdf_filename)
        
        success = self.pdf_generator.generate_pdf(result, pdf_path)
        
        if success:
            self.logger.info(f"Research completed and PDF saved: {pdf_path}")
        else:
            self.logger.error("PDF generation failed")
            pdf_path = ""
        
        return result, pdf_path

# Example usage
if __name__ == "__main__":
    researcher = DeepResearcher()
    
    # Test with the user's query
    query = "I want to transition out of software engineering for companies and I want to start a phd. I have a lower gpa. How do I still get into a phd program?"
    
    result, pdf_path = researcher.research_and_generate_pdf(query)
    
    print(f"Research completed!")
    print(f"Pages crawled: {result.total_pages_crawled}")
    print(f"Research time: {result.research_time:.1f} seconds")
    print(f"PDF saved to: {pdf_path}")