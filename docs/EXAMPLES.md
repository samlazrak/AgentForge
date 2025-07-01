# 🎯 Agent Creator Examples

This document provides comprehensive examples and tutorials for using Agent Creator effectively.

## 🚀 Quick Start Examples

### 1. Simple Research Query

```python
from agent_creator import ResearchAgent

# Initialize and start agent
agent = ResearchAgent()
agent.start()

# Perform basic research
result = agent.research_topic(
    query="What are the latest developments in renewable energy?",
    max_results=5
)

# Print summary
print("Research Summary:")
print(result['research_result'].summary)

# List sources
print(f"\nFound {len(result['research_result'].sources)} sources:")
for i, source in enumerate(result['research_result'].sources, 1):
    print(f"{i}. {source['title']}")
    print(f"   URL: {source['url']}")

agent.stop()
```

### 2. Basic Web Scraping

```python
from agent_creator import WebscraperAgent

# Initialize agent
agent = WebscraperAgent()
agent.start()

# Scrape a news website
result = agent.scrape_url("https://news.ycombinator.com")

if result.success:
    print(f"Page Title: {result.title}")
    print(f"Content Length: {len(result.text)} characters")
    print(f"Links Found: {len(result.links)}")
    print(f"Images Found: {len(result.images)}")
    print(f"Response Time: {result.response_time:.2f} seconds")
else:
    print(f"Scraping failed: {result.error}")

agent.stop()
```

## 🎓 Advanced Examples

### 3. Research with Custom Configuration

```python
from agent_creator import ResearchAgent
from agent_creator.core.base_agent import AgentConfig
from agent_creator.utils.llm_interface import LLMConfig

# Configure custom LLM
llm_config = LLMConfig(
    model_name="microsoft/DialoGPT-large",
    max_tokens=1024,
    temperature=0.7,
    top_p=0.9
)

# Configure research agent
agent_config = AgentConfig(
    name="AdvancedResearchAgent",
    description="High-performance research agent",
    capabilities=[
        "web_search", "content_analysis", 
        "citation_generation", "pdf_generation"
    ],
    llm_config=llm_config,
    max_retries=5,
    timeout=60
)

# Initialize with custom config
agent = ResearchAgent(agent_config)
agent.start()

# Perform detailed research
result = agent.research_topic(
    query="Impact of artificial intelligence on healthcare diagnostics",
    max_results=15,
    generate_pdf=True,
    generate_notebook=True
)

# Access detailed results
research_result = result['research_result']
print(f"Research completed on: {research_result.timestamp}")
print(f"Query: {research_result.query}")
print(f"Summary length: {len(research_result.summary)} characters")
print(f"Sources analyzed: {len(research_result.sources)}")
print(f"Citations generated: {len(research_result.citations)}")

# Check generated files
if result['files_generated']:
    print("\nGenerated files:")
    for file_path in result['files_generated']:
        print(f"- {file_path}")

agent.stop()
```

### 4. Advanced Web Scraping with Selenium

```python
from agent_creator import WebscraperAgent
from agent_creator.agents.webscraper_agent import ScrapingConfig

# Configure for JavaScript-heavy sites
scraping_config = ScrapingConfig(
    timeout=60,
    max_retries=3,
    delay_between_requests=2.0,
    use_selenium=True,
    headless=True,
    extract_links=True,
    extract_images=True,
    max_content_length=2000000  # 2MB
)

agent = WebscraperAgent(scraping_config=scraping_config)
agent.start()

# Scrape dynamic content
dynamic_sites = [
    "https://react-app-example.com",
    "https://spa-application.com",
    "https://dynamic-content-site.com"
]

results = agent.scrape_multiple_urls(dynamic_sites, use_selenium=True)

print(f"Scraped {len(results)} sites:")
for result in results:
    if result.success:
        print(f"✅ {result.url}")
        print(f"   Title: {result.title}")
        print(f"   Content: {len(result.text)} chars")
        print(f"   Links: {len(result.links)}")
        print(f"   Time: {result.response_time:.2f}s")
    else:
        print(f"❌ {result.url}: {result.error}")

agent.stop()
```

### 5. Integrated Research with Web Scraping

