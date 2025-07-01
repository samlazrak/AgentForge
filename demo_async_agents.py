#!/usr/bin/env python3
"""
Demo script for the new async agent infrastructure
Demonstrates:
1. Message-based agent communication
2. Async/parallel processing
3. Agent registry and discovery
"""

import asyncio
import logging
from typing import List

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the new infrastructure
from agent_creator.core.agent_bus import AgentBus, AgentEvent, EventType
from agent_creator.core.agent_registry import AgentRegistry, AgentCapability
from agent_creator.core.base_agent import AgentConfig
from agent_creator.agents.async_research_agent import AsyncResearchAgent
from agent_creator.agents.async_webscraper_agent import AsyncWebscraperAgent

async def demo_agent_bus():
    """Demonstrate agent bus communication"""
    logger.info("=== Agent Bus Demo ===")
    
    # Create agent bus
    bus = AgentBus()
    
    # Simple event handler
    async def event_handler(event):
        logger.info(f"Received event: {event.event_type} from {event.source_agent_id}")
    
    # Subscribe to events
    await bus.subscribe("demo_agent", [EventType.TASK_COMPLETED], event_handler)
    
    # Publish an event
    await bus.publish(AgentEvent(
        event_type=EventType.TASK_COMPLETED,
        source_agent_id="test_agent",
        payload={"result": "Demo task completed successfully"}
    ))
    
    # Get statistics
    stats = bus.get_statistics()
    logger.info(f"Bus stats: {stats}")

async def demo_agent_registry():
    """Demonstrate agent registry and discovery"""
    logger.info("=== Agent Registry Demo ===")
    
    # Create registry
    registry = AgentRegistry()
    
    # Create agents with custom capabilities
    research_config = AgentConfig(
        name="DemoResearchAgent",
        description="Research agent for demo",
        capabilities=["web_search", "content_analysis"]
    )
    
    webscraper_config = AgentConfig(
        name="DemoWebscraperAgent", 
        description="Webscraper agent for demo",
        capabilities=["url_scraping", "content_extraction"]
    )
    
    # Create async agents
    research_agent = AsyncResearchAgent(research_config)
    webscraper_agent = AsyncWebscraperAgent(webscraper_config)
    
    # Start agents
    await research_agent.start_async()
    await webscraper_agent.start_async()
    
    # Register agents with detailed capabilities
    research_capabilities = [
        AgentCapability(
            name="web_search",
            description="Search the web for information",
            input_types=["string"],
            output_types=["research_result"]
        ),
        AgentCapability(
            name="content_analysis",
            description="Analyze and summarize content",
            input_types=["text"],
            output_types=["summary"]
        )
    ]
    
    webscraper_capabilities = [
        AgentCapability(
            name="url_scraping",
            description="Extract content from URLs",
            input_types=["url"],
            output_types=["scraped_content"]
        )
    ]
    
    await registry.register_agent(research_agent, research_capabilities)
    await registry.register_agent(webscraper_agent, webscraper_capabilities)
    
    # Demonstrate discovery
    search_agents = registry.find_agents_by_capability("web_search")
    logger.info(f"Found {len(search_agents)} agents with web_search capability")
    
    scraping_agents = registry.find_agents_by_capability("url_scraping")
    logger.info(f"Found {len(scraping_agents)} agents with url_scraping capability")
    
    # List all capabilities
    capabilities = registry.list_capabilities()
    logger.info(f"Available capabilities: {capabilities}")
    
    # Get registry statistics
    stats = registry.get_registry_statistics()
    logger.info(f"Registry stats: {stats}")
    
    # Clean up
    await research_agent.stop_async()
    await webscraper_agent.stop_async()

async def demo_parallel_research():
    """Demonstrate parallel research capabilities"""
    logger.info("=== Parallel Research Demo ===")
    
    # Create async research agent
    config = AgentConfig(
        name="ParallelResearchAgent",
        description="Agent for parallel research demo",
        capabilities=["async_web_search", "parallel_content_analysis"]
    )
    
    agent = AsyncResearchAgent(config)
    await agent.start_async()
    
    try:
        # Demonstrate batch research
        queries = [
            "artificial intelligence trends 2024",
            "machine learning applications",
            "neural networks explained"
        ]
        
        logger.info(f"Starting batch research on {len(queries)} topics...")
        
        # Create batch research task
        task_id = await agent.create_task_async(
            "Batch Research Demo",
            {
                "type": "batch_research",
                "queries": queries,
                "max_results_per_query": 3
            }
        )
        
        # Wait for completion with timeout
        try:
            results = await agent.wait_for_task(task_id, timeout=60)
            logger.info(f"Batch research completed! Found {len(results)} results")
            
            for i, result in enumerate(results):
                logger.info(f"Query {i+1}: {result.query}")
                logger.info(f"  Sources: {len(result.sources)}")
                logger.info(f"  Summary length: {len(result.summary)} chars")
                
        except asyncio.TimeoutError:
            logger.warning("Batch research timed out")
    
    finally:
        await agent.stop_async()

