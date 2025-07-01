"""
Deep Researcher Agent for extracting links from PDFs and scraping content
"""

import os
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
import logging
from urllib.parse import urlparse, urljoin
import time

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    logging.warning("pdfplumber not available")

from ..core.base_agent import BaseAgent, AgentConfig, AgentTask

@dataclass
class ExtractedLink:
    """Represents an extracted link from PDF"""
    url: str
    text: str = ""
    page_number: int = 0
    context: str = ""
    bbox: Optional[Tuple[float, float, float, float]] = None

@dataclass
class ScrapedContent:
    """Represents scraped and filtered content"""
    url: str
    title: str = ""
    clean_text: str = ""
    images: List[str] = field(default_factory=list)
    links: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    success: bool = False
    error: Optional[str] = None

@dataclass
class ScrapingConfig:
    """Configuration for multi-level scraping"""
    max_depth: int = 1
    max_links_per_level: int = 5
    max_total_links: int = 50
    delay_between_requests: float = 1.0
    respect_robots_txt: bool = True
    relevance_threshold: float = 0.3
    allowed_domains: List[str] = field(default_factory=list)
    blocked_domains: List[str] = field(default_factory=list)

@dataclass
class DeepResearchResult:
    """Represents the complete deep research result"""
    source_pdf: str
    extracted_links: List[ExtractedLink] = field(default_factory=list)
    scraped_content: List[ScrapedContent] = field(default_factory=list)
    link_network: Dict[str, List[str]] = field(default_factory=dict)  # Maps parent URL to child URLs
    scraping_stats: Dict[str, Any] = field(default_factory=dict)
    summary: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    total_links_found: int = 0
    successful_scrapes: int = 0
    max_depth_reached: int = 0

