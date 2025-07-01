"""Setup configuration for the Deep Research System package."""

from setuptools import setup, find_packages
import os

# Read long description from README
def read_long_description():
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "A comprehensive web research tool with recursive crawling capabilities."

# Read requirements from requirements-core.txt
def read_requirements():
    requirements = []
    try:
        with open("requirements-core.txt", "r", encoding="utf-8") as fh:
            requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        # Fallback to core requirements
        requirements = [
            "duckduckgo-search>=3.9.0",
            "requests>=2.31.0", 
            "beautifulsoup4>=4.12.0",
            "reportlab>=4.0.0",
        ]
    return requirements

setup(
    name="deep-researcher",
    version="1.0.0",
    author="Deep Research System",
    author_email="",
    description="A comprehensive web research tool with recursive crawling capabilities",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/deep-researcher",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Researchers",
        "Intended Audience :: Information Technology",
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
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "web": ["streamlit>=1.28.0"],
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-mock>=3.12.0",
            "pytest-cov>=4.1.0",
        ],
        "full": [
            "streamlit>=1.28.0",
            "selenium>=4.15.0",
            "scrapy>=2.11.0",
            "fake-useragent>=1.4.0",
            "fpdf2>=2.7.0",
            "pdfplumber>=0.11.0",
            "python-docx>=1.1.0",
            "markdown>=3.5.0",
            "aiohttp>=3.9.0",
            "httpx>=0.25.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "deep-research=deep_researcher.cli.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="web scraping research crawling duckduckgo pdf report generation",
    project_urls={
        "Bug Reports": "https://github.com/your-username/deep-researcher/issues",
        "Source": "https://github.com/your-username/deep-researcher",
        "Documentation": "https://github.com/your-username/deep-researcher/blob/main/README.md",
    },
)