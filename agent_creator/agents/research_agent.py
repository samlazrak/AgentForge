"""
Research Agent for performing deep online research
"""

import json
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
import logging
import os
import re

try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False
    logging.warning("DuckDuckGo Search not available")

try:
    import requests
    from bs4 import BeautifulSoup
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False
    logging.warning("Web scraping dependencies not available")

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logging.warning("PDF generation dependencies not available")

from ..core.base_agent import BaseAgent, AgentConfig, AgentTask

@dataclass
class ResearchResult:
    """Represents a research result"""
    query: str
    sources: List[Dict[str, Any]] = field(default_factory=list)
    summary: str = ""
    citations: List[str] = field(default_factory=list)
    raw_data: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class Source:
    """Represents a research source"""
    title: str
    url: str
    snippet: str
    content: str = ""
    relevance_score: float = 0.0
    citation: str = ""

class ResearchAgent(BaseAgent):
    """
    Agent specialized in performing deep online research
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """
        Initialize the research agent
        
        Args:
            config: Agent configuration
        """
        if config is None:
            config = AgentConfig(
                name="ResearchAgent",
                description="Agent specialized in performing deep online research",
                capabilities=[
                    "web_search",
                    "content_analysis", 
                    "citation_generation",
                    "pdf_generation",
                    "notebook_generation"
                ]
            )
        
        super().__init__(config)
        self.webscraper_agent = None  # Will be set later
        
    def _initialize(self):
        """Initialize research-specific components"""
        self.logger.info("Initializing Research Agent")
        
        # Check available dependencies
        self.ddgs_available = DDGS_AVAILABLE
        self.scraping_available = SCRAPING_AVAILABLE
        self.pdf_available = PDF_AVAILABLE
        
        if not self.ddgs_available:
            self.logger.warning("DuckDuckGo search not available - using mock data")
        if not self.scraping_available:
            self.logger.warning("Web scraping not available - using mock data")
        if not self.pdf_available:
            self.logger.warning("PDF generation not available - using text output")
    
    def execute_task(self, task: AgentTask) -> Any:
        """
        Execute a research task
        
        Args:
            task: Task to execute
            
        Returns:
            Research result
        """
        task_type = task.parameters.get("type", "research")
        
        if task_type == "research":
            return self._perform_research(task)
        elif task_type == "generate_pdf":
            return self._generate_pdf_report(task)
        elif task_type == "generate_notebook":
            return self._generate_notebook(task)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    def _perform_research(self, task: AgentTask) -> ResearchResult:
        """
        Perform research on a given topic
        
        Args:
            task: Research task
            
        Returns:
            Research result
        """
        query = task.parameters.get("query", "")
        max_results = task.parameters.get("max_results", 10)
        
        if not query:
            raise ValueError("Query parameter is required for research tasks")
        
        self.logger.info(f"Starting research on: {query}")
        
        # Step 1: Perform web search
        search_results = self._search_web(query, max_results)
        
        # Step 2: Extract and analyze content
        sources = []
        for result in search_results:
            source = self._process_search_result(result)
            if source:
                sources.append(source)
        
        # Step 3: Generate summary using LLM
        summary = self._generate_summary(query, sources)
        
        # Step 4: Generate citations
        citations = self._generate_citations(sources)
        
        research_result = ResearchResult(
            query=query,
            sources=[self._source_to_dict(source) for source in sources],
            summary=summary,
            citations=citations,
            raw_data=search_results
        )
        
        self.logger.info(f"Research completed for: {query}")
        return research_result
    
    def _search_web(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search the web using DuckDuckGo
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of search results
        """
        if not self.ddgs_available:
            return self._mock_search_results(query, max_results)
        
        try:
            with DDGS() as ddgs:
                results = []
                for result in ddgs.text(query, max_results=max_results):
                    results.append({
                        'title': result.get('title', ''),
                        'url': result.get('href', ''),
                        'snippet': result.get('body', ''),
                        'published': result.get('published', '')
                    })
                return results
        except Exception as e:
            self.logger.error(f"Web search failed: {e}")
            return self._mock_search_results(query, max_results)
    
    def _mock_search_results(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock search results for testing"""
        results = []
        for i in range(min(max_results, 5)):
            results.append({
                'title': f'Mock Result {i+1} for {query}',
                'url': f'https://example.com/result{i+1}',
                'snippet': f'This is a mock search result snippet for {query}. It contains relevant information about the topic.',
                'published': datetime.now().isoformat()
            })
        return results
    
    def _process_search_result(self, result: Dict[str, Any]) -> Optional[Source]:
        """
        Process a single search result
        
        Args:
            result: Search result
            
        Returns:
            Processed source or None if processing failed
        """
        try:
            source = Source(
                title=result.get('title', ''),
                url=result.get('url', ''),
                snippet=result.get('snippet', ''),
                citation=self._generate_citation(result)
            )
            
            # Try to extract full content if webscraper is available
            if self.webscraper_agent:
                try:
                    content = self.webscraper_agent.scrape_url(result.get('url', ''))
                    source.content = content.get('text', '')[:5000]  # Limit content length
                except Exception as e:
                    self.logger.warning(f"Failed to scrape content from {result.get('url', '')}: {e}")
            
            # Calculate relevance score (simple implementation)
            source.relevance_score = len(source.snippet) / 1000.0
            
            return source
            
        except Exception as e:
            self.logger.error(f"Failed to process search result: {e}")
            return None
    
    def _generate_summary(self, query: str, sources: List[Source]) -> str:
        """
        Generate a summary of the research using LLM
        
        Args:
            query: Original query
            sources: List of sources
            
        Returns:
            Research summary
        """
        # Prepare context for LLM
        context = f"Research Query: {query}\n\n"
        context += "Sources:\n"
        
        for i, source in enumerate(sources[:5], 1):  # Limit to top 5 sources
            context += f"{i}. {source.title}\n"
            context += f"   URL: {source.url}\n"
            context += f"   Content: {source.snippet}\n"
            if source.content:
                context += f"   Full Content: {source.content[:500]}...\n"
            context += "\n"
        
        prompt = f"""
        {context}
        
        Based on the above sources, provide a comprehensive summary of the research on: {query}
        
        The summary should:
        1. Synthesize information from multiple sources
        2. Highlight key findings and insights
        3. Maintain objectivity and accuracy
        4. Be well-structured and informative
        
        Summary:
        """
        
        summary = self.llm.generate_response(prompt, max_tokens=1000)
        return summary
    
    def _generate_citations(self, sources: List[Source]) -> List[str]:
        """
        Generate citations for sources
        
        Args:
            sources: List of sources
            
        Returns:
            List of citations
        """
        citations = []
        for i, source in enumerate(sources, 1):
            citation = f"[{i}] {source.title}. Retrieved from {source.url}"
            citations.append(citation)
        return citations
    
    def _generate_citation(self, result: Dict[str, Any]) -> str:
        """
        Generate a single citation
        
        Args:
            result: Search result
            
        Returns:
            Citation string
        """
        title = result.get('title', 'Unknown Title')
        url = result.get('url', '')
        published = result.get('published', '')
        
        if published:
            return f"{title}. {published}. Retrieved from {url}"
        else:
            return f"{title}. Retrieved from {url}"
    
    def _source_to_dict(self, source: Source) -> Dict[str, Any]:
        """Convert source to dictionary"""
        return {
            'title': source.title,
            'url': source.url,
            'snippet': source.snippet,
            'content': source.content,
            'relevance_score': source.relevance_score,
            'citation': source.citation
        }
    
    def _generate_pdf_report(self, task: AgentTask) -> str:
        """
        Generate a PDF report from research results
        
        Args:
            task: Task containing research results
            
        Returns:
            Path to generated PDF file
        """
        research_result = task.parameters.get("research_result")
        if not research_result:
            raise ValueError("research_result parameter is required")
        
        filename = task.parameters.get("filename", f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        
        # Ensure filename is in research directory
        if not filename.startswith("research"):
            filename = os.path.join("research", filename)
        
        # Create research directory if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        if not self.pdf_available:
            # Fallback to text file
            text_filename = filename.replace('.pdf', '.txt')
            return self._generate_text_report(research_result, text_filename)
        
        try:
            doc = SimpleDocTemplate(filename, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1  # Center alignment
            )
            story.append(Paragraph(f"Research Report: {research_result['query']}", title_style))
            story.append(Spacer(1, 12))
            
            # Summary
            story.append(Paragraph("Executive Summary", styles['Heading2']))
            story.append(Paragraph(research_result['summary'], styles['Normal']))
            story.append(Spacer(1, 12))
            
            # Sources
            story.append(Paragraph("Sources", styles['Heading2']))
            for source in research_result['sources']:
                story.append(Paragraph(f"<b>{source['title']}</b>", styles['Normal']))
                story.append(Paragraph(f"URL: {source['url']}", styles['Normal']))
                story.append(Paragraph(source['snippet'], styles['Normal']))
                story.append(Spacer(1, 6))
            
            # Citations
            story.append(PageBreak())
            story.append(Paragraph("Citations", styles['Heading2']))
            for citation in research_result['citations']:
                story.append(Paragraph(citation, styles['Normal']))
                story.append(Spacer(1, 6))
            
            doc.build(story)
            self.logger.info(f"PDF report generated: {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Failed to generate PDF: {e}")
            # Fallback to text file
            text_filename = filename.replace('.pdf', '.txt')
            return self._generate_text_report(research_result, text_filename)
    
    def _generate_text_report(self, research_result: Dict[str, Any], filename: str) -> str:
        """Generate a text report as fallback"""
        # Ensure filename is in research directory
        if not filename.startswith("research"):
            filename = os.path.join("research", filename)
        
        # Create research directory if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Research Report: {research_result['query']}\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("Executive Summary\n")
            f.write("-" * 20 + "\n")
            f.write(research_result['summary'] + "\n\n")
            
            f.write("Sources\n")
            f.write("-" * 10 + "\n")
            for source in research_result['sources']:
                f.write(f"Title: {source['title']}\n")
                f.write(f"URL: {source['url']}\n")
                f.write(f"Snippet: {source['snippet']}\n")
                f.write("\n")
            
            f.write("Citations\n")
            f.write("-" * 10 + "\n")
            for citation in research_result['citations']:
                f.write(citation + "\n")
        
        return filename
    
    def _generate_notebook(self, task: AgentTask) -> str:
        """
        Generate a Jupyter notebook from research results
        
        Args:
            task: Task containing research results
            
        Returns:
            Path to generated notebook file
        """
        research_result = task.parameters.get("research_result")
        if not research_result:
            raise ValueError("research_result parameter is required")
        
        filename = task.parameters.get("filename", f"research_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ipynb")
        
        # Ensure filename is in research directory
        if not filename.startswith("research"):
            filename = os.path.join("research", filename)
        
        # Create research directory if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Create notebook structure
        query = research_result['query']
        summary = research_result['summary']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Build code cells content
        research_data_code = f"""# Research Data
import json
import pandas as pd

research_data = {json.dumps(research_result, indent=2, default=str)}

# Display basic statistics
print('Query: {query}')
print('Number of sources: {len(research_result.get("sources", []))}')
print('Number of citations: {len(research_result.get("citations", []))}')"""

        sources_analysis_code = """# Create DataFrame from sources
sources_df = pd.DataFrame(research_data['sources'])
print('Sources Overview:')
if not sources_df.empty:
    print(sources_df[['title', 'url', 'relevance_score']].head())

    # Plot relevance scores if available
    if 'relevance_score' in sources_df.columns:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(10, 6))
        plt.bar(range(len(sources_df)), sources_df['relevance_score'])
        plt.title('Source Relevance Scores')
        plt.xlabel('Source Index')
        plt.ylabel('Relevance Score')
        plt.show()
