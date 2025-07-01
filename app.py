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
        with col2:
            st.metric(
                "Scraping Tasks", 
                len(st.session_state.scraping_results),
                delta=None,
                help="Total web scraping tasks completed"
            )
        
        # Add quick stats
        if st.session_state.research_results or st.session_state.scraping_results:
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
                (len(st.session_state.research_results) + len(st.session_state.scraping_results)) * 10
            ), unsafe_allow_html=True)
    
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
                    st.download_button(
                        label=f"📥 Download {os.path.basename(file_path)}",
                        data=f.read(),
                        file_name=os.path.basename(file_path),
                        mime="application/octet-stream",
                        key=f"download_research_{research_data['timestamp']}_{i}_{os.path.basename(file_path)}"
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
    
    if not st.session_state.research_results and not st.session_state.scraping_results:
        st.markdown('''
        <div style="background: linear-gradient(135deg, #374151 0%, #4b5563 100%); 
                    padding: 2rem; border-radius: 16px; border: 1px solid var(--border-color); 
                    margin: 2rem 0; text-align: center;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📈</div>
            <div style="color: var(--secondary-color); font-weight: 600; font-size: 1.2rem; margin-bottom: 0.5rem;">
                Ready to Analyze
            </div>
            <div style="color: var(--text-secondary); font-size: 1rem;">
                No results yet. Start by running some research or scraping tasks!
            </div>
        </div>
        ''', unsafe_allow_html=True)
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