```python
from agent_creator import ResearchAgent, WebscraperAgent
from agent_creator.agents.webscraper_agent import ScrapingConfig

# Configure webscraper for enhanced content extraction
scraping_config = ScrapingConfig(
    timeout=30,
    delay_between_requests=1.0,
    extract_links=True,
    max_content_length=1500000
)

# Initialize both agents
research_agent = ResearchAgent()
webscraper_agent = WebscraperAgent(scraping_config=scraping_config)

# Connect them for enhanced functionality
research_agent.set_webscraper_agent(webscraper_agent)

# Start both agents
research_agent.start()
webscraper_agent.start()

# Perform enhanced research
result = research_agent.research_topic(
    query="Machine learning trends in finance 2024",
    max_results=12,
    generate_pdf=True,
    generate_notebook=True
)

# The research agent will automatically use the webscraper
# to extract full content from relevant sources for deeper analysis

print("Enhanced Research Results:")
print(f"Sources with full content extraction: {len(result['research_result'].sources)}")

# Check which sources have enhanced content
for source in result['research_result'].sources:
    content_length = len(source.get('content', ''))
    print(f"- {source['title']}: {content_length} chars extracted")

# Stop both agents
research_agent.stop()
webscraper_agent.stop()
```

## 🔬 Specialized Use Cases

### 6. Academic Research Assistant

```python
from agent_creator import ResearchAgent
import os

def academic_research_pipeline(topic, num_sources=20):
    """Complete academic research pipeline"""
    
    agent = ResearchAgent()
    agent.start()
    
    try:
        # Perform comprehensive research
        result = agent.research_topic(
            query=f"Academic research on {topic} recent studies",
            max_results=num_sources,
            generate_pdf=True,
            generate_notebook=True
        )
        
        # Process results
        research_data = result['research_result']
        
        # Create academic-style report
        academic_summary = f"""
# Academic Research Report: {topic}

## Executive Summary
{research_data.summary}

## Methodology
- Search query: {research_data.query}
- Sources analyzed: {len(research_data.sources)}
- Research date: {research_data.timestamp.strftime('%Y-%m-%d')}

## Key Findings
[Generated from {len(research_data.sources)} academic and industry sources]

## Sources and Citations
"""
        
        # Add citations
        for i, citation in enumerate(research_data.citations, 1):
            academic_summary += f"{i}. {citation}\n"
        
        # Save academic report
        report_path = f"academic_report_{topic.replace(' ', '_')}.md"
        with open(report_path, 'w') as f:
            f.write(academic_summary)
        
        print(f"Academic research completed!")
        print(f"Report saved to: {report_path}")
        print(f"Additional files: {result['files_generated']}")
        
        return result
        
    finally:
        agent.stop()

# Usage
result = academic_research_pipeline(
    "quantum computing applications in cryptography"
)
```

### 7. News Monitoring System

```python
from agent_creator import WebscraperAgent
from datetime import datetime
import json

def news_monitoring_system(news_sites, keywords):
    """Monitor news sites for specific keywords"""
    
    agent = WebscraperAgent()
    agent.start()
    
    results = []
    
    try:
        # Scrape all news sites
        scraping_results = agent.scrape_multiple_urls(news_sites)
        
        for result in scraping_results:
            if result.success:
                # Check for keywords in content
                content_lower = result.text.lower()
                found_keywords = [kw for kw in keywords if kw.lower() in content_lower]
                
                if found_keywords:
                    news_item = {
                        'url': result.url,
                        'title': result.title,
                        'keywords_found': found_keywords,
                        'timestamp': result.timestamp.isoformat(),
                        'snippet': result.text[:300] + '...'
                    }
                    results.append(news_item)
        
        # Save monitoring results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"news_monitoring_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"News monitoring completed!")
        print(f"Found {len(results)} relevant articles")
        print(f"Report saved to: {report_file}")
        
        return results
        
    finally:
        agent.stop()

# Usage
news_sites = [
    "https://techcrunch.com",
    "https://arstechnica.com",
    "https://theverge.com"
]

keywords = ["artificial intelligence", "machine learning", "quantum computing"]

monitoring_results = news_monitoring_system(news_sites, keywords)
```

### 8. Competitive Analysis Tool

```python
from agent_creator import ResearchAgent, WebscraperAgent
import pandas as pd

def competitive_analysis(company_name, competitors):
    """Perform competitive analysis research"""
    
    # Initialize agents
    research_agent = ResearchAgent()
    webscraper_agent = WebscraperAgent()
    research_agent.set_webscraper_agent(webscraper_agent)
    
    research_agent.start()
    webscraper_agent.start()
    
    analysis_results = {}
    
    try:
        # Research main company
        main_result = research_agent.research_topic(
            query=f"{company_name} business strategy products services 2024",
            max_results=10
        )
        analysis_results[company_name] = main_result['research_result']
        
        # Research competitors
        for competitor in competitors:
            competitor_result = research_agent.research_topic(
                query=f"{competitor} business strategy products services 2024",
                max_results=8
            )
            analysis_results[competitor] = competitor_result['research_result']
        
        # Create comparison report
        comparison_data = []
        for company, research_data in analysis_results.items():
            comparison_data.append({
                'Company': company,
                'Sources_Count': len(research_data.sources),
                'Summary_Length': len(research_data.summary),
                'Research_Date': research_data.timestamp.strftime('%Y-%m-%d'),
                'Key_Points': research_data.summary[:200] + '...'
            })
        
        # Save as DataFrame
        df = pd.DataFrame(comparison_data)
        df.to_csv(f'competitive_analysis_{company_name.replace(" ", "_")}.csv', index=False)
        
        print("Competitive Analysis Results:")
        print(df[['Company', 'Sources_Count', 'Summary_Length']])
        
        return analysis_results
        
    finally:
        research_agent.stop()
        webscraper_agent.stop()

# Usage
analysis = competitive_analysis(
    company_name="OpenAI",
    competitors=["Anthropic", "Google DeepMind", "Microsoft AI"]
)
```

