"""
Unit tests for the Webscraper Agent
"""

import pytest
import tempfile
import os
import time
from unittest.mock import patch, MagicMock
from datetime import datetime

from agent_creator.agents.webscraper_agent import (
    WebscraperAgent, 
    ScrapingResult, 
    ScrapingConfig,
    AgentConfig
)

class TestWebscraperAgent:
    """Test cases for Webscraper Agent"""
    
    @pytest.fixture
    def agent(self):
        """Create a webscraper agent for testing"""
        config = AgentConfig(
            name="TestWebscraperAgent",
            description="Test webscraper agent",
            capabilities=["url_scraping", "content_extraction", "link_extraction"]
        )
        scraping_config = ScrapingConfig(timeout=10, delay_between_requests=0.1)
        return WebscraperAgent(config, scraping_config)
    
    @pytest.fixture
    def mock_response(self):
        """Mock HTTP response for testing"""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {'content-type': 'text/html; charset=utf-8'}
        mock_resp.content = b'''
        <html>
            <head>
                <title>Test Page</title>
                <meta name="description" content="Test description">
                <meta property="og:title" content="OG Test Title">
            </head>
            <body>
                <h1>Main Title</h1>
                <p>Test paragraph content.</p>
                <a href="/link1">Link 1</a>
                <a href="https://example.com/link2">Link 2</a>
                <img src="/image1.jpg" alt="Image 1">
                <img src="https://example.com/image2.png" alt="Image 2">
                <script>console.log('test');</script>
                <style>body { color: black; }</style>
            </body>
        </html>
        '''
        return mock_resp
    
    @pytest.fixture
    def sample_scraping_result(self):
        """Sample scraping result for testing"""
        return ScrapingResult(
            url="https://example.com/test",
            success=True,
            title="Test Page",
            text="Main Title\nTest paragraph content.",
            html="<html><body><h1>Test</h1></body></html>",
            links=["https://example.com/link1", "https://example.com/link2"],
            images=["https://example.com/image1.jpg"],
            metadata={'title': 'Test Page', 'status_code': 200},
            response_time=1.5
        )
    
    def test_agent_initialization(self, agent):
        """Test agent initialization"""
        assert agent.config.name == "TestWebscraperAgent"
        assert "url_scraping" in agent.config.capabilities
        assert agent.agent_id is not None
        assert agent.scraping_config.timeout == 10
        assert agent.scraping_config.delay_between_requests == 0.1
        
    def test_agent_default_initialization(self):
        """Test agent initialization with default config"""
        agent = WebscraperAgent()
        assert agent.config.name == "WebscraperAgent"
        assert agent.config.description == "Agent specialized in web scraping and content extraction"
        assert len(agent.config.capabilities) == 6
        assert agent.scraping_config.timeout == 30
        
    def test_scraping_config(self):
        """Test scraping configuration"""
        config = ScrapingConfig(
            timeout=60,
            max_retries=5,
            delay_between_requests=2.0,
            use_selenium=True,
            headless=False
        )
        
        assert config.timeout == 60
        assert config.max_retries == 5
        assert config.delay_between_requests == 2.0
        assert config.use_selenium == True
        assert config.headless == False
        
    @patch('agent_creator.agents.webscraper_agent.requests.get')
    def test_scrape_with_requests_success(self, mock_get, agent, mock_response):
        """Test successful scraping with requests"""
        mock_get.return_value = mock_response
        agent.requests_available = True
        
        result = agent._scrape_with_requests("https://example.com/test")
        
        assert result.success == True
        assert result.url == "https://example.com/test"
        assert result.title == "Test Page"
        assert "Main Title" in result.text
        assert "Test paragraph content" in result.text
        assert "console.log" not in result.text  # Scripts should be removed
        assert len(result.links) > 0
        assert len(result.images) > 0
        assert result.metadata['status_code'] == 200
        
        mock_get.assert_called_once()
        
    @patch('agent_creator.agents.webscraper_agent.requests.get')
    def test_scrape_with_requests_failure(self, mock_get, agent):
        """Test scraping failure with requests"""
        mock_get.side_effect = Exception("Connection error")
        agent.requests_available = True
        
        result = agent._scrape_with_requests("https://example.com/test")
        
        assert result.success == False
        assert result.error == "Connection error"
        assert result.url == "https://example.com/test"
        
    def test_scrape_requests_not_available(self, agent):
        """Test scraping when requests is not available"""
        agent.requests_available = False
        
        result = agent._scrape_with_requests("https://example.com/test")
        
        assert result.success == True  # Mock result
        assert "Mock Page Title" in result.title
        assert "mock content" in result.text.lower()
        
    def test_extract_text_content(self, agent):
        """Test text content extraction"""
        from bs4 import BeautifulSoup
        
        html = '''
        <html>
            <body>
                <h1>Title</h1>
                <p>Paragraph 1</p>
                <p>Paragraph 2</p>
                <script>alert('test');</script>
                <style>body { color: red; }</style>
            </body>
        </html>
        '''
        
        soup = BeautifulSoup(html, 'html.parser')
        text = agent._extract_text_content(soup)
        
        assert "Title" in text
        assert "Paragraph 1" in text
        assert "Paragraph 2" in text
        assert "alert" not in text  # Script content should be removed
        assert "color: red" not in text  # Style content should be removed
        
    def test_extract_links(self, agent):
        """Test link extraction"""
        from bs4 import BeautifulSoup
        
        html = '''
        <html>
            <body>
                <a href="/relative-link">Relative</a>
                <a href="https://external.com/absolute">Absolute</a>
                <a href="#anchor">Anchor</a>
                <a>No href</a>
            </body>
        </html>
        '''
        
        soup = BeautifulSoup(html, 'html.parser')
        links = agent._extract_links(soup, "https://example.com")
        
        assert "https://example.com/relative-link" in links
        assert "https://external.com/absolute" in links
        assert "https://example.com#anchor" in links
        assert len(links) == 3  # Only links with href
        
    def test_extract_images(self, agent):
        """Test image extraction"""
        from bs4 import BeautifulSoup
        
        html = '''
        <html>
            <body>
                <img src="/relative-image.jpg" alt="Relative">
                <img src="https://external.com/absolute.png" alt="Absolute">
                <img alt="No src">
            </body>
        </html>
        '''
        
        soup = BeautifulSoup(html, 'html.parser')
        images = agent._extract_images(soup, "https://example.com")
        
        assert "https://example.com/relative-image.jpg" in images
        assert "https://external.com/absolute.png" in images
        assert len(images) == 2  # Only images with src
        
    def test_extract_metadata(self, agent, mock_response):
        """Test metadata extraction"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(mock_response.content, 'html.parser')
        metadata = agent._extract_metadata(soup, mock_response)
        
        assert metadata['title'] == 'Test Page'
        assert metadata['description'] == 'Test description'
        assert metadata['og:title'] == 'OG Test Title'
        assert metadata['status_code'] == 200
        assert metadata['content_type'] == 'text/html; charset=utf-8'
        
    def test_mock_scraping_result(self, agent):
        """Test mock scraping result generation"""
        result = agent._mock_scraping_result("https://example.com/test")
        
        assert result.success == True
        assert result.url == "https://example.com/test"
        assert "Mock Page Title" in result.title
        assert "mock content" in result.text.lower()
        assert len(result.links) > 0
        assert len(result.images) > 0
        assert result.metadata['status_code'] == 200
        
    def test_scrape_single_url_task(self, agent):
        """Test single URL scraping task"""
        agent.requests_available = False  # Use mock data
        
        task_id = agent.create_task("scrape_test", {
            "type": "scrape_url",
            "url": "https://example.com/test"
        })
        
        result = agent.run_task(task_id)
        
        assert isinstance(result, ScrapingResult)
        assert result.url == "https://example.com/test"
        assert result.success == True
        assert result.response_time > 0
        
    def test_scrape_multiple_urls_task(self, agent):
        """Test multiple URLs scraping task"""
        agent.requests_available = False  # Use mock data
        urls = ["https://example.com/page1", "https://example.com/page2"]
        
        task_id = agent.create_task("scrape_multiple", {
            "type": "scrape_multiple",
            "urls": urls
        })
        
        results = agent.run_task(task_id)
        
        assert isinstance(results, list)
        assert len(results) == 2
        assert all(isinstance(r, ScrapingResult) for r in results)
        assert results[0].url == urls[0]
        assert results[1].url == urls[1]
        
    def test_extract_links_task(self, agent):
        """Test link extraction task"""
        agent.requests_available = False  # Use mock data
        
        task_id = agent.create_task("extract_links", {
            "type": "extract_links",
            "url": "https://example.com/test"
        })
        
        links = agent.run_task(task_id)
        
        assert isinstance(links, list)
        assert len(links) > 0
        assert all(isinstance(link, str) for link in links)
        
    def test_convenience_methods(self, agent):
        """Test convenience methods"""
        agent.requests_available = False  # Use mock data
        
        # Test scrape_url
        result = agent.scrape_url("https://example.com/test")
        assert isinstance(result, ScrapingResult)
        assert result.success == True
        
        # Test scrape_multiple_urls
        urls = ["https://example.com/page1", "https://example.com/page2"]
        results = agent.scrape_multiple_urls(urls)
        assert isinstance(results, list)
        assert len(results) == 2
        
        # Test extract_links
        links = agent.extract_links("https://example.com/test")
        assert isinstance(links, list)
        assert len(links) > 0
        
    def test_task_execution_error_handling(self, agent):
        """Test error handling in task execution"""
        task = agent.create_task("invalid_task", {
            "type": "invalid_type"
        })
        
        with pytest.raises(ValueError, match="Unknown task type"):
            agent.run_task(task)
            
    def test_scraping_task_missing_url(self, agent):
        """Test scraping task with missing URL parameter"""
        task = agent.create_task("scrape_no_url", {
            "type": "scrape_url"
            # Missing url parameter
        })
        
        with pytest.raises(ValueError, match="URL parameter is required"):
            agent.run_task(task)
            
    def test_multiple_scraping_missing_urls(self, agent):
        """Test multiple scraping task with missing URLs parameter"""
        task = agent.create_task("scrape_no_urls", {
            "type": "scrape_multiple"
            # Missing urls parameter
        })
        
        with pytest.raises(ValueError, match="URLs parameter is required"):
            agent.run_task(task)
            
    @patch('agent_creator.agents.webscraper_agent.webdriver.Chrome')
    def test_selenium_fallback(self, mock_chrome, agent):
        """Test Selenium fallback when not available"""
        agent.selenium_available = False
        agent.requests_available = False
        
        result = agent._scrape_with_selenium("https://example.com/test")
        
        assert result.success == True  # Should fallback to mock
        assert "Mock Page Title" in result.title
        mock_chrome.assert_not_called()  # Selenium should not be used
        
    def test_agent_lifecycle(self, agent):
        """Test agent start/stop lifecycle"""
        assert not agent.is_running
        
        agent.start()
        assert agent.is_running
        
        agent.stop()
        assert not agent.is_running
        
    def test_task_status_tracking(self, agent):
        """Test task status tracking"""
        task_id = agent.create_task("test_task", {
            "type": "scrape_url", 
            "url": "https://example.com/test"
        })
        
        # Check initial status
        status = agent.get_task_status(task_id)
        assert status['status'] == 'pending'
        assert status['task_id'] == task_id
        
    def test_list_tasks(self, agent):
        """Test listing all tasks"""
        task_id1 = agent.create_task("task1", {
            "type": "scrape_url", 
            "url": "https://example.com/test1"
        })
        task_id2 = agent.create_task("task2", {
            "type": "scrape_url", 
            "url": "https://example.com/test2"
        })
        
        tasks = agent.list_tasks()
        assert len(tasks) == 2
        task_ids = [task['task_id'] for task in tasks]
        assert task_id1 in task_ids
        assert task_id2 in task_ids
        
    def test_get_agent_info(self, agent):
        """Test getting agent information"""
        info = agent.get_agent_info()
        assert info['name'] == agent.config.name
        assert info['agent_id'] == agent.agent_id
        assert 'capabilities' in info
        assert 'llm_info' in info
        
    def test_string_representations(self, agent):
        """Test string representations of agent"""
        str_repr = str(agent)
        assert agent.config.name in str_repr
        assert agent.agent_id in str_repr
        
        repr_str = repr(agent)
        assert repr_str == str_repr
        
    def test_content_length_limit(self, agent):
        """Test content length limiting"""
        # Create a large mock response
        large_content = b"<html><body>" + b"x" * 2000000 + b"</body></html>"
        
        with patch('agent_creator.agents.webscraper_agent.requests.get') as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.headers = {'content-type': 'text/html'}
            mock_resp.content = large_content
            mock_get.return_value = mock_resp
            
            agent.requests_available = True
            agent.scraping_config.max_content_length = 1000000  # 1MB
            
            result = agent._scrape_with_requests("https://example.com/large")
            
            assert result.success == True
            # Content should be truncated
            assert len(result.html) <= agent.scraping_config.max_content_length * 2  # Allow for HTML parsing overhead
            
    def test_user_agent_configuration(self, agent):
        """Test user agent configuration"""
        assert agent.scraping_config.user_agent is not None
        assert "Mozilla" in agent.scraping_config.user_agent
        
    def test_delay_between_requests(self, agent):
        """Test delay between multiple requests"""
        agent.requests_available = False  # Use mock data
        agent.scraping_config.delay_between_requests = 0.1
        
        urls = ["https://example.com/page1", "https://example.com/page2"]
        start_time = time.time()
        
        results = agent.scrape_multiple_urls(urls)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should have at least one delay
        assert total_time >= 0.1
        assert len(results) == 2
        
    def test_scraping_result_dataclass(self):
        """Test ScrapingResult dataclass"""
        result = ScrapingResult(url="https://example.com")
        
        assert result.url == "https://example.com"
        assert result.success == False  # Default
        assert result.title == ""  # Default
        assert result.text == ""  # Default
        assert result.links == []  # Default
        assert isinstance(result.timestamp, datetime)
        assert result.response_time == 0.0  # Default