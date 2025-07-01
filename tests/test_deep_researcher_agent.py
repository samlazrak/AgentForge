"""
Unit tests for the Deep Researcher Agent
"""

import pytest
import tempfile
import os
import json
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime

from agent_creator.agents.deep_researcher_agent import (
    DeepResearcherAgent,
    ExtractedLink,
    ScrapedContent,
    DeepResearchResult,
    AgentConfig
)
from agent_creator.agents.webscraper_agent import WebscraperAgent, ScrapingResult

class TestDeepResearcherAgent:
    """Test cases for Deep Researcher Agent"""
    
    @pytest.fixture
    def agent(self):
        """Create a deep researcher agent for testing"""
        config = AgentConfig(
            name="TestDeepResearcherAgent",
            description="Test deep researcher agent",
            capabilities=["pdf_link_extraction", "content_scraping", "content_filtering"]
        )
        return DeepResearcherAgent(config)
    
    @pytest.fixture
    def mock_webscraper_agent(self):
        """Create a mock webscraper agent"""
        mock_agent = MagicMock(spec=WebscraperAgent)
        return mock_agent
    
    @pytest.fixture
    def sample_extracted_links(self):
        """Sample extracted links for testing"""
        return [
            ExtractedLink(
                url="https://example.com/article1",
                text="Example Article 1",
                page_number=1,
                context="This is an example article about machine learning",
                bbox=(100, 200, 300, 220)
            ),
            ExtractedLink(
                url="https://github.com/user/repo",
                text="GitHub Repository",
                page_number=2,
                context="Check out this repository for more information"
            ),
            ExtractedLink(
                url="https://docs.python.org",
                text="Python Documentation",
                page_number=3,
                context="Official Python documentation and tutorials"
            )
        ]
    
    @pytest.fixture
    def sample_scraped_content(self):
        """Sample scraped content for testing"""
        return [
            ScrapedContent(
                url="https://example.com/article1",
                title="Machine Learning Article",
                clean_text="This is a comprehensive guide to machine learning concepts and applications.",
                images=["https://example.com/image1.jpg"],
                links=["https://example.com/related"],
                metadata={"author": "John Doe", "date": "2024-01-01"},
                success=True
            ),
            ScrapedContent(
                url="https://github.com/user/repo",
                title="GitHub Repository - ML Project",
                clean_text="A machine learning project with example code and datasets.",
                images=[],
                links=["https://github.com/user/repo/wiki"],
                metadata={"stars": 150, "language": "Python"},
                success=True
            )
        ]
    
    def test_agent_initialization(self, agent):
        """Test agent initialization"""
        assert agent.config.name == "TestDeepResearcherAgent"
        assert "pdf_link_extraction" in agent.config.capabilities
        assert agent.agent_id is not None
        assert agent.webscraper_agent is None
        
    def test_agent_default_initialization(self):
        """Test agent initialization with default config"""
        agent = DeepResearcherAgent()
        assert agent.config.name == "DeepResearcherAgent"
        assert agent.config.description == "Agent specialized in extracting links from PDFs and deep content scraping"
        assert len(agent.config.capabilities) == 5
        
    def test_set_webscraper_agent(self, agent, mock_webscraper_agent):
        """Test setting webscraper agent"""
        agent.set_webscraper_agent(mock_webscraper_agent)
        assert agent.webscraper_agent == mock_webscraper_agent
        
    def test_extract_urls_from_text(self, agent):
        """Test URL extraction from text"""
        text = """
        Check out these resources:
        https://example.com/article
        Visit www.python.org for documentation
        Also see http://github.com/user/repo
        """
        
        urls = agent._extract_urls_from_text(text)
        assert len(urls) >= 2
        assert "https://example.com/article" in urls
        assert any("python.org" in url for url in urls)
        assert any("github.com" in url for url in urls)
        
    def test_is_valid_url(self, agent):
        """Test URL validation"""
        valid_urls = [
            "https://example.com",
            "http://github.com/user/repo",
            "https://docs.python.org/3/"
        ]
        
        invalid_urls = [
            "not-a-url",
            "ftp://example.com",  # Different scheme
            "https://",  # No netloc
            ""
        ]
        
        for url in valid_urls:
            assert agent._is_valid_url(url), f"Should be valid: {url}"
            
        for url in invalid_urls:
            assert not agent._is_valid_url(url), f"Should be invalid: {url}"
            
    def test_extract_context_from_text(self, agent):
        """Test context extraction from text"""
        text = "This is a long document. You can find more information at https://example.com/article which contains detailed explanations."
        url = "https://example.com/article"
        
        context = agent._extract_context_from_text(text, url)
        assert "more information" in context
        assert url in context
        assert "detailed explanations" in context
        
    def test_filter_links_by_domain(self, agent, sample_extracted_links):
        """Test filtering links by domain"""
        allowed_domains = ["example.com", "github.com"]
        
        filtered_links = agent._filter_links_by_domain(sample_extracted_links, allowed_domains)
        assert len(filtered_links) == 2
        
        # Check that only allowed domains are present
        for link in filtered_links:
            domain = link.url.split("//")[1].split("/")[0]
            assert any(allowed in domain for allowed in allowed_domains)
            
    def test_filter_and_clean_content(self, agent):
        """Test content filtering and cleaning"""
        dirty_text = """
        Cookie Policy
        Accept Cookies
        Main content starts here
        This is the actual article content that we want to keep.
        It has multiple paragraphs with useful information.
        
        Footer
        Newsletter
        Follow us on social media
        Copyright 2024 All rights reserved
        """
        
        cleaned = agent._filter_and_clean_content(dirty_text)
        
        # Should keep main content
        assert "actual article content" in cleaned
        assert "useful information" in cleaned
        
        # Should remove unwanted elements
        assert "Cookie Policy" not in cleaned
        assert "Newsletter" not in cleaned
        assert "Follow us" not in cleaned
        assert "Copyright" not in cleaned
        
    def test_filter_content_task(self, agent):
        """Test content filtering task execution"""
        task = agent.create_task("filter_content", {
            "type": "filter_content",
            "text": "Newsletter signup\nActual content here\nCookie policy"
        })
        
        result = agent.run_task(task)
        assert "Actual content here" in result
        assert "Newsletter" not in result
        
    def test_filter_content_task_missing_text(self, agent):
        """Test content filtering with missing text parameter"""
        task = agent.create_task("filter_content", {
            "type": "filter_content"
        })
        
        with pytest.raises(ValueError, match="text parameter is required"):
            agent.run_task(task)
            
    @patch('agent_creator.agents.deep_researcher_agent.pdfplumber')
    def test_extract_links_from_pdf_file_with_hyperlinks(self, mock_pdfplumber, agent):
        """Test extracting links from PDF with hyperlinks"""
        # Mock pdfplumber
        agent.pdfplumber_available = True
        
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.hyperlinks = [
            {'uri': 'https://example.com/link1', 'text': 'Link 1', 'bbox': (100, 200, 300, 220)},
            {'uri': 'https://example.com/link2', 'text': 'Link 2', 'bbox': (100, 250, 300, 270)}
        ]
        mock_page.extract_text.return_value = "Some text content"
        
        mock_pdf.pages = [mock_page]
        mock_pdfplumber.open.return_value.__enter__.return_value = mock_pdf
        
        # Mock context extraction
        agent._extract_context_around_link = MagicMock(return_value="Test context")
        agent._extract_urls_from_text = MagicMock(return_value=[])
        
        links = agent._extract_links_from_pdf_file("test.pdf", max_links=5)
        
        assert len(links) == 2
        assert links[0].url == "https://example.com/link1"
        assert links[0].text == "Link 1"
        assert links[0].context == "Test context"
        
    @patch('agent_creator.agents.deep_researcher_agent.pdfplumber')
    def test_extract_links_from_pdf_file_with_text_urls(self, mock_pdfplumber, agent):
        """Test extracting URLs from PDF text content"""
        agent.pdfplumber_available = True
        
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.hyperlinks = []
        mock_page.extract_text.return_value = "Visit https://example.com for more info"
        
        mock_pdf.pages = [mock_page]
        mock_pdfplumber.open.return_value.__enter__.return_value = mock_pdf
        
        agent._extract_context_from_text = MagicMock(return_value="Test context")
        
        links = agent._extract_links_from_pdf_file("test.pdf", max_links=5)
        
        assert len(links) == 1
        assert links[0].url == "https://example.com"
        assert links[0].context == "Test context"
        
    def test_extract_links_from_pdf_file_mock_fallback(self, agent):
        """Test fallback to mock when pdfplumber is unavailable"""
        agent.pdfplumber_available = False
        
        links = agent._extract_links_from_pdf_file("test.pdf", max_links=3)
        
        assert len(links) == 3
        assert all("example-" in link.url for link in links)
        assert all(link.page_number == 1 for link in links)
        
    def test_extract_links_task(self, agent):
        """Test link extraction task"""
        agent.pdfplumber_available = False  # Use mock
        
        task = agent.create_task("extract_links", {
            "type": "extract_links",
            "pdf_path": "test.pdf",
            "max_links": 2
        })
        
        result = agent.run_task(task)
        assert len(result) == 2
        assert all(isinstance(link, ExtractedLink) for link in result)
        
    def test_extract_links_task_missing_path(self, agent):
        """Test link extraction with missing PDF path"""
        task = agent.create_task("extract_links", {
            "type": "extract_links"
        })
        
        with pytest.raises(ValueError, match="pdf_path parameter is required"):
            agent.run_task(task)
            
    def test_scrape_content_from_links_success(self, agent, sample_extracted_links, mock_webscraper_agent):
        """Test successful content scraping"""
        agent.set_webscraper_agent(mock_webscraper_agent)
        
        # Mock successful scraping results
        mock_results = [
            ScrapingResult(
                url="https://example.com/article1",
                success=True,
                title="Article 1",
                text="Content 1 with newsletter signup and cookie policy but also useful information",
                images=["image1.jpg"],
                links=["link1"],
                metadata={"test": True}
            ),
            ScrapingResult(
                url="https://github.com/user/repo",
                success=True,
                title="GitHub Repo",
                text="Repository description and documentation",
                images=[],
                links=["wiki"],
                metadata={"stars": 100}
            )
        ]
        
        mock_webscraper_agent.scrape_url.side_effect = mock_results[:2]
        
        scraped_content = agent._scrape_content_from_links(sample_extracted_links[:2])
        
        assert len(scraped_content) == 2
        assert all(content.success for content in scraped_content)
        assert mock_webscraper_agent.scrape_url.call_count == 2
        
        # Check that content was filtered
        assert "newsletter" not in scraped_content[0].clean_text.lower()
        assert "useful information" in scraped_content[0].clean_text
        
    def test_scrape_content_from_links_with_failure(self, agent, sample_extracted_links, mock_webscraper_agent):
        """Test content scraping with some failures"""
        agent.set_webscraper_agent(mock_webscraper_agent)
        
        # Mock mixed results
        mock_results = [
            ScrapingResult(url="https://example.com/article1", success=True, title="Article 1", text="Content 1"),
            ScrapingResult(url="https://github.com/user/repo", success=False, error="Connection timeout")
        ]
        
        mock_webscraper_agent.scrape_url.side_effect = mock_results
        
        scraped_content = agent._scrape_content_from_links(sample_extracted_links[:2])
        
        assert len(scraped_content) == 2
        assert scraped_content[0].success
        assert not scraped_content[1].success
        assert scraped_content[1].error == "Connection timeout"
        
    def test_scrape_content_from_links_no_webscraper(self, agent, sample_extracted_links):
        """Test content scraping without webscraper agent"""
        scraped_content = agent._scrape_content_from_links(sample_extracted_links)
        
        # Should use mock scraping
        assert len(scraped_content) == len(sample_extracted_links)
        assert all(content.success for content in scraped_content)
        assert all("Mock Title" in content.title for content in scraped_content)
        
    def test_scrape_links_task(self, agent, sample_extracted_links):
        """Test scrape links task execution"""
        # Convert to dict format for task
        link_dicts = [
            {"url": link.url, "text": link.text, "page_number": link.page_number, "context": link.context}
            for link in sample_extracted_links
        ]
        
        task = agent.create_task("scrape_links", {
            "type": "scrape_links",
            "links": link_dicts,
            "include_images": False
        })
        
        result = agent.run_task(task)
        assert len(result) == len(sample_extracted_links)
        assert all(isinstance(content, ScrapedContent) for content in result)
        
    def test_scrape_links_task_missing_links(self, agent):
        """Test scrape links task with missing links parameter"""
        task = agent.create_task("scrape_links", {
            "type": "scrape_links"
        })
        
        with pytest.raises(ValueError, match="links parameter is required"):
            agent.run_task(task)
            
    def test_generate_research_summary_with_content(self, agent, sample_extracted_links, sample_scraped_content):
        """Test research summary generation with successful content"""
        with patch.object(agent.llm, 'generate_response') as mock_llm:
            mock_llm.return_value = "This is a comprehensive research summary of machine learning topics."
            
            summary = agent._generate_research_summary(sample_extracted_links, sample_scraped_content)
            
            assert "comprehensive research summary" in summary
            mock_llm.assert_called_once()
            
            # Check that the prompt includes the right information
            call_args = mock_llm.call_args[0][0]
            assert "Total links extracted: 3" in call_args
            assert "Successfully scraped: 2" in call_args
            
    def test_generate_research_summary_no_content(self, agent, sample_extracted_links):
        """Test research summary generation with no successful content"""
        failed_content = [
            ScrapedContent(url="https://example.com", success=False, error="Failed")
        ]
        
        summary = agent._generate_research_summary(sample_extracted_links, failed_content)
        assert "No content was successfully scraped" in summary
        
    def test_generate_research_summary_llm_failure(self, agent, sample_extracted_links, sample_scraped_content):
        """Test research summary generation when LLM fails"""
        with patch.object(agent.llm, 'generate_response') as mock_llm:
            mock_llm.side_effect = Exception("LLM error")
            
            summary = agent._generate_research_summary(sample_extracted_links, sample_scraped_content)
            
            assert "Research completed with 2 successful content extractions" in summary
            
    @patch('os.path.exists')
    def test_perform_deep_research_complete_workflow(self, mock_exists, agent, mock_webscraper_agent):
        """Test complete deep research workflow"""
        mock_exists.return_value = True
        agent.pdfplumber_available = False  # Use mock extraction
        agent.set_webscraper_agent(mock_webscraper_agent)
        
        # Mock webscraper results
        mock_webscraper_agent.scrape_url.return_value = ScrapingResult(
            url="https://example-1.com/article",
            success=True,
            title="Example Article",
            text="This is example content about the topic",
            images=["image.jpg"],
            links=["related.html"],
            metadata={"source": "example"}
        )
        
        # Mock LLM for summary
        with patch.object(agent.llm, 'generate_response') as mock_llm:
            mock_llm.return_value = "Comprehensive research summary"
            
            task = agent.create_task("deep_research", {
                "type": "deep_research",
                "pdf_path": "test.pdf",
                "max_links": 3,
                "include_images": True
            })
            
            result = agent.run_task(task)
            
            assert isinstance(result, DeepResearchResult)
            assert result.source_pdf == "test.pdf"
            assert result.total_links_found == 3
            assert result.successful_scrapes == 3
            assert "Comprehensive research summary" in result.summary
            assert len(result.extracted_links) == 3
            assert len(result.scraped_content) == 3
            
    def test_perform_deep_research_missing_pdf_path(self, agent):
        """Test deep research with missing PDF path"""
        task = agent.create_task("deep_research", {
            "type": "deep_research"
        })
        
        with pytest.raises(ValueError, match="pdf_path parameter is required"):
            agent.run_task(task)
            
    @patch('os.path.exists')
    def test_perform_deep_research_file_not_found(self, mock_exists, agent):
        """Test deep research with non-existent PDF file"""
        mock_exists.return_value = False
        
        task = agent.create_task("deep_research", {
            "type": "deep_research",
            "pdf_path": "nonexistent.pdf"
        })
        
        with pytest.raises(FileNotFoundError, match="PDF file not found"):
            agent.run_task(task)
            
    @patch('os.path.exists')
    def test_perform_deep_research_with_domain_filtering(self, mock_exists, agent):
        """Test deep research with domain filtering"""
        mock_exists.return_value = True
        agent.pdfplumber_available = False  # Use mock extraction
        
        task = agent.create_task("deep_research", {
            "type": "deep_research",
            "pdf_path": "test.pdf",
            "max_links": 5,
            "filter_domains": ["example-1.com"]
        })
        
        result = agent.run_task(task)
        
        # Should only have links from allowed domain
        assert result.total_links_found == 1  # Only example-1.com should remain
        assert all("example-1.com" in link.url for link in result.extracted_links)
        
    def test_convenience_method_extract_links_from_pdf(self, agent):
        """Test convenience method for link extraction"""
        agent.pdfplumber_available = False  # Use mock
        
        links = agent.extract_links_from_pdf("test.pdf", max_links=2)
        
        assert len(links) == 2
        assert all(isinstance(link, ExtractedLink) for link in links)
        
    @patch('os.path.exists')
    def test_convenience_method_deep_research(self, mock_exists, agent):
        """Test convenience method for deep research"""
        mock_exists.return_value = True
        agent.pdfplumber_available = False  # Use mock
        
        # Mock LLM for summary
        with patch.object(agent.llm, 'generate_response') as mock_llm:
            mock_llm.return_value = "Test summary"
            
            result = agent.deep_research(
                pdf_path="test.pdf",
                max_links=2,
                filter_domains=["example.com"],
                include_images=False
            )
            
            assert isinstance(result, DeepResearchResult)
            assert result.source_pdf == "test.pdf"
            
    def test_task_execution_unknown_type(self, agent):
        """Test task execution with unknown task type"""
        task = agent.create_task("unknown_task", {
            "type": "unknown_type"
        })
        
        with pytest.raises(ValueError, match="Unknown task type"):
            agent.run_task(task)
            
    def test_agent_lifecycle(self, agent):
        """Test agent start/stop lifecycle"""
        assert not agent.is_running
        
        agent.start()
        assert agent.is_running
        
        agent.stop()
        assert not agent.is_running
        
    def test_get_agent_info(self, agent):
        """Test getting agent information"""
        info = agent.get_agent_info()
        assert info['name'] == agent.config.name
        assert info['agent_id'] == agent.agent_id
        assert 'capabilities' in info
        assert 'pdf_link_extraction' in info['capabilities']
        
    def test_string_representations(self, agent):
        """Test string representations of agent"""
        str_repr = str(agent)
        assert agent.config.name in str_repr
        assert agent.agent_id in str_repr
        
        repr_str = repr(agent)
        assert repr_str == str_repr