"""
Async Research Agent - Enhanced research agent with parallel processing capabilities
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
import logging

try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False

from ..core.async_agent import AsyncBaseAgent, AsyncAgentTask
from ..core.base_agent import AgentConfig
from .research_agent import ResearchResult, Source

class AsyncResearchAgent(AsyncBaseAgent):
    """
    Async research agent with parallel processing capabilities
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """
        Initialize async research agent
        
        Args:
            config: Agent configuration
        """
        if config is None:
            config = AgentConfig(
                name="AsyncResearchAgent",
                description="Async agent for parallel web research",
                capabilities=[
                    "async_web_search",
                    "parallel_content_analysis",
                    "batch_citation_generation",
                    "concurrent_scraping"
                ]
            )
        
        super().__init__(config)
        self.webscraper_agent = None
        self.max_concurrent_searches = 5
        self.max_concurrent_scrapes = 3
    
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
        Execute async research task
        
        Args:
            task: Task to execute
            
        Returns:
            Research result
        """
        task_type = task.parameters.get("type", "research")
        
        if task_type == "research":
            return await self._perform_research_parallel(task)
        elif task_type == "batch_research":
            return await self._perform_batch_research(task)
        elif task_type == "deep_research":
            return await self._perform_deep_research(task)
        else:
            # Fallback to sync execution for unknown types
            from .research_agent import ResearchAgent
            sync_agent = ResearchAgent()
            return sync_agent.execute_task(task)
    
    async def _perform_research_parallel(self, task: AsyncAgentTask) -> ResearchResult:
        """
        Perform research with parallel processing
        
        Args:
            task: Research task
            
        Returns:
            Research result
        """
        query = task.parameters.get("query", "")
        max_results = task.parameters.get("max_results", 10)
        
        if not query:
            raise ValueError("Query parameter is required")
        
        self.logger.info(f"Starting parallel research on: {query}")
        
        # Step 1: Parallel web search
        search_results = await self._search_web_parallel(query, max_results)
        
        # Step 2: Parallel content extraction and analysis
        sources = await self._process_search_results_parallel(search_results)
        
        # Step 3: Parallel LLM analysis
        summary = await self._generate_summary_async(query, sources)
        
        # Step 4: Generate citations
        citations = self._generate_citations(sources)
        
        research_result = ResearchResult(
            query=query,
            sources=[self._source_to_dict(source) for source in sources],
            summary=summary,
            citations=citations,
            raw_data=search_results
        )
        
        self.logger.info(f"Parallel research completed for: {query}")
        return research_result
    
    async def _search_web_parallel(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Search web using multiple search strategies in parallel
        
        Args:
            query: Search query
            max_results: Maximum results
            
        Returns:
            Combined search results
        """
        search_tasks = []
        
        # Main search
        search_tasks.append(self._search_duckduckgo_async(query, max_results // 2))
        
        # Additional search variations
        search_variations = [
            f"{query} overview",
            f"{query} analysis",
            f"{query} research",
            f"{query} guide"
        ]
        
        for variation in search_variations[:2]:  # Limit variations
            search_tasks.append(self._search_duckduckgo_async(variation, max_results // 4))
        
        # Execute searches in parallel
        results_lists = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        # Combine and deduplicate results
        combined_results = []
        seen_urls = set()
        
        for results in results_lists:
            if isinstance(results, list):
                for result in results:
                    url = result.get('url', '')
                    if url and url not in seen_urls:
                        combined_results.append(result)
                        seen_urls.add(url)
        
        return combined_results[:max_results]
    
    async def _search_duckduckgo_async(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Async DuckDuckGo search
        
        Args:
            query: Search query
            max_results: Maximum results
            
        Returns:
            Search results
        """
        if not DDGS_AVAILABLE:
            return self._mock_search_results(query, max_results)
        
        try:
            # Run DuckDuckGo search in thread pool since it's not async
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                self._run_ddgs_search,
                query,
                max_results
            )
            return results
        except Exception as e:
            self.logger.error(f"Async web search failed: {e}")
            return self._mock_search_results(query, max_results)
    
    def _run_ddgs_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Run DuckDuckGo search in executor"""
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
        except Exception:
            return []
    
    async def _process_search_results_parallel(self, search_results: List[Dict[str, Any]]) -> List[Source]:
        """
        Process search results in parallel
        
        Args:
            search_results: List of search results
            
        Returns:
            List of processed sources
        """
        semaphore = asyncio.Semaphore(self.max_concurrent_scrapes)
        tasks = []
        
        for result in search_results:
            tasks.append(self._process_single_result_async(result, semaphore))
        
        # Process results in parallel
        sources = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and None results
        valid_sources = []
        for source in sources:
            if isinstance(source, Source):
                valid_sources.append(source)
            elif isinstance(source, Exception):
                self.logger.warning(f"Source processing failed: {source}")
        
        return valid_sources
    
    async def _process_single_result_async(self, result: Dict[str, Any], semaphore: asyncio.Semaphore) -> Optional[Source]:
        """
        Process single search result asynchronously
        
        Args:
            result: Search result
            semaphore: Concurrency control
            
        Returns:
            Processed source or None
        """
        async with semaphore:
            try:
                source = Source(
                    title=result.get('title', ''),
                    url=result.get('url', ''),
                    snippet=result.get('snippet', ''),
                    citation=self._generate_citation(result)
                )
                
                # Extract content if webscraper is available
                if self.webscraper_agent:
                    try:
                        content_data = await self._scrape_content_async(result.get('url', ''))
                        source.content = content_data.get('text', '')[:5000]
                    except Exception as e:
                        self.logger.warning(f"Failed to scrape {result.get('url', '')}: {e}")
                
                # Calculate relevance score
                source.relevance_score = len(source.snippet) / 1000.0
                
                return source
                
            except Exception as e:
                self.logger.error(f"Failed to process search result: {e}")
                return None
    
    async def _scrape_content_async(self, url: str) -> Dict[str, Any]:
        """
        Scrape content asynchronously
        
        Args:
            url: URL to scrape
            
        Returns:
            Scraped content
        """
        if self.webscraper_agent and hasattr(self.webscraper_agent, 'scrape_url_async'):
            return await self.webscraper_agent.scrape_url_async(url)
        elif self.webscraper_agent:
            # Fall back to sync scraping
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                self.webscraper_agent.scrape_url,
                url
            )
        else:
            # Simple HTTP request if no webscraper
            return await self._simple_http_scrape(url)
    
    async def _simple_http_scrape(self, url: str) -> Dict[str, Any]:
        """
        Simple HTTP scraping fallback
        
        Args:
            url: URL to scrape
            
        Returns:
            Basic scraped content
        """
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        # Basic text extraction
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(content, 'html.parser')
                        text = soup.get_text()
                        return {'text': text[:5000], 'success': True}
        except Exception as e:
            self.logger.warning(f"Simple HTTP scrape failed for {url}: {e}")
        
        return {'text': '', 'success': False}
    
    async def _generate_summary_async(self, query: str, sources: List[Source]) -> str:
        """
        Generate summary using async LLM calls
        
        Args:
            query: Original query
            sources: List of sources
            
        Returns:
            Research summary
        """
        # Prepare context for LLM
        context = f"Research Query: {query}\n\n"
        context += "Sources:\n"
        
        for i, source in enumerate(sources[:5], 1):
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
        
        # Use async LLM generation if available
        if hasattr(self.llm, 'generate_response_async'):
            return await self.llm.generate_response_async(prompt, max_tokens=1000)
        else:
            # Fall back to sync
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                lambda: self.llm.generate_response(prompt, max_tokens=1000)
            )
    
    async def _perform_batch_research(self, task: AsyncAgentTask) -> List[ResearchResult]:
        """
        Perform research on multiple queries in parallel
        
        Args:
            task: Batch research task
            
        Returns:
            List of research results
        """
        queries = task.parameters.get("queries", [])
        max_results_per_query = task.parameters.get("max_results_per_query", 5)
        
        if not queries:
            raise ValueError("Queries parameter is required for batch research")
        
        self.logger.info(f"Starting batch research on {len(queries)} queries")
        
        # Create individual research tasks
        research_tasks = []
        for query in queries:
            research_task = AsyncAgentTask(
                task_id=f"batch_{query}",
                description=f"Research: {query}",
                parameters={
                    "type": "research",
                    "query": query,
                    "max_results": max_results_per_query
                }
            )
            research_tasks.append(self._perform_research_parallel(research_task))
        
        # Execute all research tasks in parallel
        results = await asyncio.gather(*research_tasks, return_exceptions=True)
        
        # Filter successful results
        successful_results = []
        for i, result in enumerate(results):
            if isinstance(result, ResearchResult):
                successful_results.append(result)
            else:
                self.logger.error(f"Batch research failed for query '{queries[i]}': {result}")
        
        return successful_results
    
    async def _perform_deep_research(self, task: AsyncAgentTask) -> ResearchResult:
        """
        Perform deep research with multiple analysis phases
        
        Args:
            task: Deep research task
            
        Returns:
            Enhanced research result
        """
        query = task.parameters.get("query", "")
        if not query:
            raise ValueError("Query parameter is required for deep research")
        
        self.logger.info(f"Starting deep research on: {query}")
        
        # Phase 1: Initial parallel research
        initial_result = await self._perform_research_parallel(task)
        
        # Phase 2: Follow-up research on key findings
        key_terms = await self._extract_key_terms(initial_result.summary)
        
        followup_tasks = []
        for term in key_terms[:3]:  # Limit follow-up queries
            followup_task = AsyncAgentTask(
                task_id=f"followup_{term}",
                description=f"Follow-up research: {term}",
                parameters={
                    "type": "research",
                    "query": f"{query} {term}",
                    "max_results": 5
                }
            )
            followup_tasks.append(self._perform_research_parallel(followup_task))
        
        # Execute follow-up research in parallel
        followup_results = await asyncio.gather(*followup_tasks, return_exceptions=True)
        
        # Combine results
        combined_sources = list(initial_result.sources)
        for result in followup_results:
            if isinstance(result, ResearchResult):
                combined_sources.extend(result.sources)
        
        # Generate enhanced summary
        enhanced_summary = await self._generate_enhanced_summary(query, combined_sources)
        
        # Create enhanced result
        enhanced_result = ResearchResult(
            query=query,
            sources=combined_sources,
            summary=enhanced_summary,
            citations=self._generate_citations([Source(**s) for s in combined_sources]),
            raw_data=initial_result.raw_data
        )
        
        return enhanced_result
    
    async def _extract_key_terms(self, summary: str) -> List[str]:
        """
        Extract key terms from summary for follow-up research
        
        Args:
            summary: Research summary
            
        Returns:
            List of key terms
        """
        # Simple keyword extraction - could be enhanced with NLP
        words = summary.split()
        
        # Filter for important words (simple heuristic)
        key_terms = []
        for word in words:
            if (len(word) > 5 and 
                word.isalpha() and 
                word not in ['research', 'analysis', 'information', 'sources', 'findings']):
                key_terms.append(word.lower())
        
        return list(set(key_terms))[:5]  # Return unique terms, max 5
    
    async def _generate_enhanced_summary(self, query: str, sources: List[Dict[str, Any]]) -> str:
        """
        Generate enhanced summary from multiple source sets
        
        Args:
            query: Original query
            sources: Combined sources from multiple research phases
            
        Returns:
            Enhanced summary
        """
        # Group sources by relevance
        high_relevance = [s for s in sources if s.get('relevance_score', 0) > 0.5]
        medium_relevance = [s for s in sources if 0.2 < s.get('relevance_score', 0) <= 0.5]
        
        context = f"Deep Research Query: {query}\n\n"
        context += "High Relevance Sources:\n"
        for i, source in enumerate(high_relevance[:5], 1):
            context += f"{i}. {source.get('title', '')}\n"
            context += f"   {source.get('snippet', '')}\n\n"
        
        context += "Supporting Sources:\n"
        for i, source in enumerate(medium_relevance[:3], 1):
            context += f"{i}. {source.get('title', '')}\n"
            context += f"   {source.get('snippet', '')}\n\n"
        
        prompt = f"""
        {context}
        
        Based on the comprehensive research above, provide an in-depth analysis of: {query}
        
        The analysis should:
        1. Synthesize information from high-relevance sources
        2. Support findings with evidence from multiple sources
        3. Identify key themes and patterns
        4. Provide actionable insights
        5. Highlight areas for further investigation
        
        Enhanced Analysis:
        """
        
        # Generate enhanced summary
        if hasattr(self.llm, 'generate_response_async'):
            return await self.llm.generate_response_async(prompt, max_tokens=1500)
        else:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                lambda: self.llm.generate_response(prompt, max_tokens=1500)
            )
    
    def _mock_search_results(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock search results for testing"""
        results = []
        for i in range(min(max_results, 5)):
            results.append({
                'title': f'Async Mock Result {i+1} for {query}',
                'url': f'https://example.com/async-result{i+1}',
                'snippet': f'This is an async mock search result snippet for {query}. It contains relevant information.',
                'published': datetime.now().isoformat()
            })
        return results
    
    def _generate_citation(self, result: Dict[str, Any]) -> str:
        """Generate citation from search result"""
        title = result.get('title', 'Unknown Title')
        url = result.get('url', '')
        published = result.get('published', '')
        
        if published:
            return f"{title}. {published}. Retrieved from {url}"
        else:
            return f"{title}. Retrieved from {url}"
    
    def _generate_citations(self, sources: List[Source]) -> List[str]:
        """Generate citations for sources"""
        citations = []
        for i, source in enumerate(sources, 1):
            citation = f"[{i}] {source.title}. Retrieved from {source.url}"
            citations.append(citation)
        return citations
    
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
    
    def set_webscraper_agent(self, webscraper_agent):
        """Set webscraper agent for content extraction"""
        self.webscraper_agent = webscraper_agent
    
    async def research_topic_async(self, query: str, max_results: int = 10, deep_research: bool = False) -> ResearchResult:
        """
        Convenience method for async research
        
        Args:
            query: Research query
            max_results: Maximum results to return
            deep_research: Whether to perform deep research
            
        Returns:
            Research result
        """
        task_type = "deep_research" if deep_research else "research"
        task_id = await self.create_task_async(
            f"Research: {query}",
            {
                "type": task_type,
                "query": query,
                "max_results": max_results
            }
        )
        
        return await self.wait_for_task(task_id)