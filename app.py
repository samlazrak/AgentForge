"""
Agent Creator - Main Application Interface

A comprehensive Streamlit application showcasing the Research Agent and Webscraper Agent
with MLX integration for advanced AI-powered research and web scraping capabilities.
"""

import streamlit as st
import os
import time
import json
from datetime import datetime
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Import our agents
try:
    from agent_creator import ResearchAgent, WebscraperAgent, LLMInterface
    from agent_creator.core.base_agent import AgentConfig
    from agent_creator.agents.webscraper_agent import ScrapingConfig
except ImportError as e:
    st.error(f"Error importing agent modules: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Agent Creator - AI Research & Web Scraping Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #1e3a8a, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .sub-header {
        font-size: 1.5rem;
        color: #374151;
        text-align: center;
        margin-bottom: 3rem;
    }
    
    .agent-card {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 2rem;
        border-radius: 1rem;
        border: 1px solid #e2e8f0;
        margin: 1rem 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .feature-box {
        background: #f1f5f9;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3b82f6;
        margin: 0.5rem 0;
    }
    
    .status-success {
        background: #dcfce7;
        color: #166534;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        border: 1px solid #bbf7d0;
    }
    
    .status-error {
        background: #fef2f2;
        color: #dc2626;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        border: 1px solid #fecaca;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e5e7eb;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'research_agent' not in st.session_state:
    st.session_state.research_agent = None
if 'webscraper_agent' not in st.session_state:
    st.session_state.webscraper_agent = None
if 'research_results' not in st.session_state:
    st.session_state.research_results = []
if 'scraping_results' not in st.session_state:
    st.session_state.scraping_results = []

def initialize_agents():
    """Initialize the research and webscraper agents"""
    try:
        # Initialize Research Agent
        research_config = AgentConfig(
            name="StreamlitResearchAgent",
            description="AI-powered research agent for comprehensive online research",
            capabilities=[
                "web_search", "content_analysis", "citation_generation",
                "pdf_generation", "notebook_generation"
            ]
        )
        st.session_state.research_agent = ResearchAgent(research_config)
        
        # Initialize Webscraper Agent
        webscraper_config = AgentConfig(
            name="StreamlitWebscraperAgent", 
            description="Advanced web scraping agent for content extraction",
            capabilities=[
                "url_scraping", "content_extraction", "link_extraction",
                "image_extraction", "metadata_extraction", "batch_scraping"
            ]
        )
        scraping_config = ScrapingConfig(
            timeout=30,
            delay_between_requests=1.0,
            max_content_length=2000000  # 2MB
        )
        st.session_state.webscraper_agent = WebscraperAgent(webscraper_config, scraping_config)
        
        # Connect webscraper to research agent
        st.session_state.research_agent.set_webscraper_agent(st.session_state.webscraper_agent)
        
        # Start agents
        st.session_state.research_agent.start()
        st.session_state.webscraper_agent.start()
        
        return True
    except Exception as e:
        st.error(f"Error initializing agents: {e}")
        return False

def main():
    """Main application interface"""
    
    # Header
    st.markdown('<h1 class="main-header">🤖 Agent Creator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Powered Research & Web Scraping Platform with MLX Integration</p>', 
                unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🛠️ Agent Control Panel")
        
        # Agent initialization
        if st.button("🚀 Initialize Agents", type="primary"):
            with st.spinner("Initializing AI agents..."):
                if initialize_agents():
                    st.success("✅ Agents initialized successfully!")
                else:
                    st.error("❌ Failed to initialize agents")
        
        # Agent status
        st.markdown("### Agent Status")
        if st.session_state.research_agent:
            st.markdown('<div class="status-success">🔬 Research Agent: Online</div>', 
                       unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-error">🔬 Research Agent: Offline</div>', 
                       unsafe_allow_html=True)
            
        if st.session_state.webscraper_agent:
            st.markdown('<div class="status-success">🕷️ Webscraper Agent: Online</div>', 
                       unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-error">🕷️ Webscraper Agent: Offline</div>', 
                       unsafe_allow_html=True)
        
        # Statistics
        st.markdown("### 📊 Statistics")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Research Tasks", len(st.session_state.research_results))
        with col2:
            st.metric("Scraping Tasks", len(st.session_state.scraping_results))
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔬 Research Agent", "🕷️ Webscraper Agent", 
        "📊 Results & Analytics", "📖 Documentation"
    ])
    
    with tab1:
        research_agent_interface()
    
    with tab2:
        webscraper_agent_interface()
    
    with tab3:
        results_analytics()
    
    with tab4:
        documentation_interface()

def research_agent_interface():
    """Interface for the Research Agent"""
    st.markdown("## 🔬 AI Research Agent")
    st.markdown("Perform comprehensive online research with AI-powered analysis and report generation.")
    
    if not st.session_state.research_agent:
        st.warning("⚠️ Please initialize the agents first using the sidebar.")
        return
    
    # Research configuration
    with st.expander("🔧 Research Configuration", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            max_results = st.slider("Maximum search results", 5, 20, 10)
            generate_pdf = st.checkbox("Generate PDF report", value=True)
        with col2:
            generate_notebook = st.checkbox("Generate Jupyter notebook", value=True)
            use_webscraper = st.checkbox("Enhanced content extraction", value=True, 
                                       help="Use webscraper agent for deeper content analysis")
    
    # Research query input
    st.markdown("### 📝 Research Query")
    query = st.text_area(
        "Enter your research topic or question:",
        placeholder="e.g., 'Latest developments in artificial intelligence and machine learning'",
        height=100
    )
    
    # Research execution
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        if st.button("🚀 Start Research", type="primary", disabled=not query.strip()):
            execute_research(query, max_results, generate_pdf, generate_notebook, use_webscraper)
    
    with col2:
        if st.button("📋 Example Query"):
            st.session_state.example_query = "Recent advances in quantum computing and their applications"
            st.rerun()
    
    # Set example query if button was clicked
    if hasattr(st.session_state, 'example_query'):
        query = st.session_state.example_query
        delattr(st.session_state, 'example_query')
        st.rerun()
    
    # Display recent research results
    if st.session_state.research_results:
        st.markdown("### 📄 Recent Research Results")
        for i, result in enumerate(reversed(st.session_state.research_results[-3:])):
            with st.expander(f"🔍 {result['query'][:50]}... ({result['timestamp']})"):
                display_research_result(result)

def execute_research(query: str, max_results: int, generate_pdf: bool, 
                    generate_notebook: bool, use_webscraper: bool):
    """Execute research with the research agent"""
    try:
        with st.spinner("🔍 Conducting research..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Start research
            status_text.text("Searching for relevant sources...")
            progress_bar.progress(25)
            
            result = st.session_state.research_agent.research_topic(
                query=query,
                max_results=max_results,
                generate_pdf=generate_pdf,
                generate_notebook=generate_notebook
            )
            
            progress_bar.progress(75)
            status_text.text("Generating reports...")
            
            # Store result
            research_data = {
                'query': query,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'result': result,
                'config': {
                    'max_results': max_results,
                    'generate_pdf': generate_pdf,
                    'generate_notebook': generate_notebook,
                    'use_webscraper': use_webscraper
                }
            }
            st.session_state.research_results.append(research_data)
            
            progress_bar.progress(100)
            status_text.text("✅ Research completed!")
            
            # Display results
            st.success("🎉 Research completed successfully!")
            display_research_result(research_data)
            
    except Exception as e:
        st.error(f"❌ Research failed: {str(e)}")

def webscraper_agent_interface():
    """Interface for the Webscraper Agent"""
    st.markdown("## 🕷️ Advanced Web Scraper")
    st.markdown("Extract content, links, and metadata from web pages with intelligent parsing.")
    
    if not st.session_state.webscraper_agent:
        st.warning("⚠️ Please initialize the agents first using the sidebar.")
        return
    
    # Scraping mode selection
    mode = st.radio(
        "Select scraping mode:",
        ["Single URL", "Multiple URLs", "Link Extraction"],
        horizontal=True
    )
    
    # Scraping configuration
    with st.expander("🔧 Scraping Configuration", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            use_selenium = st.checkbox("Use Selenium (for dynamic content)", value=False)
            extract_links = st.checkbox("Extract links", value=True)
        with col2:
            extract_images = st.checkbox("Extract images", value=True)
            timeout = st.slider("Timeout (seconds)", 10, 60, 30)
    
    if mode == "Single URL":
        single_url_interface()
    elif mode == "Multiple URLs":
        multiple_urls_interface()
    else:
        link_extraction_interface()

def single_url_interface():
    """Interface for single URL scraping"""
    st.markdown("### 🌐 Single URL Scraping")
    url = st.text_input(
        "Enter URL to scrape:",
        placeholder="https://example.com",
        help="Enter a valid URL to extract content from"
    )
    
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("🕷️ Scrape URL", type="primary", disabled=not url.strip()):
            execute_single_scraping(url)
    with col2:
        if st.button("📋 Example URL"):
            st.session_state.example_url = "https://news.ycombinator.com"
            st.rerun()

def multiple_urls_interface():
    """Interface for multiple URLs scraping"""
    st.markdown("### 🌐 Multiple URLs Scraping")
    urls_text = st.text_area(
        "Enter URLs (one per line):",
        placeholder="https://example1.com\nhttps://example2.com\nhttps://example3.com",
        height=120
    )
    
    if st.button("🕷️ Scrape All URLs", type="primary", disabled=not urls_text.strip()):
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        execute_multiple_scraping(urls)

def link_extraction_interface():
    """Interface for link extraction"""
    st.markdown("### 🔗 Link Extraction")
    url = st.text_input(
        "Enter URL to extract links from:",
        placeholder="https://example.com"
    )
    
    if st.button("🔗 Extract Links", type="primary", disabled=not url.strip()):
        execute_link_extraction(url)

def execute_single_scraping(url: str):
    """Execute single URL scraping"""
    try:
        with st.spinner(f"🕷️ Scraping {url}..."):
            result = st.session_state.webscraper_agent.scrape_url(url)
            
            # Store result
            scraping_data = {
                'type': 'single_url',
                'url': url,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'result': result
            }
            st.session_state.scraping_results.append(scraping_data)
            
            # Display results
            if result.success:
                st.success("✅ Scraping completed successfully!")
                display_scraping_result(result)
            else:
                st.error(f"❌ Scraping failed: {result.error}")
                
    except Exception as e:
        st.error(f"❌ Scraping failed: {str(e)}")

def execute_multiple_scraping(urls: List[str]):
    """Execute multiple URLs scraping"""
    try:
        with st.spinner(f"🕷️ Scraping {len(urls)} URLs..."):
            progress_bar = st.progress(0)
            
            results = st.session_state.webscraper_agent.scrape_multiple_urls(urls)
            
            # Store results
            scraping_data = {
                'type': 'multiple_urls',
                'urls': urls,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'results': results
            }
            st.session_state.scraping_results.append(scraping_data)
            
            progress_bar.progress(100)
            st.success(f"✅ Scraped {len(results)} URLs successfully!")
            
            # Display summary
            successful = sum(1 for r in results if r.success)
            st.info(f"📊 Summary: {successful}/{len(results)} URLs scraped successfully")
            
            # Display individual results
            for i, result in enumerate(results):
                with st.expander(f"Result {i+1}: {result.url}"):
                    display_scraping_result(result)
                    
    except Exception as e:
        st.error(f"❌ Multiple scraping failed: {str(e)}")

def execute_link_extraction(url: str):
    """Execute link extraction"""
    try:
        with st.spinner(f"🔗 Extracting links from {url}..."):
            links = st.session_state.webscraper_agent.extract_links(url)
            
            st.success(f"✅ Extracted {len(links)} links!")
            
            # Display links
            if links:
                st.markdown("### 🔗 Extracted Links")
                for i, link in enumerate(links, 1):
                    st.markdown(f"{i}. [{link}]({link})")
            else:
                st.info("No links found on this page.")
                
    except Exception as e:
        st.error(f"❌ Link extraction failed: {str(e)}")

def display_research_result(research_data: Dict[str, Any]):
    """Display research result in a formatted way"""
    result = research_data['result']
    research_result = result['research_result']
    
    # Summary
    st.markdown("#### 📋 Research Summary")
    st.write(research_result.summary)
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Sources Found", len(research_result.sources))
    with col2:
        st.metric("Citations", len(research_result.citations))
    with col3:
        st.metric("Files Generated", len(result['files_generated']))
    
    # Sources
    if research_result.sources:
        st.markdown("#### 📚 Sources")
        for i, source in enumerate(research_result.sources[:5], 1):
            with st.expander(f"Source {i}: {source['title']}"):
                st.markdown(f"**URL:** [{source['url']}]({source['url']})")
                st.markdown(f"**Relevance Score:** {source['relevance_score']:.2f}")
                st.markdown(f"**Snippet:** {source['snippet']}")
    
    # Generated files
    if result['files_generated']:
        st.markdown("#### 📁 Generated Files")
        for file_path in result['files_generated']:
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    st.download_button(
                        label=f"📥 Download {os.path.basename(file_path)}",
                        data=f.read(),
                        file_name=os.path.basename(file_path),
                        mime="application/octet-stream"
                    )

def display_scraping_result(result):
    """Display scraping result in a formatted way"""
    if result.success:
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Response Time", f"{result.response_time:.2f}s")
        with col2:
            st.metric("Content Length", len(result.text))
        with col3:
            st.metric("Links Found", len(result.links))
        with col4:
            st.metric("Images Found", len(result.images))
        
        # Content preview
        if result.title:
            st.markdown(f"**Title:** {result.title}")
        
        if result.text:
            st.markdown("**Content Preview:**")
            st.text_area("", result.text[:500] + "..." if len(result.text) > 500 else result.text, 
                        height=150, disabled=True)
        
        # Links and images
        col1, col2 = st.columns(2)
        with col1:
            if result.links:
                st.markdown("**Links:**")
                for link in result.links[:10]:
                    st.markdown(f"- [{link}]({link})")
                if len(result.links) > 10:
                    st.markdown(f"... and {len(result.links) - 10} more links")
        
        with col2:
            if result.images:
                st.markdown("**Images:**")
                for img in result.images[:5]:
                    st.markdown(f"- [{img}]({img})")
                if len(result.images) > 5:
                    st.markdown(f"... and {len(result.images) - 5} more images")
    else:
        st.error(f"Scraping failed: {result.error}")

def results_analytics():
    """Display results and analytics"""
    st.markdown("## 📊 Results & Analytics")
    
    if not st.session_state.research_results and not st.session_state.scraping_results:
        st.info("No results yet. Start by running some research or scraping tasks!")
        return
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Research Tasks", len(st.session_state.research_results))
    with col2:
        st.metric("Total Scraping Tasks", len(st.session_state.scraping_results))
    with col3:
        total_sources = sum(len(r['result']['research_result'].sources) 
                          for r in st.session_state.research_results)
        st.metric("Sources Analyzed", total_sources)
    with col4:
        total_urls = sum(len(r.get('urls', [r.get('url', '')])) 
                        for r in st.session_state.scraping_results)
        st.metric("URLs Scraped", total_urls)
    
    # Recent activity
    st.markdown("### 📈 Recent Activity")
    
    # Research results
    if st.session_state.research_results:
        st.markdown("#### 🔬 Research Tasks")
        for result in reversed(st.session_state.research_results):
            with st.expander(f"📄 {result['query'][:50]}... ({result['timestamp']})"):
                display_research_result(result)
    
    # Scraping results  
    if st.session_state.scraping_results:
        st.markdown("#### 🕷️ Scraping Tasks")
        for result in reversed(st.session_state.scraping_results):
            with st.expander(f"🌐 {result['type']} ({result['timestamp']})"):
                if result['type'] == 'single_url':
                    display_scraping_result(result['result'])
                else:
                    st.json(result)

def documentation_interface():
    """Display documentation and help"""
    st.markdown("## 📖 Documentation")
    
    st.markdown("""
    ### 🤖 Agent Creator Platform
    
    Welcome to the Agent Creator platform! This application showcases two powerful AI agents:
    
    #### 🔬 Research Agent
    The Research Agent is your AI-powered research assistant that can:
    - **Web Search**: Perform comprehensive searches using DuckDuckGo
    - **Content Analysis**: Use MLX-powered language models for intelligent analysis
    - **Citation Generation**: Automatically generate proper citations
    - **Report Generation**: Create professional PDF reports and Jupyter notebooks
    - **Source Integration**: Combine webscraper agent for enhanced content extraction
    
    #### 🕷️ Webscraper Agent
    The Webscraper Agent specializes in web content extraction:
    - **Single/Multiple URL Scraping**: Extract content from one or many web pages
    - **Dynamic Content Support**: Use Selenium for JavaScript-heavy sites
    - **Link & Image Extraction**: Automatically discover linked resources
    - **Metadata Extraction**: Extract page metadata and SEO information
    - **Intelligent Parsing**: Clean and structure extracted content
    
    ### 🚀 Getting Started
    
    1. **Initialize Agents**: Use the sidebar to initialize both agents
    2. **Research**: Enter a research query in the Research Agent tab
    3. **Scrape**: Use the Webscraper Agent for targeted content extraction
    4. **Analyze**: View results and download generated reports
    
    ### 🔧 Technical Features
    
    - **MLX Integration**: Advanced language model processing using Apple's MLX framework
    - **Fallback Systems**: Graceful degradation when dependencies are unavailable
    - **Task Management**: Built-in task tracking and status monitoring
    - **File Generation**: Automatic PDF and Jupyter notebook creation
    - **Error Handling**: Comprehensive error handling and user feedback
    
    ### 📋 Example Use Cases
    
    - **Academic Research**: Comprehensive literature reviews and source compilation
    - **Market Research**: Competitive analysis and trend identification
    - **Content Analysis**: Website content extraction and analysis
    - **Data Collection**: Systematic web scraping for research purposes
    
    ### 🛠️ Configuration Options
    
    - **Search Results**: Control the number of sources to analyze
    - **Output Formats**: Choose between PDF reports and Jupyter notebooks
    - **Scraping Modes**: Select appropriate scraping methods for your needs
    - **Timeout Settings**: Adjust timeouts for different website types
    """)
    
    # System information
    with st.expander("🔍 System Information"):
        st.markdown("### 🖥️ System Status")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Agent Status:**")
            st.write(f"Research Agent: {'✅ Online' if st.session_state.research_agent else '❌ Offline'}")
            st.write(f"Webscraper Agent: {'✅ Online' if st.session_state.webscraper_agent else '❌ Offline'}")
        
        with col2:
            st.markdown("**Dependencies:**")
            try:
                import mlx
                st.write("✅ MLX Framework")
            except ImportError:
                st.write("❌ MLX Framework")
            
            try:
                import selenium
                st.write("✅ Selenium WebDriver")
            except ImportError:
                st.write("❌ Selenium WebDriver")

if __name__ == "__main__":
    main()