async def demo_parallel_scraping():
    """Demonstrate parallel web scraping"""
    logger.info("=== Parallel Scraping Demo ===")
    
    # Create async webscraper agent
    config = AgentConfig(
        name="ParallelScraperAgent",
        description="Agent for parallel scraping demo",
        capabilities=["async_url_scraping", "parallel_batch_scraping"]
    )
    
    agent = AsyncWebscraperAgent(config)
    await agent.start_async()
    
    try:
        # Demo URLs (using mock-friendly URLs)
        urls = [
            "https://httpbin.org/html",
            "https://httpbin.org/json", 
            "https://httpbin.org/xml"
        ]
        
        logger.info(f"Starting parallel scraping of {len(urls)} URLs...")
        
        # Create parallel scraping task
        task_id = await agent.create_task_async(
            "Parallel Scraping Demo",
            {
                "type": "scrape_multiple",
                "urls": urls,
                "max_concurrent": 2
            }
        )
        
        # Wait for completion
        try:
            results = await agent.wait_for_task(task_id, timeout=30)
            logger.info(f"Parallel scraping completed! Processed {len(results)} URLs")
            
            for i, result in enumerate(results):
                logger.info(f"URL {i+1}: {result.url}")
                logger.info(f"  Success: {result.success}")
                logger.info(f"  Response time: {result.response_time:.2f}s")
                if result.error:
                    logger.info(f"  Error: {result.error}")
                    
        except asyncio.TimeoutError:
            logger.warning("Parallel scraping timed out")
    
    finally:
        await agent.stop_async()

async def demo_agent_integration():
    """Demonstrate integrated agent workflow"""
    logger.info("=== Agent Integration Demo ===")
    
    # Create both agents
    research_agent = AsyncResearchAgent()
    webscraper_agent = AsyncWebscraperAgent()
    
    # Start agents
    await research_agent.start_async()
    await webscraper_agent.start_async()
    
    try:
        # Set up agent integration
        research_agent.set_webscraper_agent(webscraper_agent)
        
        # Perform integrated research with content extraction
        logger.info("Starting integrated research with content extraction...")
        
        task_id = await research_agent.create_task_async(
            "Integrated Research Demo",
            {
                "type": "research",
                "query": "python async programming",
                "max_results": 3
            }
        )
        
        try:
            result = await research_agent.wait_for_task(task_id, timeout=45)
            logger.info(f"Integrated research completed!")
            logger.info(f"  Query: {result.query}")
            logger.info(f"  Sources found: {len(result.sources)}")
            logger.info(f"  Summary length: {len(result.summary)} chars")
            
            # Show first source details
            if result.sources:
                source = result.sources[0]
                logger.info(f"  First source: {source['title']}")
                logger.info(f"  Content length: {len(source.get('content', ''))} chars")
                
        except asyncio.TimeoutError:
            logger.warning("Integrated research timed out")
    
    finally:
        await research_agent.stop_async()
        await webscraper_agent.stop_async()

async def demo_task_management():
    """Demonstrate advanced task management"""
    logger.info("=== Task Management Demo ===")
    
    agent = AsyncResearchAgent()
    await agent.start_async()
    
    try:
        # Create multiple tasks with different priorities
        tasks = []
        
        # High priority task
        task1 = await agent.create_task_async(
            "High Priority Research",
            {
                "type": "research",
                "query": "urgent topic",
                "max_results": 2
            },
            priority=10
        )
        tasks.append(task1)
        
        # Medium priority task
        task2 = await agent.create_task_async(
            "Medium Priority Research", 
            {
                "type": "research",
                "query": "normal topic",
                "max_results": 2
            },
            priority=5
        )
        tasks.append(task2)
        
        # Low priority task
        task3 = await agent.create_task_async(
            "Low Priority Research",
            {
                "type": "research", 
                "query": "background topic",
                "max_results": 2
            },
            priority=1
        )
        tasks.append(task3)
        
        logger.info(f"Created {len(tasks)} tasks with different priorities")
        
        # Monitor task execution
        while True:
            running_tasks = agent.get_running_tasks()
            queue_size = agent.get_queue_size()
            
            logger.info(f"Running tasks: {len(running_tasks)}, Queue size: {queue_size}")
            
            if not running_tasks and queue_size == 0:
                break
                
            await asyncio.sleep(2)
        
        logger.info("All tasks completed!")
    
    finally:
        await agent.stop_async()

async def main():
    """Run all demos"""
    logger.info("Starting Agent Creator Infrastructure Demo")
    
    try:
        # Run demos in sequence
        await demo_agent_bus()
        await asyncio.sleep(1)
        
        await demo_agent_registry()
        await asyncio.sleep(1)
        
        await demo_parallel_research()
        await asyncio.sleep(1)
        
        await demo_parallel_scraping()
        await asyncio.sleep(1)
        
        await demo_agent_integration()
        await asyncio.sleep(1)
        
        await demo_task_management()
        
        logger.info("All demos completed successfully!")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        raise

if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())