class DeepResearcherAgent(BaseAgent):
    """
    Agent specialized in deep research by extracting links from PDFs
    and scraping content from those links
    """
    
    def __init__(self, config: Optional[AgentConfig] = None, scraping_config: Optional[ScrapingConfig] = None):
        """
        Initialize the deep researcher agent
        
        Args:
            config: Agent configuration
            scraping_config: Multi-level scraping configuration
        """
        if config is None:
            config = AgentConfig(
                name="DeepResearcherAgent",
                description="Agent specialized in extracting links from PDFs and deep content scraping",
                capabilities=[
                    "pdf_link_extraction",
                    "content_scraping",
                    "content_filtering",
                    "deep_analysis",
                    "link_validation",
                    "multi_level_scraping",
                    "network_analysis"
                ]
            )
        
        super().__init__(config)
        self.webscraper_agent = None
        self.scraping_config = scraping_config or ScrapingConfig()
        self.scraped_urls = set()  # Track scraped URLs to avoid duplicates
        self.url_relevance_cache = {}  # Cache relevance scores
        
    def _initialize(self):
        """Initialize deep researcher specific components"""
        self.logger.info("Initializing Deep Researcher Agent")
        
        # Check available dependencies
        self.pdfplumber_available = PDFPLUMBER_AVAILABLE
        
        if not self.pdfplumber_available:
            self.logger.warning("pdfplumber not available - using mock functionality")
    
    def set_webscraper_agent(self, webscraper_agent):
        """
        Set the webscraper agent for content scraping
        
        Args:
            webscraper_agent: WebscraperAgent instance
        """
        self.webscraper_agent = webscraper_agent
        self.logger.info("Webscraper agent connected")
    
    def execute_task(self, task: AgentTask) -> Any:
        """
        Execute a deep research task
        
        Args:
            task: Task to execute
            
        Returns:
            Deep research result
        """
        task_type = task.parameters.get("type", "deep_research")
        
        if task_type == "deep_research":
            return self._perform_deep_research(task)
        elif task_type == "extract_links":
            return self._extract_links_from_pdf(task)
        elif task_type == "scrape_links":
            return self._scrape_links(task)
        elif task_type == "filter_content":
            return self._filter_content(task)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    def _perform_deep_research(self, task: AgentTask) -> DeepResearchResult:
        """
        Perform complete deep research process
        
        Args:
            task: Deep research task
            
        Returns:
            Complete research result
        """
        pdf_path = task.parameters.get("pdf_path", "")
        max_links = task.parameters.get("max_links", 10)
        filter_domains = task.parameters.get("filter_domains", [])
        include_images = task.parameters.get("include_images", True)
        max_depth = task.parameters.get("max_depth", self.scraping_config.max_depth)
        use_multi_level = task.parameters.get("use_multi_level", True)
        
        if not pdf_path:
            raise ValueError("pdf_path parameter is required")
        
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        self.logger.info(f"Starting deep research on PDF: {pdf_path}")
        self.logger.info(f"Multi-level scraping: {use_multi_level}, Max depth: {max_depth}")
        
        # Step 1: Extract links from PDF
        extracted_links = self._extract_links_from_pdf_file(pdf_path, max_links)
        
        # Step 2: Filter links by domain if specified
        if filter_domains:
            extracted_links = self._filter_links_by_domain(extracted_links, filter_domains)
        
        # Step 3: Scrape content from links (with optional multi-level)
        if use_multi_level and max_depth > 1:
            scraped_content, link_network, scraping_stats = self._perform_multi_level_scraping(
                extracted_links, max_depth
            )
        else:
            scraped_content = self._scrape_content_from_links(extracted_links, include_images)
            link_network = {}
            scraping_stats = {
                'total_urls_discovered': len(extracted_links),
                'total_urls_scraped': len([c for c in scraped_content if c.success]),
                'max_depth_reached': 1
            }
        
        # Step 4: Generate enhanced summary
        summary = self._generate_research_summary(extracted_links, scraped_content)
        
        result = DeepResearchResult(
            source_pdf=pdf_path,
            extracted_links=extracted_links,
            scraped_content=scraped_content,
            link_network=link_network,
            scraping_stats=scraping_stats,
            summary=summary,
            total_links_found=len(extracted_links),
            successful_scrapes=len([c for c in scraped_content if c.success]),
            max_depth_reached=scraping_stats.get('max_depth_reached', 1)
        )
        
        self.logger.info(f"Deep research completed. Found {result.total_links_found} initial links, "
                        f"scraped {result.successful_scrapes} total pages across {result.max_depth_reached} levels")
        
        return result
    
    def _extract_links_from_pdf_file(self, pdf_path: str, max_links: int = 10) -> List[ExtractedLink]:
        """
        Extract links from a PDF file
        
        Args:
            pdf_path: Path to PDF file
            max_links: Maximum number of links to extract
            
        Returns:
            List of extracted links
        """
        if not self.pdfplumber_available:
            return self._mock_extract_links(pdf_path, max_links)
        
        extracted_links = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Extract hyperlinks from annotations
                    if hasattr(page, 'hyperlinks') and page.hyperlinks:
                        for hyperlink in page.hyperlinks:
                            if len(extracted_links) >= max_links:
                                break
                            
                            url = hyperlink.get('uri', '')
                            if url and self._is_valid_url(url):
                                # Extract surrounding text for context
                                bbox = hyperlink.get('bbox')
                                context = self._extract_context_around_link(page, bbox) if bbox else ""
                                
                                link = ExtractedLink(
                                    url=url,
                                    text=hyperlink.get('text', ''),
                                    page_number=page_num + 1,
                                    context=context,
                                    bbox=bbox
                                )
                                extracted_links.append(link)
                    
                    # Also look for URLs in the text content
                    page_text = page.extract_text() or ""
                    text_urls = self._extract_urls_from_text(page_text)
                    
                    for url in text_urls:
                        if len(extracted_links) >= max_links:
                            break
                        
                        if url not in [link.url for link in extracted_links]:
                            link = ExtractedLink(
                                url=url,
                                text="",
                                page_number=page_num + 1,
                                context=self._extract_context_from_text(page_text, url)
                            )
                            extracted_links.append(link)
                    
                    if len(extracted_links) >= max_links:
                        break
        
        except Exception as e:
            self.logger.error(f"Error extracting links from PDF: {e}")
            return self._mock_extract_links(pdf_path, max_links)
        
        return extracted_links[:max_links]
    
    def _extract_urls_from_text(self, text: str) -> List[str]:
        """
        Extract URLs from text content using regex
        
        Args:
            text: Text content
            
        Returns:
            List of extracted URLs
        """
        url_pattern = r'https?://[^\s<>"\'()]+|www\.[^\s<>"\'()]+'
        urls = re.findall(url_pattern, text, re.IGNORECASE)
        
        # Clean and validate URLs
        cleaned_urls = []
        for url in urls:
            url = url.rstrip('.,;!?)')  # Remove trailing punctuation
            if not url.startswith('http'):
                url = 'http://' + url
            
            if self._is_valid_url(url):
                cleaned_urls.append(url)
        
        return cleaned_urls
    
    def _is_valid_url(self, url: str) -> bool:
        """
        Validate if a string is a valid URL
        
        Args:
            url: URL string to validate
            
        Returns:
            True if valid URL, False otherwise
        """
        try:
            result = urlparse(url)
            # Only allow HTTP and HTTPS schemes
            return all([result.scheme in ['http', 'https'], result.netloc])
        except Exception:
            return False
    
    def _extract_context_around_link(self, page, bbox: Tuple[float, float, float, float]) -> str:
        """
        Extract text context around a link based on its bounding box
        
        Args:
            page: pdfplumber page object
            bbox: Bounding box of the link
            
        Returns:
            Context text around the link
        """
        try:
            # Expand the bounding box to capture surrounding text
            x1, y1, x2, y2 = bbox
            expanded_bbox = (
                max(0, x1 - 50),  # Expand left
                max(0, y1 - 20),  # Expand up
                x2 + 50,          # Expand right
                y2 + 20           # Expand down
            )
            
            # Crop the page to the expanded area and extract text
            cropped = page.crop(expanded_bbox)
            context = cropped.extract_text() or ""
            
            # Clean and limit context length
            context = ' '.join(context.split())  # Normalize whitespace
            return context[:200] + "..." if len(context) > 200 else context
            
        except Exception as e:
            self.logger.warning(f"Error extracting context: {e}")
            return ""
    
    def _extract_context_from_text(self, text: str, url: str) -> str:
        """
        Extract context around a URL found in text
        
        Args:
            text: Full text content
            url: URL to find context for
            
        Returns:
            Context text around the URL
        """
        try:
            url_index = text.find(url)
            if url_index == -1:
                return ""
            
            # Extract context before and after the URL
            start = max(0, url_index - 100)
            end = min(len(text), url_index + len(url) + 100)
            context = text[start:end]
            
            # Clean and normalize
            context = ' '.join(context.split())
            return context
            
        except Exception as e:
            self.logger.warning(f"Error extracting text context: {e}")
            return ""
    
    def _filter_links_by_domain(self, links: List[ExtractedLink], allowed_domains: List[str]) -> List[ExtractedLink]:
        """
        Filter links by allowed domains
        
        Args:
            links: List of extracted links
            allowed_domains: List of allowed domain patterns
            
        Returns:
            Filtered list of links
        """
        if not allowed_domains:
            return links
        
        filtered_links = []
        for link in links:
            try:
                domain = urlparse(link.url).netloc.lower()
                if any(allowed_domain.lower() in domain for allowed_domain in allowed_domains):
                    filtered_links.append(link)
            except Exception as e:
                self.logger.warning(f"Error filtering link {link.url}: {e}")
                continue
        
        return filtered_links
    
    def _scrape_content_from_links(self, links: List[ExtractedLink], include_images: bool = True) -> List[ScrapedContent]:
        """
        Scrape content from extracted links
        
        Args:
            links: List of extracted links
            include_images: Whether to include images in scraping
            
        Returns:
            List of scraped content
        """
        if not self.webscraper_agent:
            self.logger.warning("No webscraper agent available, using mock scraping")
            return self._mock_scrape_content(links)
        
        scraped_content = []
        
        for link in links:
            try:
                self.logger.info(f"Scraping content from: {link.url}")
                
                # Use webscraper agent to get content
                scraping_result = self.webscraper_agent.scrape_url(link.url)
                
                if scraping_result.success:
                    # Filter and clean the scraped content
                    clean_text = self._filter_and_clean_content(scraping_result.text)
                    
                    content = ScrapedContent(
                        url=link.url,
                        title=scraping_result.title,
                        clean_text=clean_text,
                        images=scraping_result.images if include_images else [],
                        links=scraping_result.links,
                        metadata=scraping_result.metadata,
                        success=True
                    )
                else:
                    content = ScrapedContent(
                        url=link.url,
                        success=False,
                        error=scraping_result.error
                    )
                
                scraped_content.append(content)
                
            except Exception as e:
                self.logger.error(f"Error scraping {link.url}: {e}")
                content = ScrapedContent(
                    url=link.url,
                    success=False,
                    error=str(e)
                )
                scraped_content.append(content)
        
        return scraped_content
    
    def _filter_and_clean_content(self, text: str) -> str:
        """
        Filter out unwanted content and clean the text
        
        Args:
            text: Raw scraped text
            
        Returns:
            Cleaned and filtered text
        """
        if not text:
            return ""
        
        # Common patterns to remove - target specific phrases 
        patterns_to_remove = [
            r'(?i)\bnewsletter signup?\b',
            r'(?i)\bcookie policy\b',
            r'(?i)\bprivacy policy\b', 
            r'(?i)\bterms of service\b',
            r'(?i)\baccept cookies?\b',
            r'(?i)\bsubscribe to newsletter\b',
            r'(?i)\bfollow us on\b',
            r'(?i)\bsocial media\b',
            r'(?i)\badvertisement\b',
            r'(?i)\bsign up\b',
            r'(?i)\blog in\b',
            r'(?i)\bcontact us\b',
            r'(?i)\babout us\b',
            r'(?i)\bcopyright ©?\b.*$',
            r'(?i)\ball rights reserved\b',
        ]
        
        # Remove unwanted patterns
        cleaned_text = text
        for pattern in patterns_to_remove:
            cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.MULTILINE)
        
        # Remove excessive whitespace and empty lines
        cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text)
        cleaned_text = re.sub(r' +', ' ', cleaned_text)
        cleaned_text = cleaned_text.strip()
        
        # Remove very short lines that are likely navigation elements
        lines = cleaned_text.split('\n')
        filtered_lines = []
        for line in lines:
            line = line.strip()
            if len(line) > 10 or len(line.split()) > 2:  # Keep longer lines or lines with multiple words
                filtered_lines.append(line)
        
        cleaned_text = '\n'.join(filtered_lines)
        
        # Limit text length to avoid overly long content
        if len(cleaned_text) > 5000:
            cleaned_text = cleaned_text[:5000] + "...\n[Content truncated]"
        
        return cleaned_text
    
    def _perform_multi_level_scraping(self, initial_links: List[ExtractedLink], 
                                     max_depth: int = None) -> Tuple[List[ScrapedContent], Dict[str, List[str]], Dict[str, Any]]:
        """
        Perform multi-level recursive scraping
        
        Args:
            initial_links: Starting links from PDF
            max_depth: Maximum depth to scrape (overrides config)
            
        Returns:
            Tuple of (all_scraped_content, link_network, stats)
        """
        max_depth = max_depth or self.scraping_config.max_depth
        link_network = {}
        all_scraped_content = []
        current_depth = 0
        urls_to_scrape = [(link.url, 0) for link in initial_links]  # (url, depth)
        
        stats = {
            'total_urls_discovered': 0,
            'total_urls_scraped': 0,
            'urls_per_depth': {},
            'failed_scrapes': 0,
            'duplicate_urls_skipped': 0,
            'relevance_filtered': 0
        }
        
        while urls_to_scrape and current_depth <= max_depth:
            current_level_urls = [(url, depth) for url, depth in urls_to_scrape if depth == current_depth]
            if not current_level_urls:
                current_depth += 1
                continue
                
            stats['urls_per_depth'][current_depth] = len(current_level_urls)
            self.logger.info(f"Scraping depth {current_depth}: {len(current_level_urls)} URLs")
            
            for url, depth in current_level_urls:
                if url in self.scraped_urls:
                    stats['duplicate_urls_skipped'] += 1
                    continue
                    
                if len(all_scraped_content) >= self.scraping_config.max_total_links:
                    self.logger.info("Reached maximum total links limit")
                    break
                    
                # Check relevance
                if not self._is_url_relevant(url, initial_links):
                    stats['relevance_filtered'] += 1
                    continue
                
                # Scrape the URL
                scraped_result = self._scrape_single_url_with_links(url)
                if scraped_result:
                    all_scraped_content.append(scraped_result)
                    self.scraped_urls.add(url)
                    stats['total_urls_scraped'] += 1
                    
                    # Extract links for next level
                    if depth < max_depth and scraped_result.success:
                        child_links = self._extract_relevant_child_links(scraped_result, url)
                        if child_links:
                            link_network[url] = child_links
                            # Add to queue for next depth
                            for child_url in child_links[:self.scraping_config.max_links_per_level]:
                                if child_url not in self.scraped_urls:
                                    urls_to_scrape.append((child_url, depth + 1))
                                    stats['total_urls_discovered'] += 1
                else:
                    stats['failed_scrapes'] += 1
                
                # Respect rate limiting
                time.sleep(self.scraping_config.delay_between_requests)
            
            current_depth += 1
        
        stats['max_depth_reached'] = current_depth - 1
        return all_scraped_content, link_network, stats
    
    def _scrape_single_url_with_links(self, url: str) -> Optional[ScrapedContent]:
        """
        Scrape a single URL and extract its links
        
        Args:
            url: URL to scrape
            
        Returns:
            ScrapedContent with extracted links
        """
        if not self.webscraper_agent:
            self.logger.warning("No webscraper agent available")
            return None
            
        try:
            self.logger.info(f"Scraping: {url}")
            scraping_result = self.webscraper_agent.scrape_url(url)
            
            if scraping_result.success:
                clean_text = self._filter_and_clean_content(scraping_result.text)
                
                return ScrapedContent(
                    url=url,
                    title=scraping_result.title,
                    clean_text=clean_text,
                    images=scraping_result.images,
                    links=scraping_result.links or [],
                    metadata=scraping_result.metadata,
                    success=True
                )
            else:
                return ScrapedContent(
                    url=url,
                    success=False,
                    error=scraping_result.error
                )
                
        except Exception as e:
            self.logger.error(f"Error scraping {url}: {e}")
            return ScrapedContent(
                url=url,
                success=False,
                error=str(e)
            )
    
    def _extract_relevant_child_links(self, scraped_content: ScrapedContent, parent_url: str) -> List[str]:
        """
        Extract relevant child links from scraped content
        
        Args:
            scraped_content: Content that was scraped
            parent_url: URL that was scraped
            
        Returns:
            List of relevant child URLs
        """
        if not scraped_content.links:
            return []
        
        relevant_links = []
        parent_domain = urlparse(parent_url).netloc
        
        for link in scraped_content.links:
            try:
                parsed_link = urlparse(link)
                
                # Skip non-HTTP links
                if parsed_link.scheme not in ['http', 'https']:
                    continue
                
                # Apply domain filtering
                link_domain = parsed_link.netloc
                
                # Skip if in blocked domains
                if any(blocked in link_domain for blocked in self.scraping_config.blocked_domains):
                    continue
                
                # If allowed domains specified, only include those
                if self.scraping_config.allowed_domains:
                    if not any(allowed in link_domain for allowed in self.scraping_config.allowed_domains):
                        continue
                
                # Prefer same domain links for relevance
                if link_domain == parent_domain:
                    relevant_links.append(link)
                elif len(relevant_links) < self.scraping_config.max_links_per_level // 2:
                    # Allow some cross-domain links
                    relevant_links.append(link)
                
                if len(relevant_links) >= self.scraping_config.max_links_per_level:
                    break
                    
            except Exception as e:
                self.logger.warning(f"Error processing link {link}: {e}")
                continue
        
        return relevant_links
    
    def _is_url_relevant(self, url: str, initial_links: List[ExtractedLink]) -> bool:
        """
        Check if a URL is relevant to the research topic
        
        Args:
            url: URL to check
            initial_links: Original links from PDF for context
            
        Returns:
            True if URL appears relevant
        """
        if url in self.url_relevance_cache:
            return self.url_relevance_cache[url]
        
        # Simple relevance heuristics
        url_lower = url.lower()
        
        # Check if URL contains relevant keywords
        relevant_keywords = [
            'ai', 'artificial-intelligence', 'machine-learning', 'software-development',
            'programming', 'coding', 'developer', 'engineer', 'technology', 'tech',
            'automation', 'agent', 'chatgpt', 'llm', 'generative', 'neural', 'algorithm'
        ]
        
        keyword_score = sum(1 for keyword in relevant_keywords if keyword in url_lower)
        
        # Check domain similarity to initial links
        url_domain = urlparse(url).netloc
        initial_domains = {urlparse(link.url).netloc for link in initial_links}
        domain_similarity = 1.0 if url_domain in initial_domains else 0.0
        
        # Calculate relevance score
        relevance_score = (keyword_score * 0.3) + (domain_similarity * 0.7)
        
        is_relevant = relevance_score >= self.scraping_config.relevance_threshold
        self.url_relevance_cache[url] = is_relevant
        
        return is_relevant
    
    def _generate_research_summary(self, links: List[ExtractedLink], content: List[ScrapedContent]) -> str:
        """
        Generate a summary of the research results
        
        Args:
            links: List of extracted links
            content: List of scraped content
            
        Returns:
            Research summary
        """
        successful_content = [c for c in content if c.success]
        
        if not successful_content:
            return "No content was successfully scraped from the extracted links."
        
        # Prepare context for LLM summary
        context = "Research Summary:\n\n"
        context += f"Total links extracted: {len(links)}\n"
        context += f"Successfully scraped: {len(successful_content)}\n\n"
        
        context += "Successfully scraped content:\n"
        for i, content_item in enumerate(successful_content[:5], 1):  # Limit to top 5
            context += f"{i}. {content_item.title or 'Untitled'}\n"
            context += f"   URL: {content_item.url}\n"
            context += f"   Preview: {content_item.clean_text[:200]}...\n\n"
        
        # Use LLM to generate comprehensive summary
        prompt = f"""
        {context}
        
        Based on the above information, provide a comprehensive summary of the deep research results.
        
        The summary should:
        1. Overview of the research scope and success rate
        2. Key themes and topics found across the scraped content
        3. Notable insights or patterns
        4. Quality assessment of the extracted content
        
        Summary:
        """
        
        try:
            summary = self.llm.generate_response(prompt, max_tokens=500)
            return summary
        except Exception as e:
            self.logger.warning(f"Failed to generate LLM summary: {e}")
            return f"Research completed with {len(successful_content)} successful content extractions from {len(links)} total links."
    
    def _mock_extract_links(self, pdf_path: str, max_links: int) -> List[ExtractedLink]:
        """Generate mock links for testing when pdfplumber is unavailable"""
        mock_links = []
        for i in range(min(max_links, 3)):
            link = ExtractedLink(
                url=f"https://example-{i+1}.com/article",
                text=f"Example Link {i+1}",
                page_number=1,
                context=f"This is mock context for link {i+1} extracted from the PDF."
            )
            mock_links.append(link)
        return mock_links
    
    def _mock_scrape_content(self, links: List[ExtractedLink]) -> List[ScrapedContent]:
        """Generate mock scraped content for testing"""
        mock_content = []
        for link in links:
            content = ScrapedContent(
                url=link.url,
                title=f"Mock Title for {link.url}",
                clean_text=f"This is mock cleaned content from {link.url}. It contains relevant information about the topic discussed.",
                images=[f"{link.url}/image1.jpg"],
                links=[f"{link.url}/related-link"],
                metadata={"mock": True, "source": link.url},
                success=True
            )
            mock_content.append(content)
        return mock_content
    
    def _extract_links_from_pdf(self, task: AgentTask) -> List[ExtractedLink]:
        """Task handler for link extraction only"""
        pdf_path = task.parameters.get("pdf_path", "")
        max_links = task.parameters.get("max_links", 10)
        
        if not pdf_path:
            raise ValueError("pdf_path parameter is required")
        
        return self._extract_links_from_pdf_file(pdf_path, max_links)
    
    def _scrape_links(self, task: AgentTask) -> List[ScrapedContent]:
        """Task handler for scraping links only"""
        links = task.parameters.get("links", [])
        include_images = task.parameters.get("include_images", True)
        
        if not links:
            raise ValueError("links parameter is required")
        
        # Convert dict links to ExtractedLink objects if needed
        if links and isinstance(links[0], dict):
            link_objects = []
            for link_data in links:
                link = ExtractedLink(
                    url=link_data.get("url", ""),
                    text=link_data.get("text", ""),
                    page_number=link_data.get("page_number", 0),
                    context=link_data.get("context", "")
                )
                link_objects.append(link)
            links = link_objects
        
        return self._scrape_content_from_links(links, include_images)
    
    def _filter_content(self, task: AgentTask) -> str:
        """Task handler for content filtering only"""
        text = task.parameters.get("text", "")
        
        if not text:
            raise ValueError("text parameter is required")
        
        return self._filter_and_clean_content(text)
    
    # Convenience methods for direct use
    def extract_links_from_pdf(self, pdf_path: str, max_links: int = 10) -> List[ExtractedLink]:
        """
        Convenience method to extract links from PDF
        
        Args:
            pdf_path: Path to PDF file
            max_links: Maximum number of links to extract
            
        Returns:
            List of extracted links
        """
        task_id = self.create_task("extract_links", {
            "type": "extract_links",
            "pdf_path": pdf_path,
            "max_links": max_links
        })
        return self.run_task(task_id)
    
    def deep_research(self, pdf_path: str, max_links: int = 10, filter_domains: List[str] = None, 
                     include_images: bool = True, max_depth: int = 1, use_multi_level: bool = False) -> DeepResearchResult:
        """
        Convenience method to perform complete deep research
        
        Args:
            pdf_path: Path to PDF file
            max_links: Maximum number of links to extract from PDF
            filter_domains: Optional list of domains to filter by
            include_images: Whether to include images in scraping
            max_depth: Maximum depth for multi-level scraping (1 = single level)
            use_multi_level: Whether to enable multi-level recursive scraping
            
        Returns:
            Complete deep research result
        """
        task_id = self.create_task("deep_research", {
            "type": "deep_research",
            "pdf_path": pdf_path,
            "max_links": max_links,
            "filter_domains": filter_domains or [],
            "include_images": include_images,
            "max_depth": max_depth,
            "use_multi_level": use_multi_level
        })
        return self.run_task(task_id)