# 📖 API Reference

Complete API documentation for Agent Creator framework.

## 🏗️ Core Framework

### BaseAgent

Abstract base class for all agents in the framework.

#### Constructor
```python
BaseAgent(config: AgentConfig)
```

**Parameters:**
- `config` (AgentConfig): Configuration object for the agent

#### Methods

##### `execute_task(task: AgentTask) -> Any`
**Abstract method** - Execute a specific task. Must be implemented by subclasses.

##### `create_task(description: str, parameters: Optional[Dict[str, Any]] = None) -> str`
Create a new task for the agent.

**Parameters:**
- `description` (str): Task description
- `parameters` (Optional[Dict]): Task parameters

**Returns:** Task ID (str)

##### `run_task(task_id: str) -> Any`
Run a specific task by ID.

**Parameters:**
- `task_id` (str): ID of the task to run

**Returns:** Task result

##### `get_task_status(task_id: str) -> Dict[str, Any]`
Get the status of a task.

**Returns:** Dictionary containing task status information

##### `list_tasks() -> List[Dict[str, Any]]`
List all tasks for this agent.

**Returns:** List of task information dictionaries

##### `get_capabilities() -> List[str]`
Get the capabilities of this agent.

**Returns:** List of capability strings

##### `get_agent_info() -> Dict[str, Any]`
Get comprehensive information about this agent.

**Returns:** Agent information dictionary

##### `start()` / `stop()`
Start/stop the agent.

### AgentConfig

Configuration dataclass for agents.

```python
@dataclass
class AgentConfig:
    name: str
    description: str
    capabilities: List[str] = field(default_factory=list)
    llm_config: Optional[LLMConfig] = None
    max_retries: int = 3
    timeout: int = 30
```

### AgentTask

Task representation dataclass.

```python
@dataclass
class AgentTask:
    task_id: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[Any] = None
    error: Optional[str] = None
```

## 🔬 Research Agent

### ResearchAgent

Specialized agent for AI-powered research tasks.

#### Constructor
```python
ResearchAgent(config: Optional[AgentConfig] = None)
```

#### Methods

##### `research_topic(query: str, max_results: int = 10, generate_pdf: bool = True, generate_notebook: bool = True) -> Dict[str, Any]`
Perform comprehensive research on a topic.

**Parameters:**
- `query` (str): Research query
- `max_results` (int): Maximum search results to process
- `generate_pdf` (bool): Whether to generate PDF report
- `generate_notebook` (bool): Whether to generate Jupyter notebook

**Returns:** Dictionary containing:
- `research_result` (ResearchResult): Research findings
- `files_generated` (List[str]): Paths to generated files

##### `set_webscraper_agent(webscraper_agent: WebscraperAgent)`
Connect a webscraper agent for enhanced content extraction.

### ResearchResult

Result dataclass for research operations.

```python
@dataclass
class ResearchResult:
    query: str
    sources: List[Dict[str, Any]] = field(default_factory=list)
    summary: str = ""
    citations: List[str] = field(default_factory=list)
    raw_data: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
```

### Source

Source representation dataclass.

```python
@dataclass
class Source:
    title: str
    url: str
    snippet: str
    content: str = ""
    relevance_score: float = 0.0
    citation: str = ""
```

## 🕷️ Webscraper Agent

### WebscraperAgent

Specialized agent for web content extraction.

#### Constructor
```python
WebscraperAgent(config: Optional[AgentConfig] = None, scraping_config: Optional[ScrapingConfig] = None)
```

#### Methods

##### `scrape_url(url: str, use_selenium: bool = False) -> ScrapingResult`
Scrape content from a single URL.

**Parameters:**
- `url` (str): URL to scrape
- `use_selenium` (bool): Use Selenium for dynamic content

**Returns:** ScrapingResult object

##### `scrape_multiple_urls(urls: List[str], use_selenium: bool = False) -> List[ScrapingResult]`
Scrape content from multiple URLs.

**Parameters:**
- `urls` (List[str]): List of URLs to scrape
- `use_selenium` (bool): Use Selenium for dynamic content

**Returns:** List of ScrapingResult objects

##### `extract_links(url: str) -> List[str]`
Extract all links from a page.

**Parameters:**
- `url` (str): URL to extract links from

**Returns:** List of extracted URLs

### ScrapingResult

Result dataclass for scraping operations.

```python
@dataclass
class ScrapingResult:
    url: str
    success: bool = False
    title: str = ""
    text: str = ""
    html: str = ""
    links: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    response_time: float = 0.0
```

### ScrapingConfig

Configuration dataclass for web scraping.

```python
@dataclass
class ScrapingConfig:
    timeout: int = 30
    max_retries: int = 3
    delay_between_requests: float = 1.0
    use_selenium: bool = False
    headless: bool = True
    user_agent: Optional[str] = None
    follow_redirects: bool = True
    extract_links: bool = True
    extract_images: bool = True
    max_content_length: int = 1000000  # 1MB
```

## 🤖 LLM Interface

### LLMInterface

