"""Streamlit web interface for the Deep Research System."""

import streamlit as st
import os
import time
from datetime import datetime
import logging

# Import our deep researcher
try:
    from ..core.researcher import DeepResearcher
    from ..models.data_models import ResearchResult
except ImportError:
    try:
        # Fallback for when running as standalone script
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from core.researcher import DeepResearcher
        from models.data_models import ResearchResult
    except ImportError as e:
        st.error(f"Error importing deep researcher: {e}")
        st.stop()

# Configure page
st.set_page_config(
    page_title="Deep Research Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #1f77b4;
        background-color: #f8f9fa;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    
    .research-section {
        background: white;
        padding: 2rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .finding-item {
        background: #f8f9fa;
        padding: 1rem;
        border-left: 3px solid #28a745;
        margin: 0.5rem 0;
        border-radius: 0 0.25rem 0.25rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'research_results' not in st.session_state:
    st.session_state.research_results = []
if 'current_research' not in st.session_state:
    st.session_state.current_research = None
if 'research_in_progress' not in st.session_state:
    st.session_state.research_in_progress = False


def display_research_result(research_data: dict):
    """Display research results in a formatted way"""
    if 'error' in research_data:
        st.error(f"Research failed: {research_data['error']}")
        return
    
    result = research_data['result']
    pdf_path = research_data['pdf_path']
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🔍 Search Results</h3>
            <h2>{len(result.initial_results)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📄 Pages Crawled</h3>
            <h2>{result.total_pages_crawled}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🔗 Links Found</h3>
            <h2>{result.total_links_found}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>⏱️ Time Taken</h3>
            <h2>{result.research_time:.1f}s</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Research Summary
    if result.summary:
        st.markdown("""
        <div class="research-section">
            <h2>📋 Research Summary</h2>
        </div>
        """, unsafe_allow_html=True)
        
        summary_lines = result.summary.split('\n')
        for line in summary_lines:
            if line.strip():
                st.write(line)
    
    # Key Findings
    if result.key_findings:
        st.markdown("""
        <div class="research-section">
            <h2>💡 Key Findings</h2>
        </div>
        """, unsafe_allow_html=True)
        
        for i, finding in enumerate(result.key_findings, 1):
            st.markdown(f"""
            <div class="finding-item">
                <strong>{i}.</strong> {finding}
            </div>
            """, unsafe_allow_html=True)
    
    # Level 1 Sources (Initial Search Results)
    if result.level_1_content:
        relevant_l1 = [c for c in result.level_1_content if c.success and c.relevance_score > 0.1]
        
        if relevant_l1:
            st.markdown("""
            <div class="research-section">
                <h2>🎯 Primary Sources (Level 1)</h2>
            </div>
            """, unsafe_allow_html=True)
            
            for content in relevant_l1[:5]:  # Show top 5
                with st.expander(f"📖 {content.title or 'Untitled'} (Relevance: {content.relevance_score:.2f})"):
                    st.write(f"**URL:** {content.url}")
                    if content.content:
                        excerpt = content.content[:500] + "..." if len(content.content) > 500 else content.content
                        st.write("**Content Preview:**")
                        st.write(excerpt)
    
    # Level 2 Sources (Recursive Links)
    if result.level_2_content:
        relevant_l2 = [c for c in result.level_2_content if c.success and c.relevance_score > 0.1]
        
        if relevant_l2:
            st.markdown("""
            <div class="research-section">
                <h2>🔍 Secondary Sources (Level 2)</h2>
            </div>
            """, unsafe_allow_html=True)
            
            for content in relevant_l2[:5]:  # Show top 5
                with st.expander(f"📄 {content.title or 'Untitled'} (Relevance: {content.relevance_score:.2f})"):
                    st.write(f"**URL:** {content.url}")
                    if content.content:
                        excerpt = content.content[:500] + "..." if len(content.content) > 500 else content.content
                        st.write("**Content Preview:**")
                        st.write(excerpt)
    
    # PDF Download
    if pdf_path and os.path.exists(pdf_path):
        st.markdown("""
        <div class="research-section">
            <h2>📁 Download Report</h2>
        </div>
        """, unsafe_allow_html=True)
        
        with open(pdf_path, 'rb') as f:
            st.download_button(
                label="📥 Download Complete Research Report (PDF)",
                data=f.read(),
                file_name=os.path.basename(pdf_path),
                mime="application/pdf",
                use_container_width=True
            )


def main():
    """Main application interface"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        🔍 Deep Research Assistant
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem; color: #666;">
        Advanced web crawling and research with recursive link following
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🛠️ Research Configuration")
        
        # Research history
        if st.session_state.research_results:
            st.markdown("### 📚 Research History")
            for i, research in enumerate(reversed(st.session_state.research_results[-5:]), 1):
                if 'result' in research:
                    result = research['result']
                    completed_at = research['completed_at']
                    
                    with st.expander(f"Research {i} - {completed_at.strftime('%H:%M')}"):
                        st.write(f"**Query:** {result.query[:50]}...")
                        st.write(f"**Pages Crawled:** {result.total_pages_crawled}")
                        st.write(f"**Links Found:** {result.total_links_found}")
                        st.write(f"**Time:** {result.research_time:.1f}s")
        
        # Clear history
        if st.session_state.research_results:
            if st.button("🗑️ Clear History"):
                st.session_state.research_results = []
                st.rerun()
    
    # Main interface
    st.markdown("## 📝 Enter Your Research Query")
    
    # Research input
    query = st.text_area(
        "Research Question",
        placeholder="Enter your research question here. For example: 'How to transition from software engineering to PhD with a low GPA?'",
        height=100,
        help="Be specific about what you want to research. The system will search DuckDuckGo, then recursively crawl links to find relevant information."
    )
    
    # Research controls
    col1, col2 = st.columns([3, 1])
    
    with col1:
        start_research = st.button(
            "🚀 Start Deep Research",
            type="primary",
            disabled=not query.strip() or st.session_state.research_in_progress,
            use_container_width=True
        )
    
    with col2:
        if st.session_state.research_in_progress:
            st.button("⏳ Researching...", disabled=True, use_container_width=True)
    
    # Start research
    if start_research and query.strip():
        st.session_state.current_research = None
        
        # Show progress
        st.markdown("""
        <div class="status-box">
            <h3>🔄 Research in Progress</h3>
            <p>This may take several minutes as we:</p>
            <ul>
                <li>Search DuckDuckGo for initial results</li>
                <li>Crawl and analyze each result page</li>
                <li>Extract all links from those pages</li>
                <li>Recursively crawl the most relevant links</li>
                <li>Generate a comprehensive report</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Create progress placeholders
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Run research
            researcher = DeepResearcher()
            
            # Update progress
            progress_bar.progress(10)
            status_text.text("🔍 Searching DuckDuckGo...")
            
            result, pdf_path = researcher.research_and_generate_pdf(query)
            
            # Complete progress
            progress_bar.progress(100)
            status_text.text("✅ Research completed!")
            
            # Store results
            st.session_state.current_research = {
                'result': result,
                'pdf_path': pdf_path,
                'completed_at': datetime.now()
            }
            
            # Add to history
            st.session_state.research_results.append(st.session_state.current_research)
            
            # Clear progress indicators
            time.sleep(1)
            progress_bar.empty()
            status_text.empty()
            
            st.success("🎉 Research completed successfully!")
            st.rerun()
            
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f"❌ Research failed: {str(e)}")
    
    # Display current research results
    if st.session_state.current_research and 'result' in st.session_state.current_research:
        st.markdown("---")
        st.markdown("## 📊 Research Results")
        display_research_result(st.session_state.current_research)
    
    # Information section
    with st.expander("ℹ️ How Deep Research Works"):
        st.markdown("""
        ### Research Process
        
        1. **Initial Search**: Search DuckDuckGo for your query to get 20 initial results
        2. **Level 1 Crawling**: Scrape each of those 20 pages for content and extract all links
        3. **Relevance Filtering**: Analyze content to determine relevance to your research question
        4. **Level 2 Crawling**: Follow the most promising links and scrape their content
        5. **Analysis**: Extract key findings and generate insights from all gathered content
        6. **Report Generation**: Create a comprehensive PDF report with all findings
        
        ### Features
        
        - **Recursive Link Following**: Goes beyond simple search to find deeper, related content
        - **Relevance Scoring**: Automatically identifies content most relevant to your query
        - **Comprehensive Reporting**: Generates detailed PDF reports with sources and findings
        - **Real-time Progress**: See what's happening as the research progresses
        
        ### Best Practices
        
        - Be specific in your research queries
        - Include key terms and context
        - Research queries work best when they're focused questions rather than broad topics
        """)


if __name__ == "__main__":
    main()