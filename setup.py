#!/usr/bin/env python3
"""
Setup script for Deep Research package.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements from requirements.txt, excluding streamlit and jupyter dependencies
def read_requirements():
    requirements = []
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith("#"):
                # Skip streamlit, jupyter, and MLX dependencies for core package
                if not any(skip in line.lower() for skip in [
                    'streamlit', 'gradio', 'jupyter', 'ipykernel', 'ipywidgets',
                    'mlx', 'matplotlib', 'seaborn', 'plotly', 'scikit-learn',
                    'selenium', 'scrapy', 'fake-useragent', 'pytest', 'aiohttp', 'httpx'
                ]):
                    requirements.append(line)
    
    # Add rich as a required dependency for CLI
    requirements.append("rich>=13.0.0")
    requirements.append("click>=8.0.0")  # Alternative CLI framework
    
    return requirements

setup(
    name="deep-research",
    version="1.0.0",
    author="Deep Research Team",
    author_email="research@example.com",
    description="Advanced web crawling and research tool with recursive link following",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/deep-research",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Researchers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-mock>=3.12.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "full": [
            "streamlit>=1.28.0",
            "gradio",
            "jupyter>=1.1.0",
            "ipykernel>=6.29.0",
            "ipywidgets>=8.1.0",
            "matplotlib>=3.7.0",
            "seaborn>=0.12.0",
            "plotly>=5.15.0",
            "scikit-learn>=1.3.0",
            "selenium>=4.15.0",
            "scrapy>=2.11.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "deep-research=cli:main",
            "dr=cli:main",  # Short alias
        ],
    },
    package_data={
        "": ["*.md", "*.txt", "*.yaml", "*.yml"],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "research", "web-crawling", "web-scraping", "duckduckgo", 
        "search", "analysis", "pdf-generation", "cli", "automation"
    ],
    project_urls={
        "Bug Reports": "https://github.com/yourusername/deep-research/issues",
        "Source": "https://github.com/yourusername/deep-research",
        "Documentation": "https://github.com/yourusername/deep-research#readme",
    },
)