Interface for language model interactions with MLX optimization.

#### Constructor
```python
LLMInterface(config: Optional[LLMConfig] = None)
```

#### Methods

##### `load_model() -> bool`
Load the MLX model and tokenizer.

**Returns:** True if successful, False otherwise

##### `generate_response(prompt: str, **kwargs) -> str`
Generate a response using the loaded model.

**Parameters:**
- `prompt` (str): Input prompt
- `**kwargs`: Additional generation parameters

**Returns:** Generated response text

##### `is_model_loaded() -> bool`
Check if model is loaded.

**Returns:** Boolean indicating model status

##### `get_model_info() -> Dict[str, Any]`
Get information about the loaded model.

**Returns:** Model information dictionary

### LLMConfig

Configuration dataclass for language models.

```python
@dataclass
class LLMConfig:
    model_name: str = "microsoft/DialoGPT-medium"
    max_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    device: str = "auto"
```

## 🎯 Usage Examples

### Basic Research Agent Usage

```python
from agent_creator import ResearchAgent
from agent_creator.core.base_agent import AgentConfig

# Create configuration
config = AgentConfig(
    name="MyResearchAgent",
    description="AI research assistant",
    capabilities=["web_search", "content_analysis"]
)

# Initialize agent
agent = ResearchAgent(config)
agent.start()

# Perform research
result = agent.research_topic(
    query="Quantum computing applications",
    max_results=5,
    generate_pdf=True
)

# Access results
summary = result['research_result'].summary
sources = result['research_result'].sources
files = result['files_generated']

agent.stop()
```

### Basic Webscraper Usage

```python
from agent_creator import WebscraperAgent
from agent_creator.agents.webscraper_agent import ScrapingConfig

# Configure scraping
scraping_config = ScrapingConfig(
    timeout=30,
    delay_between_requests=1.0,
    extract_links=True
)

# Initialize agent
agent = WebscraperAgent(scraping_config=scraping_config)
agent.start()

# Scrape single URL
result = agent.scrape_url("https://example.com")
if result.success:
    print(f"Title: {result.title}")
    print(f"Content: {result.text[:200]}...")

agent.stop()
```

### Combined Usage

```python
from agent_creator import ResearchAgent, WebscraperAgent

# Initialize both agents
research_agent = ResearchAgent()
webscraper_agent = WebscraperAgent()

# Connect for enhanced functionality
research_agent.set_webscraper_agent(webscraper_agent)

# Start agents
research_agent.start()
webscraper_agent.start()

# Enhanced research with deep content extraction
result = research_agent.research_topic(
    query="AI trends 2024",
    max_results=8
)

# Stop agents
research_agent.stop()
webscraper_agent.stop()
```

## 🔧 Configuration Examples

### Custom LLM Configuration

```python
from agent_creator.utils.llm_interface import LLMConfig

llm_config = LLMConfig(
    model_name="microsoft/DialoGPT-large",
    max_tokens=1024,
    temperature=0.8,
    top_p=0.95
)

agent_config = AgentConfig(
    name="CustomAgent",
    description="Agent with custom LLM",
    llm_config=llm_config
)
```

### Advanced Scraping Configuration

```python
from agent_creator.agents.webscraper_agent import ScrapingConfig

scraping_config = ScrapingConfig(
    timeout=60,
    max_retries=5,
    delay_between_requests=2.0,
    use_selenium=True,
    headless=False,
    user_agent="Custom Bot 1.0",
    max_content_length=5000000  # 5MB
)
```

## ❌ Error Handling

### Common Exceptions

- **ValueError**: Invalid parameters or configuration
- **ImportError**: Missing dependencies  
- **TimeoutError**: Request timeouts
- **WebDriverException**: Selenium-related errors

### Error Handling Example

```python
try:
    result = agent.research_topic("AI research")
except ValueError as e:
    print(f"Configuration error: {e}")
except TimeoutError as e:
    print(f"Request timeout: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Checking Dependencies

```python
# Check if optional dependencies are available
if agent.ddgs_available:
    print("DuckDuckGo search available")
if agent.selenium_available:
    print("Selenium web scraping available")
if agent.pdf_available:
    print("PDF generation available")
```

## 📊 Return Value Formats

### Research Result Structure

```python
{
    'research_result': ResearchResult(
        query="...",
        sources=[...],
        summary="...",
        citations=[...],
        raw_data=[...],
        timestamp=datetime.now()
    ),
    'files_generated': ["report.pdf", "analysis.ipynb"]
}
```

### Scraping Result Structure

```python
ScrapingResult(
    url="https://example.com",
    success=True,
    title="Page Title",
    text="Extracted text content...",
    html="<html>...</html>",
    links=["https://link1.com", "https://link2.com"],
    images=["https://img1.jpg", "https://img2.png"],
    metadata={"description": "...", "keywords": "..."},
    error=None,
    timestamp=datetime.now(),
    response_time=1.23
)
```

---

For more examples and detailed usage patterns, see the [Examples Documentation](EXAMPLES.md).