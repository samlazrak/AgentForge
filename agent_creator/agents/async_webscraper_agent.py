"""
Async Webscraper Agent - Enhanced webscraper with parallel processing capabilities
"""

import asyncio
import aiohttp
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
import logging
from urllib.parse import urljoin, urlparse

try:
    from bs4 import BeautifulSoup
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False

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

from ..core.async_agent import AsyncBaseAgent, AsyncAgentTask
from ..core.base_agent import AgentConfig
from .webscraper_agent import ScrapingResult, ScrapingConfig

class AsyncWebscraperAgent(AsyncBaseAgent):
    """
    Async webscraper agent with parallel processing capabilities
    """
    
    def __init__(self, config: Optional[AgentConfig] = None, scraping_config: Optional[ScrapingConfig] = None):
        """
        Initialize async webscraper agent
        
        Args:
            config: Agent configuration
            scraping_config: Scraping configuration
        """
        if config is None:
            config = AgentConfig(
                name="AsyncWebscraperAgent",
                description="Async agent for parallel web scraping",
                capabilities=[
                    "async_url_scraping",
                    "parallel_batch_scraping",
                    "concurrent_content_extraction",
                    "async_link_extraction"
                ]
            )
        
        super().__init__(config)
        self.scraping_config = scraping_config or ScrapingConfig()
        self.session_pool = None
        self.max_concurrent_requests = 5
    
    async def start_async(self):
        """Start async operations and initialize session pool"""
        await super().start_async()
        
        # Create HTTP session pool
        connector = aiohttp.TCPConnector(limit=self.max_concurrent_requests)
        timeout = aiohttp.ClientTimeout(total=self.scraping_config.timeout)
        
        headers = {"User-Agent": self.scraping_config.user_agent or "Mozilla/5.0"}
        self.session_pool = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=headers
        )
        
        self.logger.info("Async webscraper agent started with session pool")
    
    async def stop_async(self):
        """Stop async operations and cleanup session pool"""
        if self.session_pool:
            await self.session_pool.close()
        
        await super().stop_async()
        self.logger.info("Async webscraper agent stopped")
    
    def execute_task(self, task) -> Any:
        """
        Sync execute task - delegates to async version
        
        Args:
            task: Task to execute
            
        Returns:
            Task result
        """
        # Create async task if needed
        if not isinstance(task, AsyncAgentTask):
            async_task = AsyncAgentTask(
                task_id=task.task_id,
                description=task.description,
                parameters=task.parameters
            )
        else:
            async_task = task
        
        # Run async version in event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a task
                raise RuntimeError("Cannot run sync execute_task in running async context. Use execute_task_async instead.")
            else:
                return loop.run_until_complete(self.execute_task_async(async_task))
        except RuntimeError:
            # If no event loop, create one
            return asyncio.run(self.execute_task_async(async_task))
    
    async def execute_task_async(self, task: AsyncAgentTask) -> Any:
        """
        Execute async scraping task
        
        Args:
            task: Task to execute
            
        Returns:
            Scraping result
        """
        task_type = task.parameters.get("type", "scrape_url")
        
        if task_type == "scrape_url":
            return await self._scrape_single_url_async(task)
        elif task_type == "scrape_multiple":
            return await self._scrape_multiple_urls_async(task)
        elif task_type == "scrape_batch":
            return await self._scrape_batch_parallel(task)
        elif task_type == "extract_links":
            return await self._extract_links_async(task)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _scrape_single_url_async(self, task: AsyncAgentTask) -> ScrapingResult:
        """
        Scrape single URL asynchronously
        
        Args:
            task: Scraping task
            
        Returns:
            Scraping result
        """
        url = task.parameters.get("url", "")
        use_selenium = task.parameters.get("use_selenium", False)
        
        if not url:
            raise ValueError("URL parameter is required")
        
        self.logger.info(f"Starting async scrape: {url}")
        start_time = time.time()
        
        try:
            if use_selenium and SELENIUM_AVAILABLE:
                result = await self._scrape_with_selenium_async(url)
            else:
                result = await self._scrape_with_aiohttp(url)
            
            result.response_time = time.time() - start_time
            self.logger.info(f"Async scraping completed for: {url} in {result.response_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Async scraping failed for {url}: {e}")
            return ScrapingResult(
                url=url,
                success=False,
                error=str(e),
                response_time=time.time() - start_time
            )
    
    async def _scrape_with_aiohttp(self, url: str) -> ScrapingResult:
        """
        Scrape URL using aiohttp
        
        Args:
            url: URL to scrape
            
        Returns:
            Scraping result
        """
        result = ScrapingResult(url=url)
        
        try:
            if not self.session_pool:
                raise RuntimeError("Session pool not initialized")
            
            async with self.session_pool.get(url) as response:
                if response.status != 200:
                    result.error = f"HTTP {response.status}"
                    return result
                
                # Check content length
                content_length = response.headers.get('content-length')
                if content_length and int(content_length) > self.scraping_config.max_content_length:
                    result.error = f"Content too large: {content_length} bytes"
                    return result
                
                # Read content
                content = await response.read()
                
                if len(content) > self.scraping_config.max_content_length:
                    self.logger.warning(f"Truncating content for {url}")
                    content = content[:self.scraping_config.max_content_length]
                
                # Parse HTML
                if BEAUTIFULSOUP_AVAILABLE:
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    result.success = True
                    result.html = str(soup)
                    result.title = soup.title.string.strip() if soup.title and soup.title.string else ""
                    result.text = self._extract_text_content(soup)
                    
                    if self.scraping_config.extract_links:
                        result.links = self._extract_links(soup, url)
                    
                    if self.scraping_config.extract_images:
                        result.images = self._extract_images(soup, url)
                    
                    result.metadata = self._extract_metadata(soup, response)
                else:
                    # Fallback without BeautifulSoup
                    result.success = True
                    result.html = content.decode('utf-8', errors='ignore')
                    result.text = result.html  # Basic fallback
                    result.metadata = {
                        'status_code': response.status,
                        'content_type': response.headers.get('content-type', ''),
                        'content_length': len(content)
                    }
        
        except Exception as e:
            result.error = str(e)
            self.logger.error(f"aiohttp scraping failed: {e}")
        
        return result
    
    async def _scrape_with_selenium_async(self, url: str) -> ScrapingResult:
        """
        Scrape URL using Selenium in executor
        
        Args:
            url: URL to scrape
            
        Returns:
            Scraping result
        """
        if not SELENIUM_AVAILABLE:
            self.logger.warning("Selenium not available, falling back to aiohttp")
            return await self._scrape_with_aiohttp(url)
        
        # Run Selenium in thread executor to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self._run_selenium_scrape,
            url
        )
        
        return result
    
    def _run_selenium_scrape(self, url: str) -> ScrapingResult:
        """
        Run Selenium scraping in executor
        
        Args:
            url: URL to scrape
            
        Returns:
            Scraping result
        """
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
            if BEAUTIFULSOUP_AVAILABLE:
                soup = BeautifulSoup(result.html, 'html.parser')
                result.text = self._extract_text_content(soup)
                
                if self.scraping_config.extract_links:
                    result.links = self._extract_links(soup, url)
                
                if self.scraping_config.extract_images:
                    result.images = self._extract_images(soup, url)
                
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
    
    async def _scrape_multiple_urls_async(self, task: AsyncAgentTask) -> List[ScrapingResult]:
        """
        Scrape multiple URLs with controlled concurrency
        
        Args:
            task: Task with URL list
            
        Returns:
            List of scraping results
        """
        urls = task.parameters.get("urls", [])
        use_selenium = task.parameters.get("use_selenium", False)
        max_concurrent = task.parameters.get("max_concurrent", self.max_concurrent_requests)
        
        if not urls:
            raise ValueError("URLs parameter is required")
        
        self.logger.info(f"Starting parallel scraping of {len(urls)} URLs")
        
        semaphore = asyncio.Semaphore(max_concurrent)
        tasks = []
        
        for url in urls:
            task_params = {
                "type": "scrape_url",
                "url": url,
                "use_selenium": use_selenium
            }
            tasks.append(self._scrape_with_semaphore(task_params, semaphore))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful_results = []
        for i, result in enumerate(results):
            if isinstance(result, ScrapingResult):
                successful_results.append(result)
            else:
                self.logger.error(f"Scraping failed for URL {urls[i]}: {result}")
                successful_results.append(ScrapingResult(
                    url=urls[i],
                    success=False,
                    error=str(result)
                ))
        
        return successful_results
    
    async def _scrape_with_semaphore(self, task_params: Dict[str, Any], semaphore: asyncio.Semaphore) -> ScrapingResult:
        """
        Scrape URL with semaphore control
        
        Args:
            task_params: Task parameters
            semaphore: Concurrency control
            
        Returns:
            Scraping result
        """
        async with semaphore:
            # Add delay between requests
            if self.scraping_config.delay_between_requests > 0:
                await asyncio.sleep(self.scraping_config.delay_between_requests)
            
            # Create task and execute
            scrape_task = AsyncAgentTask(
                task_id="temp_scrape",
                description="Scrape URL",
                parameters=task_params
            )
            
            return await self._scrape_single_url_async(scrape_task)
    
    async def _scrape_batch_parallel(self, task: AsyncAgentTask) -> Dict[str, List[ScrapingResult]]:
        """
        Scrape multiple batches of URLs in parallel
        
        Args:
            task: Batch scraping task
            
        Returns:
            Dictionary of batch results
        """
        batches = task.parameters.get("batches", {})
        
        if not batches:
            raise ValueError("Batches parameter is required")
        
        self.logger.info(f"Starting batch scraping of {len(batches)} batches")
        
        # Create tasks for each batch
        batch_tasks = {}
        for batch_name, urls in batches.items():
            batch_task = AsyncAgentTask(
                task_id=f"batch_{batch_name}",
                description=f"Scrape batch: {batch_name}",
                parameters={
                    "type": "scrape_multiple",
                    "urls": urls,
                    "max_concurrent": 3  # Limit per batch
                }
            )
            batch_tasks[batch_name] = self._scrape_multiple_urls_async(batch_task)
        
        # Execute all batches in parallel
        batch_results = await asyncio.gather(*batch_tasks.values(), return_exceptions=True)
        
        # Combine results
        results = {}
        for batch_name, result in zip(batches.keys(), batch_results):
            if isinstance(result, list):
                results[batch_name] = result
            else:
                self.logger.error(f"Batch {batch_name} failed: {result}")
                results[batch_name] = []
        
        return results
    
    async def _extract_links_async(self, task: AsyncAgentTask) -> List[str]:
        """
        Extract links from URL asynchronously
        
        Args:
            task: Link extraction task
            
        Returns:
            List of extracted links
        """
        url = task.parameters.get("url", "")
        if not url:
            raise ValueError("URL parameter is required")
        
        # First scrape the page
        scrape_task = AsyncAgentTask(
            task_id="temp_scrape",
            description="Scrape for links",
            parameters={"type": "scrape_url", "url": url}
        )
        
        result = await self._scrape_single_url_async(scrape_task)
        
        if result.success and result.links:
            return result.links
        else:
            return []
    
    def _extract_text_content(self, soup) -> str:
        """Extract clean text from HTML"""
        if not BEAUTIFULSOUP_AVAILABLE:
            return ""
        
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
    
    def _extract_links(self, soup, base_url: str) -> List[str]:
        """Extract links from HTML"""
        if not BEAUTIFULSOUP_AVAILABLE:
            return []
        
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            if absolute_url not in links:
                links.append(absolute_url)
        return links
    
    def _extract_images(self, soup, base_url: str) -> List[str]:
        """Extract image URLs from HTML"""
        if not BEAUTIFULSOUP_AVAILABLE:
            return []
        
        images = []
        for img in soup.find_all('img', src=True):
            src = img['src']
            absolute_url = urljoin(base_url, src)
            if absolute_url not in images:
                images.append(absolute_url)
        return images
    
    def _extract_metadata(self, soup, response) -> Dict[str, Any]:
        """Extract metadata from HTML and response"""
        metadata = {}
        
        if BEAUTIFULSOUP_AVAILABLE:
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
        if hasattr(response, 'status'):
            metadata['status_code'] = response.status
            metadata['content_type'] = response.headers.get('content-type', '')
        
        return metadata
    
    def _extract_selenium_metadata(self, driver, soup) -> Dict[str, Any]:
        """Extract metadata using Selenium"""
        metadata = self._extract_metadata(soup, None)
        
        # Additional Selenium metadata
        metadata['current_url'] = driver.current_url
        metadata['page_source_length'] = len(driver.page_source)
        
        return metadata
    
    # Convenience methods for external use
    async def scrape_url_async(self, url: str, use_selenium: bool = False) -> ScrapingResult:
        """
        Convenience method to scrape single URL
        
        Args:
            url: URL to scrape
            use_selenium: Whether to use Selenium
            
        Returns:
            Scraping result
        """
        task_id = await self.create_task_async(
            f"Scrape: {url}",
            {
                "type": "scrape_url",
                "url": url,
                "use_selenium": use_selenium
            }
        )
        
        return await self.wait_for_task(task_id)
    
    async def scrape_multiple_urls_async(self, urls: List[str], max_concurrent: int = 5) -> List[ScrapingResult]:
        """
        Convenience method to scrape multiple URLs
        
        Args:
            urls: List of URLs to scrape
            max_concurrent: Maximum concurrent requests
            
        Returns:
            List of scraping results
        """
        task_id = await self.create_task_async(
            f"Scrape {len(urls)} URLs",
            {
                "type": "scrape_multiple",
                "urls": urls,
                "max_concurrent": max_concurrent
            }
        )
        
        return await self.wait_for_task(task_id)
    
    async def extract_links_async(self, url: str) -> List[str]:
        """
        Convenience method to extract links
        
        Args:
            url: URL to extract links from
            
        Returns:
            List of extracted links
        """
        task_id = await self.create_task_async(
            f"Extract links: {url}",
            {
                "type": "extract_links",
                "url": url
            }
        )
        
        return await self.wait_for_task(task_id)