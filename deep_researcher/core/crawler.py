"""Web crawler for the Deep Research System."""

import logging
import time
from typing import List, Set
from urllib.parse import urljoin

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

from ..models.data_models import SearchResult, ScrapedContent


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