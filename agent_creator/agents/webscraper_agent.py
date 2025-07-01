"""
Webscraper Agent for extracting content from web pages
"""

import asyncio
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
import logging
import re
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logging.warning("Requests and BeautifulSoup not available")

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logging.warning("Selenium not available")

try:
    from fake_useragent import UserAgent
    FAKE_USERAGENT_AVAILABLE = True
except ImportError:
    FAKE_USERAGENT_AVAILABLE = False
    logging.warning("Fake UserAgent not available")

from ..core.base_agent import BaseAgent, AgentConfig, AgentTask

@dataclass
class ScrapingResult:
    """Represents a scraping result"""
    url: str
    success: bool = False
    title: str = ""
    text: str = ""
    html: str = ""
    links: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    response_time: float = 0.0

@dataclass
class ScrapingConfig:
    """Configuration for web scraping"""
    timeout: int = 30
    max_retries: int = 3
    delay_between_requests: float = 1.0
    use_selenium: bool = False
    headless: bool = True
    user_agent: Optional[str] = None
    follow_redirects: bool = True
    extract_links: bool = True
    extract_images: bool = True
    max_content_length: int = 1000000  # 1MB

class WebscraperAgent(BaseAgent):
    """
    Agent specialized in web scraping and content extraction
    """
    
    def __init__(self, config: Optional[AgentConfig] = None, scraping_config: Optional[ScrapingConfig] = None):
        """
        Initialize the webscraper agent
        
        Args:
            config: Agent configuration
            scraping_config: Scraping-specific configuration
        """
        if config is None:
            config = AgentConfig(
                name="WebscraperAgent",
                description="Agent specialized in web scraping and content extraction",
                capabilities=[
                    "url_scraping",
                    "content_extraction",
                    "link_extraction", 
                    "image_extraction",
                    "metadata_extraction",
                    "batch_scraping"
                ]
            )
        
        self.scraping_config = scraping_config or ScrapingConfig()
        self.driver = None
        super().__init__(config)
        
    def _initialize(self):
        """Initialize scraping-specific components"""
        self.logger.info("Initializing Webscraper Agent")
        
        # Check available dependencies
        self.requests_available = REQUESTS_AVAILABLE
        self.selenium_available = SELENIUM_AVAILABLE
        self.fake_useragent_available = FAKE_USERAGENT_AVAILABLE
        
        if not self.requests_available:
            self.logger.warning("Requests not available - limited functionality")
        if not self.selenium_available:
            self.logger.warning("Selenium not available - no dynamic content support")
        
        # Initialize user agent
        if self.fake_useragent_available and not self.scraping_config.user_agent:
            try:
                ua = UserAgent()
                self.scraping_config.user_agent = ua.random
                self.logger.info(f"Using random user agent: {self.scraping_config.user_agent}")
            except Exception as e:
                self.logger.warning(f"Failed to generate random user agent: {e}")
                self.scraping_config.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        elif not self.scraping_config.user_agent:
            self.scraping_config.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    def execute_task(self, task: AgentTask) -> Any:
        """
        Execute a scraping task
        
        Args:
            task: Task to execute
            
        Returns:
            Scraping result
        """
        task_type = task.parameters.get("type", "scrape_url")
        
        if task_type == "scrape_url":
            return self._scrape_single_url(task)
        elif task_type == "scrape_multiple":
            return self._scrape_multiple_urls(task)
        elif task_type == "extract_links":
            return self._extract_links_from_page(task)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    def _scrape_single_url(self, task: AgentTask) -> ScrapingResult:
        """
        Scrape a single URL
        
        Args:
            task: Scraping task
            
        Returns:
            Scraping result
        """
        url = task.parameters.get("url", "")
        use_selenium = task.parameters.get("use_selenium", self.scraping_config.use_selenium)
        
        if not url:
            raise ValueError("URL parameter is required for scraping tasks")
        
        self.logger.info(f"Starting to scrape: {url}")
        start_time = time.time()
        
        try:
            if use_selenium and self.selenium_available:
                result = self._scrape_with_selenium(url)
            else:
                result = self._scrape_with_requests(url)
            
            result.response_time = time.time() - start_time
            self.logger.info(f"Scraping completed for: {url} in {result.response_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Scraping failed for {url}: {e}")
            return ScrapingResult(
                url=url,
                success=False,
                error=str(e),
                response_time=time.time() - start_time
            )
    
    def _scrape_with_requests(self, url: str) -> ScrapingResult:
        """
        Scrape URL using requests and BeautifulSoup
        
        Args:
            url: URL to scrape
            
        Returns:
            Scraping result
        """
        if not self.requests_available:
            return self._mock_scraping_result(url)
        
        result = ScrapingResult(url=url)
        
        try:
            headers = {"User-Agent": self.scraping_config.user_agent}
            
            response = requests.get(
                url,
                headers=headers,
                timeout=self.scraping_config.timeout,
                allow_redirects=self.scraping_config.follow_redirects
            )
            response.raise_for_status()
            
            # Check content length
            if len(response.content) > self.scraping_config.max_content_length:
                self.logger.warning(f"Content length exceeds limit: {len(response.content)}")
                content = response.content[:self.scraping_config.max_content_length]
            else:
                content = response.content
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract basic information
            result.success = True
            result.html = str(soup)
            result.title = soup.title.string.strip() if soup.title and soup.title.string else ""
            
            # Extract text content
            result.text = self._extract_text_content(soup)
            
            # Extract links if requested
            if self.scraping_config.extract_links:
                result.links = self._extract_links(soup, url)
            
            # Extract images if requested
            if self.scraping_config.extract_images:
                result.images = self._extract_images(soup, url)
            
            # Extract metadata
            result.metadata = self._extract_metadata(soup, response)
            
        except Exception as e:
            result.error = str(e)
            self.logger.error(f"Requests scraping failed: {e}")
        
        return result
    
    def _scrape_with_selenium(self, url: str) -> ScrapingResult:
        """
        Scrape URL using Selenium WebDriver
        
        Args:
            url: URL to scrape
            
        Returns:
            Scraping result  
        """
        if not self.selenium_available:
            self.logger.warning("Selenium not available, falling back to requests")
            return self._scrape_with_requests(url)
        
        result = ScrapingResult(url=url)
        driver = None
        
        try:
            # Setup Chrome options
            options = Options()
            if self.scraping_config.headless:
                options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument(f"--user-agent={self.scraping_config.user_agent}")
            
            driver = webdriver.Chrome(options=options)
            driver.set_page_load_timeout(self.scraping_config.timeout)
            
            # Navigate to URL
            driver.get(url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Extract information
            result.success = True
            result.html = driver.page_source
            result.title = driver.title
            
            # Parse with BeautifulSoup for text extraction
            soup = BeautifulSoup(result.html, 'html.parser')
            result.text = self._extract_text_content(soup)
            
            # Extract links if requested
            if self.scraping_config.extract_links:
                result.links = self._extract_links(soup, url)
            
            # Extract images if requested  
            if self.scraping_config.extract_images:
                result.images = self._extract_images(soup, url)
            
            # Extract metadata
            result.metadata = self._extract_selenium_metadata(driver, soup)
            
        except TimeoutException:
            result.error = "Page load timeout"
        except WebDriverException as e:
            result.error = f"WebDriver error: {str(e)}"
        except Exception as e:
            result.error = str(e)
        finally:
            if driver:
                driver.quit()
        
        return result
    
    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """
        Extract clean text content from HTML
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Clean text content
        """
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """
        Extract all links from the page
        
        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative links
            
        Returns:
            List of absolute URLs
        """
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            if absolute_url not in links:
                links.append(absolute_url)
        return links
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """
        Extract all image URLs from the page
        
        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative URLs
            
        Returns:
            List of absolute image URLs
        """
        images = []
        for img in soup.find_all('img', src=True):
            src = img['src']
            absolute_url = urljoin(base_url, src)
            if absolute_url not in images:
                images.append(absolute_url)
        return images
    
    def _extract_metadata(self, soup: BeautifulSoup, response=None) -> Dict[str, Any]:
        """
        Extract metadata from the page
        
        Args:
            soup: BeautifulSoup object
            response: HTTP response object (optional)
            
        Returns:
            Dictionary of metadata
        """
        metadata = {}
        
        # Basic metadata
        if soup.title and soup.title.string:
            metadata['title'] = soup.title.string.strip()
        
        # Meta tags
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            if meta.get('name'):
                metadata[meta['name']] = meta.get('content', '')
            elif meta.get('property'):
                metadata[meta['property']] = meta.get('content', '')
        
        # Response metadata
        if response:
            metadata['status_code'] = response.status_code
            metadata['content_type'] = response.headers.get('content-type', '')
            metadata['content_length'] = len(response.content)
        
        return metadata
    
    def _extract_selenium_metadata(self, driver, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extract metadata when using Selenium
        
        Args:
            driver: WebDriver instance
            soup: BeautifulSoup object
            
        Returns:
            Dictionary of metadata
        """
        metadata = self._extract_metadata(soup)
        
        # Additional Selenium-specific metadata
        metadata['current_url'] = driver.current_url
        metadata['page_source_length'] = len(driver.page_source)
        
        return metadata
    
    def _mock_scraping_result(self, url: str) -> ScrapingResult:
        """
        Generate mock scraping result for testing
        
        Args:
            url: URL to mock
            
        Returns:
            Mock scraping result
        """
        return ScrapingResult(
            url=url,
            success=True,
            title=f"Mock Page Title for {url}",
            text=f"This is mock content for {url}. The page contains information about the requested topic.",
            html=f"<html><head><title>Mock Page Title for {url}</title></head><body><p>This is mock content.</p></body></html>",
            links=[f"{url}/link1", f"{url}/link2"],
            images=[f"{url}/image1.jpg", f"{url}/image2.png"],
            metadata={
                'title': f"Mock Page Title for {url}",
                'description': f"Mock description for {url}",
                'status_code': 200,
                'content_type': 'text/html'
            }
        )
    
    def _scrape_multiple_urls(self, task: AgentTask) -> List[ScrapingResult]:
        """
        Scrape multiple URLs
        
        Args:
            task: Task containing list of URLs
            
        Returns:
            List of scraping results
        """
        urls = task.parameters.get("urls", [])
        if not urls:
            raise ValueError("URLs parameter is required for multiple scraping")
        
        results = []
        for i, url in enumerate(urls):
            self.logger.info(f"Scraping URL {i+1}/{len(urls)}: {url}")
            
            # Create individual task for each URL
            single_task = self.create_task(f"scrape_single_{i}", {
                "type": "scrape_url",
                "url": url,
                "use_selenium": task.parameters.get("use_selenium", False)
            })
            
            result = self.run_task(single_task)
            results.append(result)
            
            # Respect delay between requests
            if i < len(urls) - 1:  # Don't delay after last request
                time.sleep(self.scraping_config.delay_between_requests)
        
        return results
    
    def _extract_links_from_page(self, task: AgentTask) -> List[str]:
        """
        Extract links from a page
        
        Args:
            task: Task containing URL
            
        Returns:
            List of extracted links
        """
        url = task.parameters.get("url", "")
        if not url:
            raise ValueError("URL parameter is required")
        
        # First scrape the page
        scrape_task = self.create_task("scrape_for_links", {
            "type": "scrape_url",
            "url": url
        })
        
        result = self.run_task(scrape_task)
        return result.links if result.success else []
    
    def scrape_url(self, url: str, use_selenium: bool = False) -> ScrapingResult:
        """
        Convenience method to scrape a single URL
        
        Args:
            url: URL to scrape
            use_selenium: Whether to use Selenium
            
        Returns:
            Scraping result
        """
        task_id = self.create_task("scrape_url", {
            "type": "scrape_url",
            "url": url,
            "use_selenium": use_selenium
        })
        
        return self.run_task(task_id)
    
    def scrape_multiple_urls(self, urls: List[str], use_selenium: bool = False) -> List[ScrapingResult]:
        """
        Convenience method to scrape multiple URLs
        
        Args:
            urls: List of URLs to scrape
            use_selenium: Whether to use Selenium
            
        Returns:
            List of scraping results
        """
        task_id = self.create_task("scrape_multiple", {
            "type": "scrape_multiple",
            "urls": urls,
            "use_selenium": use_selenium
        })
        
        return self.run_task(task_id)
    
    def extract_links(self, url: str) -> List[str]:
        """
        Convenience method to extract links from a page
        
        Args:
            url: URL to extract links from
            
        Returns:
            List of links
        """
        task_id = self.create_task("extract_links", {
            "type": "extract_links", 
            "url": url
        })
        
        return self.run_task(task_id)
    
    def __del__(self):
        """Cleanup when agent is destroyed"""
        if hasattr(self, 'driver') and self.driver:
            try:
                self.driver.quit()
            except:
                pass