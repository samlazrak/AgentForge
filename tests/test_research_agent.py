"""
Unit tests for the Research Agent
"""

import pytest
import tempfile
import os
import json
from unittest.mock import patch, MagicMock
from datetime import datetime

from agent_creator.agents.research_agent import (
    ResearchAgent, 
    ResearchResult, 
    Source,
    AgentConfig
)

class TestResearchAgent:
    """Test cases for Research Agent"""
    
    @pytest.fixture
    def agent(self):
        """Create a research agent for testing"""
        config = AgentConfig(
            name="TestResearchAgent",
            description="Test research agent",
            capabilities=["web_search", "content_analysis", "citation_generation"]
        )
        return ResearchAgent(config)
    
    @pytest.fixture
    def mock_search_results(self):
        """Mock search results for testing"""
        return [
            {
                'title': 'Test Article 1',
                'url': 'https://example.com/article1',
                'snippet': 'This is a test article about machine learning and AI.',
                'published': '2024-01-01'
            },
            {
                'title': 'Test Article 2', 
                'url': 'https://example.com/article2',
                'snippet': 'Another test article discussing AI applications.',
                'published': '2024-01-02'
            }
        ]
    
    @pytest.fixture
    def sample_research_result(self):
        """Sample research result for testing"""
        return ResearchResult(
            query="machine learning",
            sources=[
                {
                    'title': 'ML Article',
                    'url': 'https://example.com/ml',
                    'snippet': 'Article about machine learning',
                    'content': 'Full content about ML',
                    'relevance_score': 0.8,
                    'citation': 'ML Article. Retrieved from https://example.com/ml'
                }
            ],
            summary="Machine learning is a field of AI that focuses on algorithms.",
            citations=["[1] ML Article. Retrieved from https://example.com/ml"],
            raw_data=[{'title': 'ML Article', 'url': 'https://example.com/ml'}]
        )
    
    def test_agent_initialization(self, agent):
        """Test agent initialization"""
        assert agent.config.name == "TestResearchAgent"
        assert "web_search" in agent.config.capabilities
        assert agent.agent_id is not None
        assert agent.llm is not None
        
    def test_agent_default_initialization(self):
        """Test agent initialization with default config"""
        agent = ResearchAgent()
        assert agent.config.name == "ResearchAgent"
        assert agent.config.description == "Agent specialized in performing deep online research"
        assert len(agent.config.capabilities) == 5
        
    def test_mock_search_results(self, agent):
        """Test mock search results generation"""
        results = agent._mock_search_results("test query", 3)
        assert len(results) == 3
        assert all('title' in result for result in results)
        assert all('url' in result for result in results)
        assert all('snippet' in result for result in results)
        assert all('test query' in result['title'] for result in results)
        
    @patch('agent_creator.agents.research_agent.DDGS')
    def test_web_search_with_ddgs(self, mock_ddgs, agent, mock_search_results):
        """Test web search with DuckDuckGo"""
        # Mock DDGS
        mock_ddgs_instance = MagicMock()
        mock_ddgs.return_value.__enter__.return_value = mock_ddgs_instance
        mock_ddgs_instance.text.return_value = [
            {
                'title': 'Test Article',
                'href': 'https://example.com/test',
                'body': 'Test snippet',
                'published': '2024-01-01'
            }
        ]
        
        # Set DDGS as available
        agent.ddgs_available = True
        
        results = agent._search_web("test query", 5)
        assert len(results) == 1
        assert results[0]['title'] == 'Test Article'
        assert results[0]['url'] == 'https://example.com/test'
        
    def test_web_search_fallback(self, agent):
        """Test web search fallback to mock results"""
        agent.ddgs_available = False
        results = agent._search_web("test query", 3)
        assert len(results) == 3
        assert all('Mock Result' in result['title'] for result in results)
        
    def test_process_search_result(self, agent, mock_search_results):
        """Test processing individual search results"""
        result = mock_search_results[0]
        source = agent._process_search_result(result)
        
        assert source is not None
        assert source.title == result['title']
        assert source.url == result['url']
        assert source.snippet == result['snippet']
        assert source.citation != ""
        assert source.relevance_score > 0
        
    def test_generate_citation(self, agent):
        """Test citation generation"""
        result = {
            'title': 'Test Article',
            'url': 'https://example.com/test',
            'published': '2024-01-01'
        }
        
        citation = agent._generate_citation(result)
        assert 'Test Article' in citation
        assert 'https://example.com/test' in citation
        assert '2024-01-01' in citation
        
    def test_generate_citations(self, agent):
        """Test generating multiple citations"""
        sources = [
            Source(title="Article 1", url="https://example.com/1", snippet="Snippet 1"),
            Source(title="Article 2", url="https://example.com/2", snippet="Snippet 2")
        ]
        
        citations = agent._generate_citations(sources)
        assert len(citations) == 2
        assert "[1]" in citations[0]
        assert "[2]" in citations[1]
        assert "Article 1" in citations[0]
        assert "Article 2" in citations[1]
        
    def test_generate_summary(self, agent):
        """Test summary generation using LLM"""
        sources = [
            Source(title="ML Article", url="https://example.com/ml", snippet="Machine learning basics")
        ]
        
        with patch.object(agent.llm, 'generate_response') as mock_llm:
            mock_llm.return_value = "This is a test summary about machine learning."
            
            summary = agent._generate_summary("machine learning", sources)
            assert summary == "This is a test summary about machine learning."
            mock_llm.assert_called_once()
            
    def test_source_to_dict(self, agent):
        """Test converting source to dictionary"""
        source = Source(
            title="Test Article",
            url="https://example.com/test",
            snippet="Test snippet",
            content="Full content",
            relevance_score=0.75,
            citation="Test citation"
        )
        
        source_dict = agent._source_to_dict(source)
        assert source_dict['title'] == "Test Article"
        assert source_dict['url'] == "https://example.com/test"
        assert source_dict['relevance_score'] == 0.75
        
    def test_perform_research_task(self, agent, mock_search_results):
        """Test complete research task execution"""
        # Mock the search and LLM
        agent.ddgs_available = False  # Use mock search
        
        with patch.object(agent.llm, 'generate_response') as mock_llm:
            mock_llm.return_value = "Test research summary"
            
            task = agent.create_task("research", {
                "type": "research", 
                "query": "machine learning",
                "max_results": 3
            })
            
            result = agent.run_task(task)
            
            assert isinstance(result, ResearchResult)
            assert result.query == "machine learning"
            assert len(result.sources) > 0
            assert result.summary == "Test research summary"
            assert len(result.citations) > 0
            
    def test_generate_text_report(self, agent, sample_research_result):
        """Test text report generation"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            filename = f.name
            
        try:
            result_path = agent._generate_text_report(sample_research_result.__dict__, filename)
            assert result_path == filename
            
            # Check file contents
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "machine learning" in content
                assert "Executive Summary" in content
                assert "Sources" in content
                assert "Citations" in content
                
        finally:
            if os.path.exists(filename):
                os.remove(filename)
                
    def test_generate_notebook(self, agent, sample_research_result):
        """Test Jupyter notebook generation"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ipynb', delete=False) as f:
            filename = f.name
            
        try:
            task = agent.create_task("generate_notebook", {
                "type": "generate_notebook",
                "research_result": sample_research_result.__dict__,
                "filename": filename
            })
            
            result_path = agent.run_task(task)
            assert result_path == filename
            
            # Check notebook structure
            with open(filename, 'r', encoding='utf-8') as f:
                notebook = json.load(f)
                assert 'cells' in notebook
                assert len(notebook['cells']) > 0
                assert notebook['nbformat'] == 4
                
                # Check for expected content
                content_str = json.dumps(notebook)
                assert "machine learning" in content_str
                assert "Research Analysis" in content_str
                
        finally:
            if os.path.exists(filename):
                os.remove(filename)
                
    def test_pdf_generation_fallback(self, agent, sample_research_result):
        """Test PDF generation fallback to text"""
        agent.pdf_available = False
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
            filename = f.name
            
        try:
            task = agent.create_task("generate_pdf", {
                "type": "generate_pdf",
                "research_result": sample_research_result.__dict__,
                "filename": filename
            })
            
            result_path = agent.run_task(task)
            # Should fallback to .txt file
            expected_txt_file = filename.replace('.pdf', '.txt')
            assert result_path == expected_txt_file
            assert os.path.exists(expected_txt_file)
            
            # Cleanup
            if os.path.exists(expected_txt_file):
                os.remove(expected_txt_file)
                
        finally:
            if os.path.exists(filename):
                os.remove(filename)
                
    def test_research_topic_convenience_method(self, agent):
        """Test the convenience method for researching topics"""
        agent.ddgs_available = False  # Use mock search
        
        with patch.object(agent.llm, 'generate_response') as mock_llm:
            mock_llm.return_value = "Test research summary"
            
            with tempfile.TemporaryDirectory() as temp_dir:
                os.chdir(temp_dir)
                
                result = agent.research_topic(
                    "test topic", 
                    max_results=3,
                    generate_pdf=True,
                    generate_notebook=True
                )
                
                assert 'research_result' in result
                assert 'files_generated' in result
                assert len(result['files_generated']) == 2  # PDF and notebook
                
                # Check files exist
                for file_path in result['files_generated']:
                    assert os.path.exists(file_path)
                    
    def test_task_execution_error_handling(self, agent):
        """Test error handling in task execution"""
        task = agent.create_task("invalid_task", {
            "type": "invalid_type"
        })
        
        with pytest.raises(ValueError, match="Unknown task type"):
            agent.run_task(task)
            
    def test_research_task_missing_query(self, agent):
        """Test research task with missing query parameter"""
        task = agent.create_task("research", {
            "type": "research"
            # Missing query parameter
        })
        
        with pytest.raises(ValueError, match="Query parameter is required"):
            agent.run_task(task)
            
    def test_webscraper_agent_integration(self, agent):
        """Test integration with webscraper agent"""
        mock_webscraper = MagicMock()
        mock_webscraper.scrape_url.return_value = {'text': 'Scraped content'}
        
        agent.set_webscraper_agent(mock_webscraper)
        assert agent.webscraper_agent is not None
        
        # Test that webscraper is called during result processing
        result = {
            'title': 'Test Article',
            'url': 'https://example.com/test',
            'snippet': 'Test snippet'
        }
        
        source = agent._process_search_result(result)
        assert source.content == 'Scraped content'
        mock_webscraper.scrape_url.assert_called_once_with('https://example.com/test')
        
    def test_agent_lifecycle(self, agent):
        """Test agent start/stop lifecycle"""
        assert not agent.is_running
        
        agent.start()
        assert agent.is_running
        
        agent.stop()
        assert not agent.is_running
        
    def test_task_status_tracking(self, agent):
        """Test task status tracking"""
        task_id = agent.create_task("test_task", {"type": "research", "query": "test"})
        
        # Check initial status
        status = agent.get_task_status(task_id)
        assert status['status'] == 'pending'
        assert status['task_id'] == task_id
        
        # Test invalid task ID
        with pytest.raises(ValueError, match="Task .* not found"):
            agent.get_task_status("invalid_id")
            
    def test_list_tasks(self, agent):
        """Test listing all tasks"""
        task_id1 = agent.create_task("task1", {"type": "research", "query": "test1"})
        task_id2 = agent.create_task("task2", {"type": "research", "query": "test2"})
        
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