"""Main deep research orchestrator for the Deep Research System."""

import logging
import os
import re
import time
from datetime import datetime
from typing import Tuple

from ..models.data_models import ResearchResult
from .crawler import WebCrawler
from .analyzer import ContentAnalyzer
from .report import ReportGenerator, PDFGenerator


class DeepResearcher:
    """Main deep research orchestrator"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.crawler = WebCrawler()
        self.analyzer = ContentAnalyzer()
        self.report_generator = ReportGenerator()
        self.pdf_generator = PDFGenerator()
    
    def research(self, query: str, max_initial_results: int = 20, 
                max_level2_per_page: int = 10) -> ResearchResult:
        """Perform comprehensive deep research"""
        start_time = time.time()
        self.logger.info(f"Starting deep research for: {query}")
        
        # Initialize result
        result = ResearchResult(query=query)
        
        try:
            # Step 1: Search DuckDuckGo for initial results
            self.logger.info("Step 1: Searching DuckDuckGo...")
            result.initial_results = self.crawler.search_duckduckgo(query, max_initial_results)
            
            if not result.initial_results:
                self.logger.error("No initial search results found")
                return result
            
            # Step 2: Crawl level 1 pages (initial search results)
            self.logger.info("Step 2: Crawling level 1 pages...")
            level1_urls = [r.url for r in result.initial_results]
            result.level_1_content = self.crawler.scrape_multiple_urls(level1_urls)
            
            # Filter for relevant content
            result.level_1_content = self.analyzer.filter_relevant_content(
                result.level_1_content, query
            )
            
            # Step 3: Extract all links from level 1 pages
            self.logger.info("Step 3: Extracting links from level 1 pages...")
            all_level2_links = []
            for content in result.level_1_content:
                if content.success and content.links:
                    # Limit links per page
                    page_links = content.links[:max_level2_per_page]
                    all_level2_links.extend(page_links)
            
            # Remove duplicates and limit total
            all_level2_links = list(set(all_level2_links))
            if len(all_level2_links) > 100:  # Reasonable limit
                all_level2_links = all_level2_links[:100]
            
            result.total_links_found = len(all_level2_links)
            
            # Step 4: Crawl level 2 pages (links from level 1)
            if all_level2_links:
                self.logger.info(f"Step 4: Crawling {len(all_level2_links)} level 2 pages...")
                result.level_2_content = self.crawler.scrape_multiple_urls(all_level2_links)
                
                # Filter for relevant content
                result.level_2_content = self.analyzer.filter_relevant_content(
                    result.level_2_content, query
                )
            
            # Step 5: Generate summary and key findings
            self.logger.info("Step 5: Generating summary and findings...")
            result.summary = self.report_generator.generate_summary(result)
            result.key_findings = self.report_generator.extract_key_findings(result)
            
            # Calculate final statistics
            result.total_pages_crawled = len([c for c in result.level_1_content + result.level_2_content if c.success])
            result.research_time = time.time() - start_time
            
            self.logger.info(f"Research completed in {result.research_time:.1f} seconds")
            self.logger.info(f"Total pages crawled: {result.total_pages_crawled}")
            self.logger.info(f"Relevant sources found: {len([c for c in result.level_1_content + result.level_2_content if c.relevance_score > 0.1])}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error during research: {e}")
            result.research_time = time.time() - start_time
            return result
    
    def research_and_generate_pdf(self, query: str, output_dir: str = "research_output") -> Tuple[ResearchResult, str]:
        """Perform research and generate PDF report"""
        # Perform research
        result = self.research(query)
        
        # Generate PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_query = re.sub(r'[^a-zA-Z0-9\s]', '', query)[:50]
        safe_query = re.sub(r'\s+', '_', safe_query)
        
        pdf_filename = f"deep_research_{safe_query}_{timestamp}.pdf"
        pdf_path = os.path.join(output_dir, pdf_filename)
        
        success = self.pdf_generator.generate_pdf(result, pdf_path)
        
        if success:
            self.logger.info(f"Research completed and PDF saved: {pdf_path}")
        else:
            self.logger.error("PDF generation failed")
            pdf_path = ""
        
        return result, pdf_path