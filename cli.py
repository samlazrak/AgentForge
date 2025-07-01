#!/usr/bin/env python3
"""
Deep Research CLI Tool

A command-line interface for performing comprehensive web research using 
DuckDuckGo search and recursive web crawling.

Usage:
    python cli.py "research query here"
    python cli.py "research query here" --output-dir ./reports --pdf
    python cli.py "research query here" --max-results 30 --max-level2 15 --verbose
"""

import argparse
import sys
import os
import time
from pathlib import Path
from typing import Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.tree import Tree
    from rich.layout import Layout
    from rich.live import Live
    from rich.columns import Columns
    from rich.align import Align
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Warning: 'rich' library not available. Install with: pip install rich")

from deep_research import DeepResearcher, ResearchResult


class DeepResearchCLI:
    """Command-line interface for deep research operations"""
    
    def __init__(self):
        if RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None
    
    def print(self, *args, **kwargs):
        """Rich-aware print function"""
        if self.console:
            self.console.print(*args, **kwargs)
        else:
            print(*args, **kwargs)
    
    def print_header(self):
        """Print the application header"""
        if self.console:
            self.console.print(Panel.fit(
                "[bold blue]🔍 Deep Research CLI[/bold blue]\n"
                "[dim]Advanced web crawling and research with recursive link following[/dim]",
                box=box.DOUBLE,
                border_style="blue"
            ))
        else:
            print("=" * 60)
            print("🔍 Deep Research CLI")
            print("Advanced web crawling and research with recursive link following")
            print("=" * 60)
    
    def print_summary_table(self, result: ResearchResult):
        """Print a summary table of research results"""
        if self.console:
            table = Table(title="📊 Research Summary", box=box.ROUNDED)
            table.add_column("Metric", style="cyan", no_wrap=True)
            table.add_column("Value", style="magenta")
            
            table.add_row("Query", result.query)
            table.add_row("Initial Search Results", str(len(result.initial_results)))
            table.add_row("Level 1 Pages Crawled", str(len(result.level_1_content)))
            table.add_row("Level 2 Pages Crawled", str(len(result.level_2_content)))
            table.add_row("Total Pages Crawled", str(result.total_pages_crawled))
            table.add_row("Total Links Found", str(result.total_links_found))
            table.add_row("Research Time", f"{result.research_time:.1f} seconds")
            table.add_row("Timestamp", result.timestamp.strftime('%Y-%m-%d %H:%M:%S'))
            
            self.console.print(table)
        else:
            print("\n📊 Research Summary:")
            print(f"  Query: {result.query}")
            print(f"  Initial Search Results: {len(result.initial_results)}")
            print(f"  Level 1 Pages Crawled: {len(result.level_1_content)}")
            print(f"  Level 2 Pages Crawled: {len(result.level_2_content)}")
            print(f"  Total Pages Crawled: {result.total_pages_crawled}")
            print(f"  Total Links Found: {result.total_links_found}")
            print(f"  Research Time: {result.research_time:.1f} seconds")
            print(f"  Timestamp: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def print_key_findings(self, result: ResearchResult):
        """Print key findings from the research"""
        if not result.key_findings:
            return
        
        if self.console:
            self.console.print("\n💡 [bold green]Key Findings[/bold green]")
            for i, finding in enumerate(result.key_findings, 1):
                # Extract source if present
                if "(Source:" in finding:
                    content, source = finding.rsplit("(Source:", 1)
                    source = source.rstrip(")")
                    self.console.print(f"  [cyan]{i}.[/cyan] {content.strip()}")
                    self.console.print(f"     [dim]Source: {source}[/dim]")
                else:
                    self.console.print(f"  [cyan]{i}.[/cyan] {finding}")
                self.console.print()
        else:
            print("\n💡 Key Findings:")
            for i, finding in enumerate(result.key_findings, 1):
                print(f"  {i}. {finding}")
                print()
    
    def print_sources_tree(self, result: ResearchResult, max_sources: int = 10):
        """Print sources in a tree format"""
        all_content = result.level_1_content + result.level_2_content
        relevant_content = [c for c in all_content if c.success and c.relevance_score > 0.1]
        relevant_content.sort(key=lambda x: x.relevance_score, reverse=True)
        
        if not relevant_content:
            return
        
        if self.console:
            tree = Tree("🔗 [bold blue]Top Sources[/bold blue]")
            
            level1_tree = tree.add("📋 Level 1 Sources (Direct Search Results)")
            level2_tree = tree.add("🔍 Level 2 Sources (Recursive Links)")
            
            level1_sources = [c for c in relevant_content if c in result.level_1_content][:max_sources//2]
            level2_sources = [c for c in relevant_content if c in result.level_2_content][:max_sources//2]
            
            for source in level1_sources:
                title = source.title or "Untitled"
                if len(title) > 50:
                    title = title[:47] + "..."
                
                branch = level1_tree.add(f"[green]{title}[/green] (Relevance: {source.relevance_score:.2f})")
                branch.add(f"[dim]{source.url}[/dim]")
                
                # Add content preview
                if source.content:
                    preview = source.content[:150].replace('\n', ' ')
                    if len(source.content) > 150:
                        preview += "..."
                    branch.add(f"[italic]{preview}[/italic]")
            
            for source in level2_sources:
                title = source.title or "Untitled"
                if len(title) > 50:
                    title = title[:47] + "..."
                
                branch = level2_tree.add(f"[green]{title}[/green] (Relevance: {source.relevance_score:.2f})")
                branch.add(f"[dim]{source.url}[/dim]")
                
                # Add content preview
                if source.content:
                    preview = source.content[:150].replace('\n', ' ')
                    if len(source.content) > 150:
                        preview += "..."
                    branch.add(f"[italic]{preview}[/italic]")
            
            self.console.print(tree)
        else:
            print("\n🔗 Top Sources:")
            print("\n📋 Level 1 Sources (Direct Search Results):")
            level1_sources = [c for c in relevant_content if c in result.level_1_content][:max_sources//2]
            for i, source in enumerate(level1_sources, 1):
                print(f"  {i}. {source.title or 'Untitled'} (Relevance: {source.relevance_score:.2f})")
                print(f"     URL: {source.url}")
                if source.content:
                    preview = source.content[:150].replace('\n', ' ')
                    if len(source.content) > 150:
                        preview += "..."
                    print(f"     Preview: {preview}")
                print()
            
            print("\n🔍 Level 2 Sources (Recursive Links):")
            level2_sources = [c for c in relevant_content if c in result.level_2_content][:max_sources//2]
            for i, source in enumerate(level2_sources, 1):
                print(f"  {i}. {source.title or 'Untitled'} (Relevance: {source.relevance_score:.2f})")
                print(f"     URL: {source.url}")
                if source.content:
                    preview = source.content[:150].replace('\n', ' ')
                    if len(source.content) > 150:
                        preview += "..."
                    print(f"     Preview: {preview}")
                print()
    
    def print_summary_text(self, result: ResearchResult):
        """Print the research summary"""
        if not result.summary:
            return
        
        if self.console:
            self.console.print(Panel(
                result.summary,
                title="📋 [bold green]Research Summary[/bold green]",
                border_style="green",
                box=box.ROUNDED
            ))
        else:
            print("\n📋 Research Summary:")
            print("=" * 50)
            print(result.summary)
            print("=" * 50)
    
    def run_research_with_progress(self, query: str, max_results: int = 20, 
                                 max_level2: int = 10) -> ResearchResult:
        """Run research with a progress indicator"""
        researcher = DeepResearcher()
        
        if self.console:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=self.console
            ) as progress:
                
                # Add tasks
                search_task = progress.add_task("🔍 Searching DuckDuckGo...", total=100)
                crawl_task = progress.add_task("🕷️ Crawling Level 1 pages...", total=100)
                links_task = progress.add_task("🔗 Extracting links...", total=100)
                level2_task = progress.add_task("📄 Crawling Level 2 pages...", total=100)
                analysis_task = progress.add_task("📊 Analyzing content...", total=100)
                
                # Simulate progress updates
                progress.update(search_task, advance=50)
                time.sleep(0.5)
                
                # Actually run the research
                result = researcher.research(query, max_results, max_level2)
                
                # Complete all tasks
                progress.update(search_task, completed=100)
                progress.update(crawl_task, completed=100)
                progress.update(links_task, completed=100)
                progress.update(level2_task, completed=100)
                progress.update(analysis_task, completed=100)
                
                time.sleep(1)  # Show completed state
        else:
            print("🔍 Searching DuckDuckGo...")
            print("🕷️ Crawling Level 1 pages...")
            print("🔗 Extracting links...")
            print("📄 Crawling Level 2 pages...")
            print("📊 Analyzing content...")
            result = researcher.research(query, max_results, max_level2)
        
        return result
    
    def save_results_to_json(self, result: ResearchResult, output_path: str):
        """Save research results to JSON file"""
        import json
        from dataclasses import asdict
        
        try:
            # Convert dataclass to dict
            result_dict = asdict(result)
            
            # Convert datetime objects to strings
            result_dict['timestamp'] = result.timestamp.isoformat()
            for content in result_dict['level_1_content'] + result_dict['level_2_content']:
                content['scraped_at'] = content['scraped_at'].isoformat() if content['scraped_at'] else None
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result_dict, f, indent=2, ensure_ascii=False)
            
            self.print(f"✅ [green]Results saved to JSON:[/green] {output_path}")
            
        except Exception as e:
            self.print(f"❌ [red]Error saving JSON:[/red] {e}")
    
    def run(self, args):
        """Main CLI execution"""
        self.print_header()
        
        if args.verbose:
            import logging
            logging.getLogger().setLevel(logging.INFO)
        
        # Validate query
        if not args.query.strip():
            self.print("❌ [red]Error:[/red] Query cannot be empty")
            return 1
        
        # Show research configuration
        if self.console:
            config_table = Table(title="🛠️ Research Configuration", box=box.SIMPLE)
            config_table.add_column("Setting", style="cyan")
            config_table.add_column("Value", style="yellow")
            
            config_table.add_row("Query", args.query)
            config_table.add_row("Max Initial Results", str(args.max_results))
            config_table.add_row("Max Level 2 per Page", str(args.max_level2))
            config_table.add_row("Output Directory", args.output_dir)
            config_table.add_row("Generate PDF", "Yes" if args.pdf else "No")
            config_table.add_row("Save JSON", "Yes" if args.json else "No")
            
            self.console.print(config_table)
            self.console.print()
        else:
            print("\n🛠️ Research Configuration:")
            print(f"  Query: {args.query}")
            print(f"  Max Initial Results: {args.max_results}")
            print(f"  Max Level 2 per Page: {args.max_level2}")
            print(f"  Output Directory: {args.output_dir}")
            print(f"  Generate PDF: {'Yes' if args.pdf else 'No'}")
            print(f"  Save JSON: {'Yes' if args.json else 'No'}")
            print()
        
        try:
            # Create output directory
            Path(args.output_dir).mkdir(parents=True, exist_ok=True)
            
            # Run research
            self.print("🚀 [bold blue]Starting deep research...[/bold blue]\n")
            result = self.run_research_with_progress(args.query, args.max_results, args.max_level2)
            
            # Display results
            self.print("\n✅ [bold green]Research completed![/bold green]\n")
            self.print_summary_table(result)
            
            # Display summary text
            if result.summary:
                self.print_summary_text(result)
            
            # Display key findings
            if result.key_findings:
                self.print_key_findings(result)
            
            # Display sources
            self.print_sources_tree(result, max_sources=args.max_sources)
            
            # Generate PDF if requested
            pdf_path = None
            if args.pdf:
                self.print("\n📄 [bold blue]Generating PDF report...[/bold blue]")
                researcher = DeepResearcher()
                pdf_generator = researcher.pdf_generator
                
                # Generate filename
                import re
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_query = re.sub(r'[^a-zA-Z0-9\s]', '', args.query)[:50]
                safe_query = re.sub(r'\s+', '_', safe_query)
                pdf_filename = f"deep_research_{safe_query}_{timestamp}.pdf"
                pdf_path = os.path.join(args.output_dir, pdf_filename)
                
                success = pdf_generator.generate_pdf(result, pdf_path)
                if success:
                    self.print(f"✅ [green]PDF report saved:[/green] {pdf_path}")
                else:
                    self.print("❌ [red]Failed to generate PDF report[/red]")
            
            # Save JSON if requested
            if args.json:
                timestamp = result.timestamp.strftime("%Y%m%d_%H%M%S")
                safe_query = re.sub(r'[^a-zA-Z0-9\s]', '', args.query)[:50]
                safe_query = re.sub(r'\s+', '_', safe_query)
                json_filename = f"deep_research_{safe_query}_{timestamp}.json"
                json_path = os.path.join(args.output_dir, json_filename)
                self.save_results_to_json(result, json_path)
            
            # Final summary
            if self.console:
                final_panel = Panel(
                    f"[green]✅ Research completed successfully![/green]\n\n"
                    f"[cyan]📊 Statistics:[/cyan]\n"
                    f"  • Pages crawled: {result.total_pages_crawled}\n"
                    f"  • Links found: {result.total_links_found}\n"
                    f"  • Research time: {result.research_time:.1f} seconds\n"
                    f"  • Key findings: {len(result.key_findings)}\n\n"
                    f"[cyan]📁 Output files:[/cyan]\n" +
                    (f"  • PDF: {pdf_path}\n" if pdf_path else "") +
                    (f"  • JSON: {json_path}\n" if args.json else "") +
                    f"  • Output directory: {args.output_dir}",
                    title="🎉 [bold green]Research Complete[/bold green]",
                    border_style="green",
                    box=box.DOUBLE
                )
                self.console.print(final_panel)
            else:
                print("\n🎉 Research Complete!")
                print("=" * 50)
                print(f"✅ Research completed successfully!")
                print(f"📊 Pages crawled: {result.total_pages_crawled}")
                print(f"📊 Links found: {result.total_links_found}")
                print(f"📊 Research time: {result.research_time:.1f} seconds")
                print(f"📊 Key findings: {len(result.key_findings)}")
                if pdf_path:
                    print(f"📄 PDF: {pdf_path}")
                if args.json:
                    print(f"📄 JSON: {json_path}")
                print(f"📁 Output directory: {args.output_dir}")
                print("=" * 50)
            
            return 0
            
        except KeyboardInterrupt:
            self.print("\n❌ [red]Research interrupted by user[/red]")
            return 1
        except Exception as e:
            self.print(f"\n❌ [red]Error during research:[/red] {e}")
            if args.verbose:
                import traceback
                self.print(traceback.format_exc())
            return 1


def create_parser():
    """Create the argument parser"""
    parser = argparse.ArgumentParser(
        description="Deep Research CLI - Advanced web crawling and research tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "How to transition from software engineering to PhD?"
  %(prog)s "machine learning trends 2024" --max-results 30 --pdf
  %(prog)s "climate change solutions" --output-dir ./reports --json --verbose
  %(prog)s "startup funding strategies" --max-level2 15 --max-sources 20

For more information, visit: https://github.com/yourusername/deep-research
        """
    )
    
    # Required arguments
    parser.add_argument(
        "query",
        type=str,
        help="Research query to investigate"
    )
    
    # Optional arguments
    parser.add_argument(
        "--max-results",
        type=int,
        default=20,
        help="Maximum number of initial search results to crawl (default: 20)"
    )
    
    parser.add_argument(
        "--max-level2",
        type=int,
        default=10,
        help="Maximum number of level 2 links to follow per page (default: 10)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="research_output",
        help="Output directory for generated reports (default: research_output)"
    )
    
    parser.add_argument(
        "--pdf",
        action="store_true",
        help="Generate PDF report"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Save results as JSON file"
    )
    
    parser.add_argument(
        "--max-sources",
        type=int,
        default=10,
        help="Maximum number of sources to display in output (default: 10)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Deep Research CLI v1.0.0"
    )
    
    return parser


def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    cli = DeepResearchCLI()
    return cli.run(args)


if __name__ == "__main__":
    sys.exit(main())