## 🛠️ Utility Functions and Helpers

### 9. Batch Processing Utilities

```python
from agent_creator import WebscraperAgent
from concurrent.futures import ThreadPoolExecutor
import time

class BatchProcessor:
    """Utility class for batch processing URLs"""
    
    def __init__(self, max_workers=5):
        self.max_workers = max_workers
        self.agent = WebscraperAgent()
    
    def process_urls_parallel(self, urls, use_selenium=False):
        """Process URLs in parallel"""
        self.agent.start()
        
        try:
            results = []
            batch_size = 10  # Process in batches
            
            for i in range(0, len(urls), batch_size):
                batch = urls[i:i + batch_size]
                print(f"Processing batch {i//batch_size + 1}: {len(batch)} URLs")
                
                batch_results = self.agent.scrape_multiple_urls(batch, use_selenium)
                results.extend(batch_results)
                
                # Respect rate limits
                if i + batch_size < len(urls):
                    time.sleep(2)
            
            return results
            
        finally:
            self.agent.stop()
    
    def analyze_results(self, results):
        """Analyze batch processing results"""
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        
        analysis = {
            'total_processed': len(results),
            'successful': len(successful),
            'failed': len(failed),
            'success_rate': len(successful) / len(results) * 100,
            'avg_response_time': sum(r.response_time for r in successful) / len(successful) if successful else 0,
            'avg_content_length': sum(len(r.text) for r in successful) / len(successful) if successful else 0
        }
        
        return analysis

# Usage
processor = BatchProcessor(max_workers=3)

urls = [
    "https://example1.com", "https://example2.com", 
    "https://example3.com", "https://example4.com"
]

results = processor.process_urls_parallel(urls)
analysis = processor.analyze_results(results)

print(f"Batch Processing Analysis:")
print(f"Success Rate: {analysis['success_rate']:.1f}%")
print(f"Average Response Time: {analysis['avg_response_time']:.2f}s")
print(f"Average Content Length: {analysis['avg_content_length']:.0f} chars")
```

### 10. Research Report Generator

```python
from agent_creator import ResearchAgent
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

class ReportGenerator:
    """Generate comprehensive research reports with visualizations"""
    
    def __init__(self):
        self.agent = ResearchAgent()
    
    def generate_comprehensive_report(self, topic, output_dir="reports"):
        """Generate a comprehensive research report"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        self.agent.start()
        
        try:
            # Perform research
            result = self.agent.research_topic(
                query=topic,
                max_results=15,
                generate_pdf=True,
                generate_notebook=True
            )
            
            research_data = result['research_result']
            
            # Generate visualizations
            self._create_source_analysis_chart(research_data, output_dir)
            self._create_timeline_chart(research_data, output_dir)
            
            # Create detailed markdown report
            report_path = os.path.join(output_dir, f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
            self._create_markdown_report(research_data, report_path)
            
            print(f"Comprehensive report generated in: {output_dir}")
            return output_dir
            
        finally:
            self.agent.stop()
    
    def _create_source_analysis_chart(self, research_data, output_dir):
        """Create visualization of source analysis"""
        if not research_data.sources:
            return
            
        # Extract relevance scores
        scores = [source.get('relevance_score', 0) for source in research_data.sources]
        titles = [source.get('title', '')[:30] + '...' for source in research_data.sources]
        
        plt.figure(figsize=(12, 8))
        plt.barh(range(len(scores)), scores)
        plt.yticks(range(len(titles)), titles)
        plt.xlabel('Relevance Score')
        plt.title('Source Relevance Analysis')
        plt.tight_layout()
        
        chart_path = os.path.join(output_dir, 'source_relevance.png')
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_timeline_chart(self, research_data, output_dir):
        """Create timeline visualization"""
        # This is a placeholder - in real implementation,
        # you would extract publication dates from sources
        pass
    
    def _create_markdown_report(self, research_data, report_path):
        """Create detailed markdown report"""
        report_content = f"""# Research Report: {research_data.query}

**Generated:** {research_data.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

{research_data.summary}

## Research Metrics

- **Sources Analyzed:** {len(research_data.sources)}
- **Citations Generated:** {len(research_data.citations)}
- **Research Date:** {research_data.timestamp.strftime('%Y-%m-%d')}

## Detailed Sources

"""
        
        for i, source in enumerate(research_data.sources, 1):
            report_content += f"""### Source {i}: {source.get('title', 'Unknown Title')}

**URL:** {source.get('url', 'Unknown URL')}
**Relevance Score:** {source.get('relevance_score', 0):.2f}

**Summary:** {source.get('snippet', 'No summary available')}

---

"""
        
        report_content += """## Citations

"""
        for citation in research_data.citations:
            report_content += f"- {citation}\n"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

# Usage
generator = ReportGenerator()
output_dir = generator.generate_comprehensive_report(
    "Sustainable energy technologies 2024"
)
```

