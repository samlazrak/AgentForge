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
class DeepResearchResult:
    """Represents the complete deep research result"""
    source_pdf: str
    extracted_links: List[ExtractedLink] = field(default_factory=list)
    scraped_content: List[ScrapedContent] = field(default_factory=list)
    summary: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    total_links_found: int = 0
    successful_scrapes: int = 0

class DeepResearcherAgent(BaseAgent):
    """
    Agent specialized in deep research by extracting links from PDFs
    and scraping content from those links
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """
        Initialize the deep researcher agent
        
        Args:
            config: Agent configuration
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
                    "link_validation"
                ]
            )
        
        super().__init__(config)
        self.webscraper_agent = None
        
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
        
        if not pdf_path:
            raise ValueError("pdf_path parameter is required")
        
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        self.logger.info(f"Starting deep research on PDF: {pdf_path}")
        
        # Step 1: Extract links from PDF
        extracted_links = self._extract_links_from_pdf_file(pdf_path, max_links)
        
        # Step 2: Filter links by domain if specified
        if filter_domains:
            extracted_links = self._filter_links_by_domain(extracted_links, filter_domains)
        
        # Step 3: Scrape content from links
        scraped_content = self._scrape_content_from_links(extracted_links, include_images)
        
        # Step 4: Generate summary
        summary = self._generate_research_summary(extracted_links, scraped_content)
        
        result = DeepResearchResult(
            source_pdf=pdf_path,
            extracted_links=extracted_links,
            scraped_content=scraped_content,
            summary=summary,
            total_links_found=len(extracted_links),
            successful_scrapes=len([c for c in scraped_content if c.success])
        )
        
        self.logger.info(f"Deep research completed. Found {result.total_links_found} links, "
                        f"successfully scraped {result.successful_scrapes} sites")
        
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
                     include_images: bool = True) -> DeepResearchResult:
        """
        Convenience method to perform complete deep research
        
        Args:
            pdf_path: Path to PDF file
            max_links: Maximum number of links to extract
            filter_domains: Optional list of domains to filter by
            include_images: Whether to include images in scraping
            
        Returns:
            Complete deep research result
        """
        task_id = self.create_task("deep_research", {
            "type": "deep_research",
            "pdf_path": pdf_path,
            "max_links": max_links,
            "filter_domains": filter_domains or [],
            "include_images": include_images
        })
        return self.run_task(task_id)