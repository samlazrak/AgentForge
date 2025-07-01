# Agent Creator

A toolkit for building specialized AI agents focused on research, web scraping, and data analysis. I built this because I got tired of switching between different tools for research projects - it handles the tedious parts of information gathering and analysis so you don't have to.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MLX](https://img.shields.io/badge/MLX-optimized-green.svg)](https://ml-explore.github.io/mlx/)
[![Streamlit](https://img.shields.io/badge/Streamlit-web_app-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What It Does

This is essentially three different tools rolled into one:

1. **Research Agent** - Takes a question, searches the web, reads through results, and writes up a summary with proper citations
2. **Web Scraper** - Pulls content from websites (both simple and JavaScript-heavy ones) and organizes it
3. **Data Analysis Agent** - Loads your data files, runs analysis, creates visualizations, and explains what it found

There's a web interface built with Streamlit that makes everything point-and-click, plus a Python API if you want to integrate it into your own code.

## Web Interface

The Streamlit interface has three tabs that mirror the three agents. Upload files by dragging and dropping, enter URLs or search queries, and everything runs in the browser. Results can be downloaded in various formats.

The interface shows progress in real-time, so you can see what's happening when the agents are working through large tasks.

## File Format Support

- **Standard formats**: CSV, Excel (.xlsx/.xls), JSON, TSV
- **ATF files**: These are common in neuroscience labs for electrophysiology recordings. Most tools can't read them properly, but this handles the metadata and multiple data columns correctly.

## Performance Notes

If you're on Apple Silicon (M1/M2/M3), the MLX optimization makes AI inference significantly faster. On other hardware, it falls back to standard methods automatically.

The web scraper includes rate limiting so you don't hammer servers, and the data analysis can handle reasonably large files without running out of memory.

## Architecture