## 🔧 Configuration Templates

### 11. Configuration Presets

```python
from agent_creator.core.base_agent import AgentConfig
from agent_creator.utils.llm_interface import LLMConfig
from agent_creator.agents.webscraper_agent import ScrapingConfig

class ConfigurationPresets:
    """Predefined configuration templates"""
    
    @staticmethod
    def academic_research_config():
        """Configuration optimized for academic research"""
        llm_config = LLMConfig(
            model_name="microsoft/DialoGPT-large",
            max_tokens=1024,
            temperature=0.3,  # Lower temperature for more focused results
            top_p=0.8
        )
        
        return AgentConfig(
            name="AcademicResearchAgent",
            description="Agent optimized for academic research",
            capabilities=[
                "web_search", "content_analysis", "citation_generation",
                "pdf_generation", "notebook_generation"
            ],
            llm_config=llm_config,
            max_retries=5,
            timeout=60
        )
    
    @staticmethod
    def news_monitoring_config():
        """Configuration optimized for news monitoring"""
        return ScrapingConfig(
            timeout=20,
            max_retries=3,
            delay_between_requests=0.5,
            use_selenium=False,
            extract_links=True,
            extract_images=False,
            max_content_length=500000  # 500KB for news articles
        )
    
    @staticmethod
    def comprehensive_research_config():
        """Configuration for comprehensive research tasks"""
        llm_config = LLMConfig(
            model_name="microsoft/DialoGPT-large",
            max_tokens=1536,
            temperature=0.7,
            top_p=0.9
        )
        
        return AgentConfig(
            name="ComprehensiveResearchAgent",
            description="Agent for detailed research tasks",
            capabilities=[
                "web_search", "content_analysis", "citation_generation",
                "pdf_generation", "notebook_generation"
            ],
            llm_config=llm_config,
            max_retries=3,
            timeout=90
        )

# Usage examples
academic_config = ConfigurationPresets.academic_research_config()
news_config = ConfigurationPresets.news_monitoring_config()
comprehensive_config = ConfigurationPresets.comprehensive_research_config()

# Use with agents
from agent_creator import ResearchAgent, WebscraperAgent

research_agent = ResearchAgent(academic_config)
webscraper_agent = WebscraperAgent(scraping_config=news_config)
```

## 📊 Performance Monitoring

### 12. Performance Tracking

```python
import time
import psutil
from datetime import datetime

class PerformanceMonitor:
    """Monitor agent performance and resource usage"""
    
    def __init__(self):
        self.start_time = None
        self.metrics = []
    
    def start_monitoring(self):
        """Start performance monitoring"""
        self.start_time = time.time()
        self.metrics = []
    
    def record_metric(self, operation, duration, memory_used=None):
        """Record performance metric"""
        if memory_used is None:
            memory_used = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        metric = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'duration': duration,
            'memory_mb': memory_used
        }
        self.metrics.append(metric)
    
    def get_performance_summary(self):
        """Get performance summary"""
        if not self.metrics:
            return None
        
        total_duration = sum(m['duration'] for m in self.metrics)
        avg_memory = sum(m['memory_mb'] for m in self.metrics) / len(self.metrics)
        
        return {
            'total_operations': len(self.metrics),
            'total_duration': total_duration,
            'average_duration': total_duration / len(self.metrics),
            'average_memory_mb': avg_memory,
            'operations_per_second': len(self.metrics) / total_duration if total_duration > 0 else 0
        }

# Usage with monitoring
from agent_creator import ResearchAgent

monitor = PerformanceMonitor()
agent = ResearchAgent()

monitor.start_monitoring()
agent.start()

start_time = time.time()
result = agent.research_topic("AI performance optimization")
operation_time = time.time() - start_time

monitor.record_metric("research_topic", operation_time)

agent.stop()

summary = monitor.get_performance_summary()
print(f"Performance Summary: {summary}")
```

---

These examples demonstrate the full range of capabilities available in Agent Creator. Start with the basic examples and gradually explore more advanced use cases as you become familiar with the framework.