else:
    print('No sources available')"""

        citations_code = """# Display citations
for i, citation in enumerate(research_data.get('citations', []), 1):
    print(f'{i}. {citation}')"""
        
        notebook = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        f"# Research Analysis: {query}\\n\\nGenerated on: {timestamp}\\n"
                    ]
                },
                {
                    "cell_type": "markdown", 
                    "metadata": {},
                    "source": [
                        f"## Executive Summary\\n\\n{summary}\\n"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": research_data_code
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": "## Sources Analysis\\n"
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": sources_analysis_code
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": "## Citations\\n"
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": citations_code
                }
            ],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "name": "python",
                    "version": "3.8.0"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }
        
        # Write notebook to file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Jupyter notebook generated: {filename}")
        return filename
    
    def set_webscraper_agent(self, webscraper_agent):
        """Set the webscraper agent for content extraction"""
        self.webscraper_agent = webscraper_agent
        self.logger.info("Webscraper agent set for content extraction")
    
    def research_topic(self, query: str, max_results: int = 10, generate_pdf: bool = True, generate_notebook: bool = True) -> Dict[str, Any]:
        """
        Convenience method to research a topic and generate outputs
        
        Args:
            query: Research query
            max_results: Maximum number of search results
            generate_pdf: Whether to generate PDF report
            generate_notebook: Whether to generate Jupyter notebook
            
        Returns:
            Dictionary containing research results and file paths
        """
        # Create and run research task
        task_id = self.create_task("research", {
            "type": "research",
            "query": query,
            "max_results": max_results
        })
        
        research_result = self.run_task(task_id)
        
        result = {
            "research_result": research_result,
            "files_generated": []
        }
        
        # Generate PDF if requested
        if generate_pdf:
            pdf_task_id = self.create_task("generate_pdf", {
                "type": "generate_pdf",
                "research_result": research_result.__dict__,
                "filename": f"research_{query.replace(' ', '_')[:20]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            })
            pdf_path = self.run_task(pdf_task_id)
            result["files_generated"].append(pdf_path)
        
        # Generate notebook if requested
        if generate_notebook:
            notebook_task_id = self.create_task("generate_notebook", {
                "type": "generate_notebook",
                "research_result": research_result.__dict__,
                "filename": f"research_{query.replace(' ', '_')[:20]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ipynb"
            })
            notebook_path = self.run_task(notebook_task_id)
            result["files_generated"].append(notebook_path)
        
        return result