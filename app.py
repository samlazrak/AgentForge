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
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)

# Import our agents
try:
    from agent_creator import ResearchAgent, WebscraperAgent, DataAnalysisAgent, DeepResearcherAgent, LLMInterface
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
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Root variables for consistent theming */
    :root {
        --primary-color: #6366f1;
        --primary-hover: #5856e4;
        --secondary-color: #06b6d4;
        --accent-color: #f59e0b;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --error-color: #ef4444;
        --background-primary: #1e293b;
        --background-secondary: #334155;
        --background-tertiary: #475569;
        --background-card: #2d3748;
        --background-soft: #374151;
        --text-primary: #f1f5f9;
        --text-secondary: #cbd5e1;
        --border-color: #475569;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.2);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.2);
        --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --gradient-secondary: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
        --gradient-accent: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    
    /* Global styles */
    .main > div {
        padding: 2rem 1rem;
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--background-tertiary);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--primary-color);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary-hover);
    }
    
    /* Main header styling */
    .main-header {
        font-size: clamp(2.5rem, 5vw, 4rem);
        font-weight: 700;
        color: transparent;
        text-align: center;
        margin: 0 0 1rem 0;
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.025em;
        line-height: 1.1;
        position: relative;
    }
    
    .main-header::after {
        content: '';
        position: absolute;
        bottom: -10px;
        left: 50%;
        transform: translateX(-50%);
        width: 100px;
        height: 4px;
        background: var(--gradient-secondary);
        border-radius: 2px;
    }
    
    .sub-header {
        font-size: 1.25rem;
        color: var(--text-secondary);
        text-align: center;
        margin-bottom: 3rem;
        font-weight: 400;
        line-height: 1.6;
    }
    
         /* Enhanced sidebar styling */
     .css-1d391kg {
         background: linear-gradient(180deg, #1e293b 0%, #334155 100%);
         border-right: 1px solid var(--border-color);
     }
     
     .sidebar .sidebar-content {
         padding: 2rem 1rem;
     }
    
         /* Card components */
     .agent-card {
         background: var(--background-card);
         padding: 2rem;
         border-radius: 16px;
         border: 1px solid var(--border-color);
         margin: 1rem 0;
         box-shadow: var(--shadow-lg);
         transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
         position: relative;
         overflow: hidden;
     }
    
    .agent-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--gradient-primary);
    }
    
    .agent-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-xl);
        border-color: var(--primary-color);
    }
    
    /* Feature boxes */
    .feature-box {
        background: var(--background-secondary);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid var(--primary-color);
        margin: 1rem 0;
        transition: all 0.3s ease;
        position: relative;
    }
    
         .feature-box:hover {
         background: var(--background-card);
         box-shadow: var(--shadow-md);
         transform: translateX(4px);
     }
    
    /* Status indicators */
    .status-success {
        background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
        color: var(--success-color);
        padding: 0.75rem 1rem;
        border-radius: 8px;
        border: 1px solid #bbf7d0;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin: 0.5rem 0;
        box-shadow: var(--shadow-sm);
    }
    
    .status-error {
        background: linear-gradient(135deg, #fef2f2 0%, #fecaca 100%);
        color: var(--error-color);
        padding: 0.75rem 1rem;
        border-radius: 8px;
        border: 1px solid #fecaca;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin: 0.5rem 0;
        box-shadow: var(--shadow-sm);
    }
    
         /* Metric cards */
     .metric-card {
         background: var(--background-card);
         padding: 1.5rem;
         border-radius: 12px;
         border: 1px solid var(--border-color);
         text-align: center;
         box-shadow: var(--shadow-md);
         transition: all 0.3s ease;
         position: relative;
         overflow: hidden;
     }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--gradient-secondary);
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }
    
    /* Enhanced buttons */
    .stButton > button {
        background: var(--gradient-primary) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: var(--shadow-md) !important;
        letter-spacing: 0.025em !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-lg) !important;
        background: var(--gradient-accent) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Enhanced inputs */
         .stTextInput > div > div > input {
         border: 2px solid var(--border-color) !important;
         border-radius: 8px !important;
         padding: 0.75rem !important;
         font-family: 'Inter', sans-serif !important;
         transition: all 0.3s ease !important;
         background: var(--background-card) !important;
     }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
        outline: none !important;
    }
    
         .stTextArea > div > div > textarea {
         border: 2px solid var(--border-color) !important;
         border-radius: 8px !important;
         padding: 0.75rem !important;
         font-family: 'Inter', sans-serif !important;
         transition: all 0.3s ease !important;
         background: var(--background-card) !important;
     }
    
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
        outline: none !important;
    }
    
    /* Enhanced tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: var(--background-secondary);
        padding: 0.5rem;
        border-radius: 12px;
        border: 1px solid var(--border-color);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        white-space: pre-wrap;
        background: transparent;
        border-radius: 8px;
        color: var(--text-secondary);
        font-weight: 500;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
        border: none;
    }
    
         .stTabs [aria-selected="true"] {
         background: var(--background-card) !important;
         color: var(--primary-color) !important;
         box-shadow: var(--shadow-sm);
     }
    
    /* Enhanced expanders */
    .streamlit-expanderHeader {
        background: var(--background-secondary) !important;
        border-radius: 8px !important;
        border: 1px solid var(--border-color) !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
         .streamlit-expanderHeader:hover {
         background: var(--background-card) !important;
         box-shadow: var(--shadow-sm) !important;
     }
    
         .streamlit-expanderContent {
         background: var(--background-card) !important;
         border: 1px solid var(--border-color) !important;
         border-top: none !important;
         border-radius: 0 0 8px 8px !important;
     }
    
         /* Enhanced metrics */
     [data-testid="metric-container"] {
         background: var(--background-card);
         border: 1px solid var(--border-color);
         padding: 1rem;
         border-radius: 8px;
         box-shadow: var(--shadow-sm);
         transition: all 0.3s ease;
     }
    
    [data-testid="metric-container"]:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-1px);
    }
    
    /* Enhanced progress bars */
    .stProgress > div > div > div > div {
        background: var(--gradient-primary) !important;
        border-radius: 4px !important;
    }
    
    /* Success/error messages */
    .stSuccess {
        background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%) !important;
        border: 1px solid #bbf7d0 !important;
        border-radius: 8px !important;
        color: var(--success-color) !important;
    }
    
    .stError {
        background: linear-gradient(135deg, #fef2f2 0%, #fecaca 100%) !important;
        border: 1px solid #fecaca !important;
        border-radius: 8px !important;
        color: var(--error-color) !important;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #fefce8 0%, #fef3c7 100%) !important;
        border: 1px solid #fef3c7 !important;
        border-radius: 8px !important;
        color: var(--warning-color) !important;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%) !important;
        border: 1px solid #bfdbfe !important;
        border-radius: 8px !important;
        color: var(--secondary-color) !important;
    }
    
         /* Enhanced selectbox */
     .stSelectbox > div > div > div {
         border: 2px solid var(--border-color) !important;
         border-radius: 8px !important;
         background: var(--background-card) !important;
     }
    
    /* Enhanced radio buttons */
    .stRadio > div > label > div {
        background: var(--background-secondary) !important;
        border: 2px solid var(--border-color) !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }
    
         .stRadio > div > label > div:hover {
         border-color: var(--primary-color) !important;
         background: var(--background-card) !important;
     }
    
         /* Enhanced checkboxes */
     .stCheckbox > label > div {
         background: var(--background-card) !important;
         border: 2px solid var(--border-color) !important;
         border-radius: 4px !important;
     }
    
    /* Animation classes */
    .fade-in {
        animation: fadeIn 0.6s ease-in;
    }
    
    .slide-up {
        animation: slideUp 0.6s ease-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes slideUp {
        from { 
            opacity: 0;
            transform: translateY(20px);
        }
        to { 
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Glass morphism effect for special cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        padding: 2rem;
        margin: 1rem 0;
    }
    
    /* Loading spinner enhancement */
    .stSpinner > div {
        border-color: var(--primary-color) !important;
    }
    
    /* Code blocks */
    .stCode {
        border-radius: 8px !important;
        border: 1px solid var(--border-color) !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    /* Download button enhancement */
    .stDownloadButton > button {
        background: var(--gradient-secondary) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: var(--shadow-md) !important;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main > div {
            padding: 1rem 0.5rem;
        }
        
        .main-header {
            font-size: 2rem;
        }
        
        .sub-header {
            font-size: 1rem;
        }
        
        .agent-card, .feature-box {
            padding: 1rem;
        }
    }
    
         /* Additional responsive styles can be added here if needed */
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'research_agent' not in st.session_state:
    st.session_state.research_agent = None
if 'webscraper_agent' not in st.session_state:
    st.session_state.webscraper_agent = None
if 'data_analysis_agent' not in st.session_state:
    st.session_state.data_analysis_agent = None
if 'deep_researcher_agent' not in st.session_state:
    st.session_state.deep_researcher_agent = None
if 'research_results' not in st.session_state:
    st.session_state.research_results = []
if 'scraping_results' not in st.session_state:
    st.session_state.scraping_results = []
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = []
if 'deep_research_results' not in st.session_state:
    st.session_state.deep_research_results = []

def initialize_agents():
    """Initialize the research and webscraper agents"""
    try:
        # First, organize research files if the script exists
        try:
            import subprocess
            import sys
            from pathlib import Path
            
            if Path("move_research_files.py").exists():
                st.info("🗂️ Organizing research files...")
                result = subprocess.run([sys.executable, "move_research_files.py"], 
                                      capture_output=True, text=True, check=True)
                if "files moved:" in result.stdout and "0" not in result.stdout.split("files moved:")[1].split("\n")[0]:
                    st.success("✅ Research files organized successfully!")
        except Exception as e:
            # Don't fail initialization if file organization fails
            st.warning(f"⚠️ Could not organize research files: {e}")
        
        # Create directories if they don't exist
        os.makedirs("research", exist_ok=True)
        os.makedirs("deep research", exist_ok=True)
        
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
        
        # Initialize Data Analysis Agent
        data_analysis_config = AgentConfig(
            name="StreamlitDataAnalysisAgent",
            description="Advanced data analysis agent with visualization capabilities",
            capabilities=[
                "data_loading", "statistical_analysis", "visualization",
                "correlation_analysis", "hypothesis_testing", "atf_support"
            ]
        )
        st.session_state.data_analysis_agent = DataAnalysisAgent(data_analysis_config)
        
        # Initialize Deep Researcher Agent
        deep_researcher_config = AgentConfig(
            name="StreamlitDeepResearcherAgent",
            description="Advanced PDF link extraction and deep content scraping agent",
            capabilities=[
                "pdf_link_extraction", "content_scraping", "content_filtering",
                "deep_analysis", "link_validation"
            ]
        )
        st.session_state.deep_researcher_agent = DeepResearcherAgent(deep_researcher_config)
        
        # Connect agents
        if st.session_state.research_agent and st.session_state.webscraper_agent:
            st.session_state.research_agent.set_webscraper_agent(st.session_state.webscraper_agent)
        
        if st.session_state.deep_researcher_agent and st.session_state.webscraper_agent:
            st.session_state.deep_researcher_agent.set_webscraper_agent(st.session_state.webscraper_agent)
        
        # Start agents
        st.session_state.research_agent.start()
        st.session_state.webscraper_agent.start()
        st.session_state.data_analysis_agent.start()
        st.session_state.deep_researcher_agent.start()
        
        return True
        
    except Exception as e:
        st.error(f"Error initializing agents: {e}")
        return False

def main():
    """Main application interface"""
    
    # Header with enhanced styling
    st.markdown('''
    <div class="fade-in">
        <h1 class="main-header">🤖 Agent Creator</h1>
        <p class="sub-header">AI-Powered Research & Web Scraping Platform with MLX Integration</p>
        <div style="text-align: center; margin-bottom: 2rem;">
            <span style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                         color: white; padding: 0.5rem 1rem; border-radius: 20px; 
                         font-size: 0.9rem; font-weight: 500; margin: 0 0.5rem;">
                🚀 Next-Gen AI Platform
            </span>
            <span style="background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%); 
                         color: white; padding: 0.5rem 1rem; border-radius: 20px; 
                         font-size: 0.9rem; font-weight: 500; margin: 0 0.5rem;">
                ⚡ MLX Powered
            </span>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Enhanced Sidebar
    with st.sidebar:
        st.markdown('''
        <div class="slide-up">
            <h2 style="color: var(--primary-color); font-weight: 600; margin-bottom: 1.5rem; 
                       text-align: center; font-size: 1.5rem;">
                🛠️ Control Center
            </h2>
        </div>
        ''', unsafe_allow_html=True)
        
        # Agent initialization with enhanced styling
        st.markdown('''
        <div style="background: linear-gradient(135deg, #374151 0%, #4b5563 100%); 
                    padding: 1rem; border-radius: 12px; margin-bottom: 1.5rem; 
                    border: 2px solid var(--border-color);">
        ''', unsafe_allow_html=True)
        if st.button("🚀 Initialize Agents", type="primary", key="init_agents_btn", use_container_width=True):
            with st.spinner("🔄 Initializing AI agents..."):
                if initialize_agents():
                    st.success("✅ Agents initialized successfully!")
                else:
                    st.error("❌ Failed to initialize agents")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Agent status with enhanced cards
        st.markdown('''
        <div style="margin: 1.5rem 0;">
            <h3 style="color: var(--text-primary); font-weight: 600; margin-bottom: 1rem; 
                       font-size: 1.1rem; display: flex; align-items: center; gap: 0.5rem;">
                📡 Agent Status
            </h3>
        </div>
        ''', unsafe_allow_html=True)
        
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
            
        if st.session_state.data_analysis_agent:
            st.markdown('<div class="status-success">📊 Data Analysis Agent: Online</div>', 
                       unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-error">📊 Data Analysis Agent: Offline</div>', 
                       unsafe_allow_html=True)
            
        if st.session_state.deep_researcher_agent:
            st.markdown('<div class="status-success">🔍 Deep Researcher Agent: Online</div>', 
                       unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-error">🔍 Deep Researcher Agent: Offline</div>', 
                       unsafe_allow_html=True)
        
        # Enhanced Statistics
        st.markdown('''
        <div style="margin: 1.5rem 0;">
            <h3 style="color: var(--text-primary); font-weight: 600; margin-bottom: 1rem; 
                       font-size: 1.1rem; display: flex; align-items: center; gap: 0.5rem;">
                📊 Analytics
            </h3>
        </div>
        ''', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "Research Tasks", 
                len(st.session_state.research_results),
                delta=None,
                help="Total research tasks completed"
            )
            st.metric(
                "Deep Research", 
                len(st.session_state.deep_research_results),
                delta=None,
                help="Total deep research tasks completed"
            )
        with col2:
            st.metric(
                "Scraping Tasks", 
                len(st.session_state.scraping_results),
                delta=None,
                help="Total web scraping tasks completed"
            )
            st.metric(
                "Analysis Tasks", 
                len(st.session_state.analysis_results),
                delta=None,
                help="Total data analysis tasks completed"
            )
        
        # Add quick stats
        if st.session_state.research_results or st.session_state.scraping_results or st.session_state.analysis_results:
            st.markdown('''
            <div style="background: var(--background-secondary); padding: 1rem; 
                        border-radius: 8px; margin-top: 1rem; text-align: center;">
                <div style="font-size: 0.9rem; color: var(--text-secondary);">
                    Platform Activity Score
                </div>
                <div style="font-size: 1.5rem; font-weight: 600; color: var(--primary-color);">
                    {}
                </div>
            </div>
            '''.format(
                (len(st.session_state.research_results) + len(st.session_state.scraping_results) + len(st.session_state.analysis_results) + len(st.session_state.deep_research_results)) * 10
            ), unsafe_allow_html=True)
    
    # Main content area
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🔬 Research Agent", "🕷️ Webscraper Agent", "📊 Data Analysis Agent", 
        "🔍 Deep Researcher", "📈 Results & Analytics", "📖 Documentation"
    ])
    
    with tab1:
        research_agent_interface()
    
    with tab2:
        webscraper_agent_interface()
    
    with tab3:
        data_analysis_agent_interface()
    
    with tab4:
        deep_researcher_interface()
    
    with tab5:
        results_analytics()
    
    with tab6:
        documentation_interface()

def research_agent_interface():
    """Interface for the Research Agent"""
    st.markdown('''
    <div class="slide-up">
        <div style="background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%); 
                    padding: 2rem; border-radius: 16px; margin-bottom: 2rem; 
                    border: 1px solid var(--border-color); position: relative; overflow: hidden;">
            <div style="position: absolute; top: 0; left: 0; right: 0; height: 4px; 
                        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);"></div>
            <h2 style="color: var(--primary-color); font-size: 2rem; font-weight: 700; 
                       margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.75rem;">
                🔬 AI Research Agent
            </h2>
            <p style="color: var(--text-secondary); font-size: 1.1rem; margin: 0; line-height: 1.6;">
                Perform comprehensive online research with AI-powered analysis and report generation.
            </p>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    if not st.session_state.research_agent:
        st.markdown('''
        <div style="background: linear-gradient(135deg, #374151 0%, #4b5563 100%); 
                    padding: 1.5rem; border-radius: 12px; border: 1px solid var(--border-color); 
                    margin: 2rem 0; text-align: center;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">⚠️</div>
            <div style="color: var(--warning-color); font-weight: 600; font-size: 1.1rem;">
                Please initialize the agents first using the sidebar.
            </div>
        </div>
        ''', unsafe_allow_html=True)
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
    
    # Research query input with enhanced styling
    st.markdown('''
    <div style="margin: 2rem 0;">
        <h3 style="color: var(--text-primary); font-weight: 600; margin-bottom: 1rem; 
                   font-size: 1.3rem; display: flex; align-items: center; gap: 0.5rem;">
            📝 Research Query
        </h3>
        <p style="color: var(--text-secondary); margin-bottom: 1rem; font-size: 0.95rem;">
            Enter your research topic or question. Be specific for better results.
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    query = st.text_area(
        "Research Topic",
        placeholder="e.g., 'Latest developments in artificial intelligence and machine learning'",
        height=120,
        help="Provide a clear, specific research question or topic for optimal results",
        label_visibility="collapsed"
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
    st.markdown('''
    <div class="slide-up">
        <div style="background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%); 
                    padding: 2rem; border-radius: 16px; margin-bottom: 2rem; 
                    border: 1px solid var(--border-color); position: relative; overflow: hidden;">
            <div style="position: absolute; top: 0; left: 0; right: 0; height: 4px; 
                        background: linear-gradient(90deg, #06b6d4 0%, #3b82f6 100%);"></div>
            <h2 style="color: var(--secondary-color); font-size: 2rem; font-weight: 700; 
                       margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.75rem;">
                🕷️ Advanced Web Scraper
            </h2>
            <p style="color: var(--text-secondary); font-size: 1.1rem; margin: 0; line-height: 1.6;">
                Extract content, links, and metadata from web pages with intelligent parsing.
            </p>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    if not st.session_state.webscraper_agent:
        st.markdown('''
        <div style="background: linear-gradient(135deg, #374151 0%, #4b5563 100%); 
                    padding: 1.5rem; border-radius: 12px; border: 1px solid var(--border-color); 
                    margin: 2rem 0; text-align: center;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">⚠️</div>
            <div style="color: var(--warning-color); font-weight: 600; font-size: 1.1rem;">
                Please initialize the agents first using the sidebar.
            </div>
        </div>
        ''', unsafe_allow_html=True)
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
    st.markdown('''
    <div style="margin: 1.5rem 0;">
        <h3 style="color: var(--secondary-color); font-weight: 600; margin-bottom: 1rem; 
                   font-size: 1.3rem; display: flex; align-items: center; gap: 0.5rem;">
            🌐 Single URL Scraping
        </h3>
        <p style="color: var(--text-secondary); margin-bottom: 1rem; font-size: 0.95rem;">
            Extract content from a single webpage with intelligent parsing.
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    url = st.text_input(
        "URL to Scrape",
        placeholder="https://example.com",
        help="Enter a valid URL to extract content from",
        key="single_url_input",
        label_visibility="collapsed"
    )
    
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("🕷️ Scrape URL", type="primary", disabled=not url.strip(), key="scrape_single_url_btn"):
            execute_single_scraping(url)
    with col2:
        if st.button("📋 Example URL", key="example_single_url_btn"):
            st.session_state.example_url = "https://news.ycombinator.com"
            st.rerun()

def multiple_urls_interface():
    """Interface for multiple URLs scraping"""
    st.markdown('''
    <div style="margin: 1.5rem 0;">
        <h3 style="color: var(--secondary-color); font-weight: 600; margin-bottom: 1rem; 
                   font-size: 1.3rem; display: flex; align-items: center; gap: 0.5rem;">
            🌐 Multiple URLs Scraping
        </h3>
        <p style="color: var(--text-secondary); margin-bottom: 1rem; font-size: 0.95rem;">
            Batch process multiple URLs for efficient content extraction.
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    urls_text = st.text_area(
        "URLs to Scrape",
        placeholder="https://example1.com\nhttps://example2.com\nhttps://example3.com",
        height=140,
        help="Enter each URL on a separate line for batch processing",
        label_visibility="collapsed"
    )
    
    if st.button("🕷️ Scrape All URLs", type="primary", disabled=not urls_text.strip(), key="scrape_multiple_urls_btn"):
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        execute_multiple_scraping(urls)

def link_extraction_interface():
    """Interface for link extraction"""
    st.markdown('''
    <div style="margin: 1.5rem 0;">
        <h3 style="color: var(--secondary-color); font-weight: 600; margin-bottom: 1rem; 
                   font-size: 1.3rem; display: flex; align-items: center; gap: 0.5rem;">
            🔗 Link Extraction
        </h3>
        <p style="color: var(--text-secondary); margin-bottom: 1rem; font-size: 0.95rem;">
            Discover and extract all links from a webpage automatically.
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    url = st.text_input(
        "URL for Link Extraction",
        placeholder="https://example.com",
        key="link_extraction_input",
        help="Enter a URL to extract all discoverable links from the page",
        label_visibility="collapsed"
    )
    
    if st.button("🔗 Extract Links", type="primary", disabled=not url.strip(), key="extract_links_btn"):
        execute_link_extraction(url)

def data_analysis_agent_interface():
    """Interface for the Data Analysis Agent"""
    st.markdown('''
    <div class="slide-up">
        <div style="background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%); 
                    padding: 2rem; border-radius: 16px; margin-bottom: 2rem; 
                    border: 1px solid var(--border-color); position: relative; overflow: hidden;">
            <div style="position: absolute; top: 0; left: 0; right: 0; height: 4px; 
                        background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%);"></div>
            <h2 style="color: #f59e0b; font-size: 2rem; font-weight: 700; 
                       margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.75rem;">
                📊 Data Analysis Agent
            </h2>
                         <p style="color: var(--text-secondary); font-size: 1.1rem; margin: 0; line-height: 1.6;">
                 Comprehensive data analysis with automated visualization and statistical insights.<br/>
                 <strong>New:</strong> ATF (Axon Text Format) file support for electrophysiology data analysis.
             </p>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    if not st.session_state.data_analysis_agent:
        st.markdown('''
        <div style="background: linear-gradient(135deg, #374151 0%, #4b5563 100%); 
                    padding: 1.5rem; border-radius: 12px; border: 1px solid var(--border-color); 
                    margin: 2rem 0; text-align: center;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">⚠️</div>
            <div style="color: var(--warning-color); font-weight: 600; font-size: 1.1rem;">
                Please initialize the agents first using the sidebar.
            </div>
        </div>
        ''', unsafe_allow_html=True)
        return
    
    # Analysis mode selection
    mode = st.radio(
        "Select analysis mode:",
        ["File Upload", "Manual Data Entry", "Example Dataset"],
        horizontal=True
    )
    
    # Analysis configuration
    with st.expander("🔧 Analysis Configuration", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            analysis_type = st.selectbox(
                "Analysis Type",
                ["comprehensive", "statistical", "visualization", "correlation"]
            )
            generate_report = st.checkbox("Generate comprehensive report", value=True)
        with col2:
            create_visualizations = st.checkbox("Create visualizations", value=True)
            perform_quality_check = st.checkbox("Perform data quality check", value=True)
    
    if mode == "File Upload":
        file_upload_interface(analysis_type, generate_report, create_visualizations, perform_quality_check)
    elif mode == "Manual Data Entry":
        manual_data_interface(analysis_type, generate_report, create_visualizations, perform_quality_check)
    else:
        example_dataset_interface(analysis_type, generate_report, create_visualizations, perform_quality_check)
    
    # Display recent analysis results
    if st.session_state.analysis_results:
        st.markdown("### 📊 Recent Analysis Results")
        for i, result in enumerate(reversed(st.session_state.analysis_results[-3:])):
            with st.expander(f"📈 {result['type']} analysis ({result['timestamp']})"):
                display_analysis_result(result)

def file_upload_interface(analysis_type, generate_report, create_visualizations, perform_quality_check):
    """Interface for file upload analysis"""
    st.markdown('''
    <div style="margin: 1.5rem 0;">
        <h3 style="color: #f59e0b; font-weight: 600; margin-bottom: 1rem; 
                   font-size: 1.3rem; display: flex; align-items: center; gap: 0.5rem;">
            📁 File Upload Analysis
        </h3>
        <p style="color: var(--text-secondary); margin-bottom: 1rem; font-size: 0.95rem;">
                         Upload a CSV, Excel, JSON, TSV, or ATF file for comprehensive data analysis.
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose a data file",
        type=['csv', 'xlsx', 'xls', 'json', 'tsv', 'atf'],
        help="Supported formats: CSV, Excel (.xlsx, .xls), JSON, TSV, ATF (Axon Text Format)"
    )
    
    if uploaded_file is not None:
        col1, col2 = st.columns([2, 1])
        with col1:
            if st.button("🚀 Analyze Data", type="primary", key="analyze_file_btn"):
                execute_file_analysis(uploaded_file, analysis_type, generate_report, create_visualizations, perform_quality_check)
        with col2:
            st.info(f"File: {uploaded_file.name} ({uploaded_file.size} bytes)")

def manual_data_interface(analysis_type, generate_report, create_visualizations, perform_quality_check):
    """Interface for manual data entry"""
    st.markdown('''
    <div style="margin: 1.5rem 0;">
        <h3 style="color: #f59e0b; font-weight: 600; margin-bottom: 1rem; 
                   font-size: 1.3rem; display: flex; align-items: center; gap: 0.5rem;">
            ✏️ Manual Data Entry
        </h3>
        <p style="color: var(--text-secondary); margin-bottom: 1rem; font-size: 0.95rem;">
            Enter your data manually in JSON format for analysis.
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    data_input = st.text_area(
        "Data (JSON format)",
        placeholder='{"column1": [1, 2, 3], "column2": ["A", "B", "C"]}',
        height=200,
        help="Enter data in JSON format with column names as keys and arrays as values"
    )
    
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("🚀 Analyze Data", type="primary", disabled=not data_input.strip(), key="analyze_manual_data_btn"):
            execute_manual_data_analysis(data_input, analysis_type, generate_report, create_visualizations, perform_quality_check)
    with col2:
        if st.button("📋 Example Data", key="example_data_btn"):
            st.session_state.example_data = '{"age": [25, 30, 35, 40, 45], "salary": [50000, 60000, 70000, 80000, 90000], "department": ["IT", "Sales", "HR", "IT", "Sales"]}'
            st.rerun()

def example_dataset_interface(analysis_type, generate_report, create_visualizations, perform_quality_check):
    """Interface for example dataset analysis"""
    st.markdown('''
    <div style="margin: 1.5rem 0;">
        <h3 style="color: #f59e0b; font-weight: 600; margin-bottom: 1rem; 
                   font-size: 1.3rem; display: flex; align-items: center; gap: 0.5rem;">
            🎯 Example Dataset
        </h3>
        <p style="color: var(--text-secondary); margin-bottom: 1rem; font-size: 0.95rem;">
            Use a built-in example dataset to explore the data analysis capabilities.
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    dataset_choice = st.selectbox(
        "Choose an example dataset:",
        ["Employee Data", "Sales Data", "Weather Data"]
    )
    
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("🚀 Analyze Dataset", type="primary", key="analyze_example_btn"):
            execute_example_dataset_analysis(dataset_choice, analysis_type, generate_report, create_visualizations, perform_quality_check)
    with col2:
        st.info(f"Dataset: {dataset_choice}")

def execute_file_analysis(uploaded_file, analysis_type, generate_report, create_visualizations, perform_quality_check):
    """Execute file analysis"""
    try:
        with st.spinner("📊 Analyzing uploaded file..."):
            # Save uploaded file temporarily
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            # Analyze file
            result = st.session_state.data_analysis_agent.analyze_file(tmp_file_path, analysis_type)
            
            # Store result
            analysis_data = {
                'type': 'file_upload',
                'filename': uploaded_file.name,
                'analysis_type': analysis_type,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'result': result,
                'config': {
                    'generate_report': generate_report,
                    'create_visualizations': create_visualizations,
                    'perform_quality_check': perform_quality_check
                }
            }
            st.session_state.analysis_results.append(analysis_data)
            
            # Clean up temp file
            os.unlink(tmp_file_path)
            
            st.success("✅ Analysis completed successfully!")
            display_analysis_result(analysis_data)
            
    except Exception as e:
        st.error(f"❌ Analysis failed: {str(e)}")

def execute_manual_data_analysis(data_input, analysis_type, generate_report, create_visualizations, perform_quality_check):
    """Execute manual data analysis"""
    try:
        with st.spinner("📊 Analyzing manual data..."):
            import json
            data_dict = json.loads(data_input)
            
            # Analyze data
            result = st.session_state.data_analysis_agent.analyze_dataframe(data_dict, analysis_type)
            
            # Store result
            analysis_data = {
                'type': 'manual_data',
                'analysis_type': analysis_type,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'result': result,
                'config': {
                    'generate_report': generate_report,
                    'create_visualizations': create_visualizations,
                    'perform_quality_check': perform_quality_check
                }
            }
            st.session_state.analysis_results.append(analysis_data)
            
            st.success("✅ Analysis completed successfully!")
            display_analysis_result(analysis_data)
            
    except json.JSONDecodeError:
        st.error("❌ Invalid JSON format. Please check your data input.")
    except Exception as e:
        st.error(f"❌ Analysis failed: {str(e)}")

def execute_example_dataset_analysis(dataset_choice, analysis_type, generate_report, create_visualizations, perform_quality_check):
    """Execute example dataset analysis"""
    try:
        with st.spinner(f"📊 Analyzing {dataset_choice}..."):
            # Create example data based on choice
            if dataset_choice == "Employee Data":
                data_dict = {
                    "employee_id": list(range(1, 51)),
                    "age": [25 + i % 40 for i in range(50)],
                    "salary": [40000 + i * 1000 + (i % 10) * 500 for i in range(50)],
                    "department": [["IT", "Sales", "HR", "Marketing", "Finance"][i % 5] for i in range(50)],
                    "years_experience": [i % 15 for i in range(50)]
                }
            elif dataset_choice == "Sales Data":
                data_dict = {
                    "month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"] * 8 + ["Jul", "Aug"],
                    "sales": [10000 + i * 500 + (i % 10) * 200 for i in range(50)],
                    "region": [["North", "South", "East", "West"][i % 4] for i in range(50)],
                    "product": [["Product A", "Product B", "Product C"][i % 3] for i in range(50)]
                }
            else:  # Weather Data
                data_dict = {
                    "date": [f"2024-01-{str(i+1).zfill(2)}" for i in range(31)] + [f"2024-02-{str(i+1).zfill(2)}" for i in range(19)],
                    "temperature": [20 + i % 15 + (i % 7) * 2 for i in range(50)],
                    "humidity": [40 + i % 30 + (i % 5) * 3 for i in range(50)],
                    "rainfall": [0 if i % 3 == 0 else (i % 10) * 2 for i in range(50)]
                }
            
            # Analyze data
            result = st.session_state.data_analysis_agent.analyze_dataframe(data_dict, analysis_type)
            
            # Store result
            analysis_data = {
                'type': 'example_dataset',
                'dataset': dataset_choice,
                'analysis_type': analysis_type,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'result': result,
                'config': {
                    'generate_report': generate_report,
                    'create_visualizations': create_visualizations,
                    'perform_quality_check': perform_quality_check
                }
            }
            st.session_state.analysis_results.append(analysis_data)
            
            st.success("✅ Analysis completed successfully!")
            display_analysis_result(analysis_data)
            
    except Exception as e:
        st.error(f"❌ Analysis failed: {str(e)}")

def display_analysis_result(analysis_data: Dict[str, Any]):
    """Display data analysis result in a formatted way"""
    result = analysis_data['result']
    
    # Summary
    st.markdown("#### 📋 Analysis Summary")
    if hasattr(result, 'data_summary') and result.data_summary:
        summary = result.data_summary
        
        # Basic metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if 'shape' in summary:
                st.metric("Rows", summary['shape'][0])
        with col2:
            if 'shape' in summary:
                st.metric("Columns", summary['shape'][1])
        with col3:
            if 'missing_values' in summary:
                total_missing = sum(summary['missing_values'].values())
                st.metric("Missing Values", total_missing)
        with col4:
            if 'memory_usage' in summary:
                st.metric("Memory Usage", f"{summary['memory_usage'] / 1024:.1f} KB")
    
    # Insights
    if hasattr(result, 'insights') and result.insights:
        st.markdown("#### 💡 Key Insights")
        for insight in result.insights[:5]:  # Show top 5 insights
            st.markdown(f"• {insight}")
    
    # Visualizations
    if hasattr(result, 'visualizations') and result.visualizations:
        st.markdown("#### 📈 Visualizations")
        cols = st.columns(2)
        for i, viz_path in enumerate(result.visualizations):
            if os.path.exists(viz_path):
                with cols[i % 2]:
                    st.image(viz_path, caption=os.path.basename(viz_path))
    
    # Recommendations
    if hasattr(result, 'recommendations') and result.recommendations:
        st.markdown("#### 🎯 Recommendations")
        for rec in result.recommendations[:3]:  # Show top 3 recommendations
            st.markdown(f"• {rec}")
    
    # Statistical tests
    if hasattr(result, 'statistical_tests') and result.statistical_tests:
        with st.expander("📊 Statistical Analysis"):
            st.json(result.statistical_tests)

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
        for i, file_path in enumerate(result['files_generated']):
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    # Create a unique key that includes result ID and file path hash
                    file_hash = hashlib.md5(file_path.encode()).hexdigest()[:8]
                    unique_key = f"download_{research_data.get('id', 'unknown')}_{i}_{file_hash}"
                    
                    st.download_button(
                        label=f"📥 Download {os.path.basename(file_path)}",
                        data=f.read(),
                        file_name=os.path.basename(file_path),
                        mime="application/octet-stream",
                        key=unique_key
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
    st.markdown('''
    <div class="slide-up">
        <div style="background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%); 
                    padding: 2rem; border-radius: 16px; margin-bottom: 2rem; 
                    border: 1px solid var(--border-color); position: relative; overflow: hidden;">
            <div style="position: absolute; top: 0; left: 0; right: 0; height: 4px; 
                        background: linear-gradient(90deg, #a855f7 0%, #8b5cf6 100%);"></div>
            <h2 style="color: #a855f7; font-size: 2rem; font-weight: 700; 
                       margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.75rem;">
                📊 Results & Analytics
            </h2>
            <p style="color: var(--text-secondary); font-size: 1.1rem; margin: 0; line-height: 1.6;">
                Comprehensive overview of your research and scraping activities.
            </p>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    if not st.session_state.research_results and not st.session_state.scraping_results and not st.session_state.deep_research_results:
        st.markdown('''
        <div style="background: linear-gradient(135deg, #374151 0%, #4b5563 100%); 
                    padding: 2rem; border-radius: 16px; border: 1px solid var(--border-color); 
                    margin: 2rem 0; text-align: center;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📈</div>
            <div style="color: var(--secondary-color); font-weight: 600; font-size: 1.2rem; margin-bottom: 0.5rem;">
                Ready to Analyze
            </div>
            <div style="color: var(--text-secondary); font-size: 1rem;">
                No results yet. Start by running some research, scraping, or deep research tasks!
            </div>
        </div>
        ''', unsafe_allow_html=True)
        return
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Research Tasks", len(st.session_state.research_results))
        st.metric("Deep Research", len(st.session_state.deep_research_results))
    with col2:
        st.metric("Scraping Tasks", len(st.session_state.scraping_results))
        st.metric("Analysis Tasks", len(st.session_state.analysis_results))
    with col3:
        total_sources = sum(len(r['result']['research_result'].sources) 
                          for r in st.session_state.research_results)
        st.metric("Sources Analyzed", total_sources)
    with col4:
        total_urls = sum(len(r.get('urls', [r.get('url', '')])) 
                        for r in st.session_state.scraping_results)
        total_deep_links = sum(r['result'].total_links_found 
                              for r in st.session_state.deep_research_results)
        st.metric("URLs Scraped", total_urls)
        st.metric("Deep Links Found", total_deep_links)
    
    # Recent activity
    st.markdown("### 📈 Recent Activity")
    
    # Research results
    if st.session_state.research_results:
        st.markdown("#### 🔬 Research Tasks")
        for result in reversed(st.session_state.research_results):
            with st.expander(f"📄 {result['query'][:50]}... ({result['timestamp']})"):
                display_research_result(result)
    
    # Deep research results
    if st.session_state.deep_research_results:
        st.markdown("#### 🔍 Deep Research Tasks")
        for result in reversed(st.session_state.deep_research_results):
            with st.expander(f"📄 {result['filename']} ({result['timestamp']})"):
                display_deep_research_result(result)
    
    # Scraping results  
    if st.session_state.scraping_results:
        st.markdown("#### 🕷️ Scraping Tasks")
        for result in reversed(st.session_state.scraping_results):
            with st.expander(f"🌐 {result['type']} ({result['timestamp']})"):
                if result['type'] == 'single_url':
                    display_scraping_result(result['result'])
                else:
                    st.json(result)
    
    # Analysis results
    if st.session_state.analysis_results:
        st.markdown("#### 📊 Analysis Tasks")
        for result in reversed(st.session_state.analysis_results):
            with st.expander(f"📈 {result['type']} ({result['timestamp']})"):
                display_analysis_result(result)

def documentation_interface():
    """Display documentation and help"""
    st.markdown('''
    <div class="slide-up">
        <div style="background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%); 
                    padding: 2rem; border-radius: 16px; margin-bottom: 2rem; 
                    border: 1px solid var(--border-color); position: relative; overflow: hidden;">
            <div style="position: absolute; top: 0; left: 0; right: 0; height: 4px; 
                        background: linear-gradient(90deg, #ec4899 0%, #be185d 100%);"></div>
            <h2 style="color: #ec4899; font-size: 2rem; font-weight: 700; 
                       margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.75rem;">
                📖 Documentation & Help
            </h2>
            <p style="color: var(--text-secondary); font-size: 1.1rem; margin: 0; line-height: 1.6;">
                Complete guide to using the Agent Creator platform effectively.
            </p>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown("""
    ### 🤖 Agent Creator Platform
    
    Welcome to the Agent Creator platform! This application showcases four powerful AI agents:
    
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
    
    #### 📊 Data Analysis Agent
    The Data Analysis Agent provides comprehensive data processing and analysis:
    - **Multi-Format Support**: CSV, Excel, JSON, TSV, and **ATF (Axon Text Format)** files
    - **Statistical Analysis**: Comprehensive statistical tests and correlations
    - **Automated Visualizations**: Distribution plots, correlation heatmaps, box plots
    - **Data Quality Assessment**: Missing values, outliers, data type analysis
    - **AI-Generated Insights**: Intelligent analysis using LLM integration
    - **Electrophysiology Data**: Specialized support for ATF files from electrophysiology experiments
    
    #### 🔍 Deep Researcher Agent
    The Deep Researcher Agent specializes in PDF-based research and deep content analysis:
    - **PDF Link Extraction**: Extract hyperlinks and URLs from PDF documents
    - **Content Scraping**: Automatically scrape and analyze content from extracted links
    - **Intelligent Filtering**: Filter content by domain and relevance
    - **Comprehensive Reports**: Generate detailed analysis reports with structured data
    - **Automated Summarization**: AI-powered summarization of scraped content
    - **File Organization**: Save results to dedicated deep research directory
    
    ### 🚀 Getting Started
    
    1. **Initialize Agents**: Use the sidebar to initialize all agents
    2. **Research**: Enter a research query in the Research Agent tab
    3. **Deep Research**: Upload a PDF in the Deep Researcher tab for link extraction
    4. **Scrape**: Use the Webscraper Agent for targeted content extraction
    5. **Analyze**: Upload data files in the Data Analysis Agent tab
    6. **Review**: View results and download generated reports in the Results & Analytics tab
    
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
    - **PDF Research**: Extract and analyze references from academic papers and documents
    - **Scientific Data Analysis**: Process experimental data including electrophysiology recordings (ATF format)
    - **Laboratory Data Processing**: Analyze and visualize scientific measurements and observations
    
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
            st.write(f"Data Analysis Agent: {'✅ Online' if st.session_state.data_analysis_agent else '❌ Offline'}")
            st.write(f"Deep Researcher Agent: {'✅ Online' if st.session_state.deep_researcher_agent else '❌ Offline'}")
        
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
            
            try:
                import pdfplumber
                st.write("✅ PDF Processing (pdfplumber)")
            except ImportError:
                st.write("❌ PDF Processing (pdfplumber)")

def deep_researcher_interface():
    """Interface for the Deep Researcher Agent"""
    st.markdown('''
    <div class="slide-up">
        <div style="background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%); 
                    padding: 2rem; border-radius: 16px; margin-bottom: 2rem; 
                    border: 1px solid var(--border-color); position: relative; overflow: hidden;">
            <div style="position: absolute; top: 0; left: 0; right: 0; height: 4px; 
                        background: linear-gradient(90deg, #8b5cf6 0%, #a855f7 100%);"></div>
            <h2 style="color: #8b5cf6; font-size: 2rem; font-weight: 700; 
                       margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.75rem;">
                🔍 Deep Researcher Agent
            </h2>
            <p style="color: var(--text-secondary); font-size: 1.1rem; margin: 0; line-height: 1.6;">
                Extract links from PDF documents and perform deep content analysis with intelligent filtering.<br/>
                <strong>Features:</strong> PDF link extraction, content scraping, and automated report generation.
            </p>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    if not st.session_state.deep_researcher_agent:
        st.markdown('''
        <div style="background: linear-gradient(135deg, #374151 0%, #4b5563 100%); 
                    padding: 1.5rem; border-radius: 12px; border: 1px solid var(--border-color); 
                    margin: 2rem 0; text-align: center;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">⚠️</div>
            <div style="color: var(--warning-color); font-weight: 600; font-size: 1.1rem;">
                Please initialize the agents first using the sidebar.
            </div>
        </div>
        ''', unsafe_allow_html=True)
        return
    
    # Deep research configuration
    with st.expander("🔧 Deep Research Configuration", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            max_links = st.slider("Maximum links to extract", 5, 50, 15)
            include_images = st.checkbox("Include images in scraping", value=True)
        with col2:
            filter_domains = st.text_input(
                "Filter domains (comma-separated)", 
                placeholder="arxiv.org, github.com, nature.com",
                help="Only extract links from specific domains (optional)"
            )
            save_to_deep_research = st.checkbox("Save to deep research directory", value=True)
    
    # PDF upload interface
    st.markdown('''
    <div style="margin: 2rem 0;">
        <h3 style="color: #8b5cf6; font-weight: 600; margin-bottom: 1rem; 
                   font-size: 1.3rem; display: flex; align-items: center; gap: 0.5rem;">
            📄 PDF Document Upload
        </h3>
        <p style="color: var(--text-secondary); margin-bottom: 1rem; font-size: 0.95rem;">
            Upload a PDF document to extract links and perform deep research analysis.
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    uploaded_pdf = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload a PDF document for link extraction and deep analysis"
    )
    
    if uploaded_pdf is not None:
        col1, col2 = st.columns([2, 1])
        with col1:
            if st.button("🔍 Start Deep Research", type="primary", key="start_deep_research_btn"):
                execute_deep_research(
                    uploaded_pdf, max_links, include_images, 
                    filter_domains, save_to_deep_research
                )
        with col2:
            st.info(f"File: {uploaded_pdf.name} ({uploaded_pdf.size} bytes)")
    
    # Display recent deep research results
    if st.session_state.deep_research_results:
        st.markdown("### 🔍 Recent Deep Research Results")
        for i, result in enumerate(reversed(st.session_state.deep_research_results[-3:])):
            with st.expander(f"📄 {result['filename']} ({result['timestamp']})"):
                display_deep_research_result(result)

def execute_deep_research(uploaded_pdf, max_links: int, include_images: bool, 
                         filter_domains: str, save_to_deep_research: bool):
    """Execute deep research with the uploaded PDF"""
    try:
        with st.spinner("🔍 Performing deep research..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Save uploaded PDF temporarily
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_pdf.getvalue())
                tmp_file_path = tmp_file.name
            
            # Step 1: Extract links from PDF
            status_text.text("Extracting links from PDF...")
            progress_bar.progress(25)
            
            # Parse filter domains
            domain_list = []
            if filter_domains.strip():
                domain_list = [domain.strip() for domain in filter_domains.split(',') if domain.strip()]
            
            # Perform deep research
            result = st.session_state.deep_researcher_agent.deep_research(
                pdf_path=tmp_file_path,
                max_links=max_links,
                filter_domains=domain_list,
                include_images=include_images
            )
            
            progress_bar.progress(75)
            status_text.text("Generating comprehensive report...")
            
            # Save results to deep research directory if requested
            saved_files = []
            if save_to_deep_research:
                saved_files = save_deep_research_results(result, uploaded_pdf.name)
            
            # Store result
            deep_research_data = {
                'filename': uploaded_pdf.name,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'result': result,
                'saved_files': saved_files,
                'config': {
                    'max_links': max_links,
                    'include_images': include_images,
                    'filter_domains': domain_list,
                    'save_to_deep_research': save_to_deep_research
                }
            }
            st.session_state.deep_research_results.append(deep_research_data)
            
            # Clean up temp file
            os.unlink(tmp_file_path)
            
            progress_bar.progress(100)
            status_text.text("✅ Deep research completed!")
            
            # Display results
            st.success("🎉 Deep research completed successfully!")
            display_deep_research_result(deep_research_data)
            
    except Exception as e:
        st.error(f"❌ Deep research failed: {str(e)}")

def save_deep_research_results(result, original_filename: str) -> List[str]:
    """Save deep research results to the deep research directory"""
    saved_files = []
    
    try:
        # Create timestamp for unique filenames
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = os.path.splitext(original_filename)[0]
        
        # Save comprehensive report as text file
        report_filename = f"deep_research_{base_name}_{timestamp}.txt"
        report_path = os.path.join("deep research", report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"Deep Research Report\n")
            f.write(f"{'=' * 50}\n\n")
            f.write(f"Source PDF: {original_filename}\n")
            f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Links Found: {result.total_links_found}\n")
            f.write(f"Successful Scrapes: {result.successful_scrapes}\n\n")
            
            f.write(f"Summary:\n{'-' * 20}\n{result.summary}\n\n")
            
            f.write(f"Extracted Links:\n{'-' * 20}\n")
            for i, link in enumerate(result.extracted_links, 1):
                f.write(f"{i}. {link.url}\n")
                if link.text:
                    f.write(f"   Text: {link.text}\n")
                if link.context:
                    f.write(f"   Context: {link.context}\n")
                f.write(f"   Page: {link.page_number}\n\n")
            
            f.write(f"Scraped Content:\n{'-' * 20}\n")
            for i, content in enumerate(result.scraped_content, 1):
                f.write(f"{i}. {content.url}\n")
                f.write(f"   Title: {content.title}\n")
                f.write(f"   Success: {content.success}\n")
                if content.success:
                    f.write(f"   Content: {content.clean_text[:500]}...\n")
                else:
                    f.write(f"   Error: {content.error}\n")
                f.write("\n")
        
        saved_files.append(report_path)
        
        # Save as JSON for structured data
        json_filename = f"deep_research_{base_name}_{timestamp}.json"
        json_path = os.path.join("deep research", json_filename)
        
        # Convert result to JSON-serializable format
        json_data = {
            'source_pdf': original_filename,
            'timestamp': result.timestamp.isoformat(),
            'total_links_found': result.total_links_found,
            'successful_scrapes': result.successful_scrapes,
            'summary': result.summary,
            'extracted_links': [
                {
                    'url': link.url,
                    'text': link.text,
                    'page_number': link.page_number,
                    'context': link.context
                }
                for link in result.extracted_links
            ],
            'scraped_content': [
                {
                    'url': content.url,
                    'title': content.title,
                    'success': content.success,
                    'clean_text': content.clean_text,
                    'error': content.error
                }
                for content in result.scraped_content
            ]
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        saved_files.append(json_path)
        
    except Exception as e:
        st.warning(f"Could not save deep research results: {str(e)}")
    
    return saved_files

def display_deep_research_result(deep_research_data: Dict[str, Any]):
    """Display deep research result in a formatted way"""
    result = deep_research_data['result']
    
    # Summary metrics
    st.markdown("#### 📋 Deep Research Summary")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Links Found", result.total_links_found)
    with col2:
        st.metric("Successful Scrapes", result.successful_scrapes)
    with col3:
        scrape_rate = (result.successful_scrapes / max(result.total_links_found, 1)) * 100
        st.metric("Success Rate", f"{scrape_rate:.1f}%")
    with col4:
        if deep_research_data['saved_files']:
            st.metric("Files Generated", len(deep_research_data['saved_files']))
    
    # Analysis summary
    if result.summary:
        st.markdown("#### 💡 Analysis Summary")
        st.write(result.summary)
    
    # Extracted links
    if result.extracted_links:
        st.markdown("#### 🔗 Extracted Links")
        for i, link in enumerate(result.extracted_links[:10], 1):  # Show first 10
            with st.expander(f"Link {i}: {link.url[:50]}..."):
                st.markdown(f"**URL:** [{link.url}]({link.url})")
                st.markdown(f"**Page:** {link.page_number}")
                if link.text:
                    st.markdown(f"**Text:** {link.text}")
                if link.context:
                    st.markdown(f"**Context:** {link.context}")
        
        if len(result.extracted_links) > 10:
            st.info(f"... and {len(result.extracted_links) - 10} more links")
    
    # Scraped content preview
    successful_content = [c for c in result.scraped_content if c.success]
    if successful_content:
        st.markdown("#### 📄 Scraped Content Preview")
        for i, content in enumerate(successful_content[:3], 1):  # Show first 3
            with st.expander(f"Content {i}: {content.title or content.url[:50]}"):
                st.markdown(f"**URL:** [{content.url}]({content.url})")
                if content.title:
                    st.markdown(f"**Title:** {content.title}")
                if content.clean_text:
                    st.markdown(f"**Content Preview:**")
                    st.text_area(
                        "", 
                        content.clean_text[:300] + "..." if len(content.clean_text) > 300 else content.clean_text,
                        height=100, 
                        disabled=True,
                        key=f"content_preview_{i}_{hash(content.url)}_{deep_research_data['timestamp'].replace(' ', '_').replace(':', '_')}"
                    )
    
    # Download generated files
    if deep_research_data['saved_files']:
        st.markdown("#### 📁 Generated Files")
        for file_path in deep_research_data['saved_files']:
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    st.download_button(
                        label=f"📥 Download {os.path.basename(file_path)}",
                        data=f.read(),
                        file_name=os.path.basename(file_path),
                        mime="application/octet-stream",
                        key=f"download_deep_research_{deep_research_data['timestamp']}_{os.path.basename(file_path)}"
                    )

if __name__ == "__main__":
    main()