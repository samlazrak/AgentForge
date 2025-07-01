# 🏗️ Agent Creator Architecture

This document provides a comprehensive overview of Agent Creator's architecture, design patterns, and system components.

## 🎯 Design Philosophy

Agent Creator is built on several key principles:

1. **Modularity**: Each component has a single responsibility and clear interfaces
2. **Extensibility**: Easy to add new agent types and capabilities
3. **Robustness**: Graceful handling of failures with fallback mechanisms
4. **Performance**: Optimized for Apple Silicon with MLX integration
5. **Usability**: Both programmatic API and intuitive web interface

## 📐 System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Creator Platform                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   Streamlit     │    │   Jupyter       │                │
│  │   Web App       │    │   Notebook      │                │
│  │   (app.py)      │    │   Interface     │                │
│  └─────────────────┘    └─────────────────┘                │
│           │                       │                        │
│           └───────────┬───────────┘                        │
│                       │                                    │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                 Agent Framework                         ││
│  │                                                         ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     ││
│  │  │ Research    │  │ Webscraper  │  │   Future    │     ││
│  │  │   Agent     │  │   Agent     │  │   Agents    │     ││
│  │  └─────────────┘  └─────────────┘  └─────────────┘     ││
│  │         │                │                │            ││
│  │         └────────────────┼────────────────┘            ││
│  │                          │                             ││
│  │  ┌─────────────────────────────────────────────────────┐││
│  │  │              Core Framework                         │││
│  │  │                                                     │││
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐│││
│  │  │  │  BaseAgent   │  │ AgentConfig  │  │  AgentTask   ││││
│  │  │  │   (Abstract) │  │              │  │              ││││
│  │  │  └──────────────┘  └──────────────┘  └──────────────┘│││
│  │  └─────────────────────────────────────────────────────┘││
│  │                          │                             ││
│  │  ┌─────────────────────────────────────────────────────┐││
│  │  │                 Utilities                           │││
│  │  │                                                     │││
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐│││
│  │  │  │     LLM      │  │    Search    │  │   Document   ││││
│  │  │  │  Interface   │  │   Engines    │  │  Generation  ││││
│  │  │  │     MLX      │  │  DuckDuckGo  │  │   PDF/IPYNB  ││││
│  │  │  └──────────────┘  └──────────────┘  └──────────────┘│││
│  │  └─────────────────────────────────────────────────────┘││
│  └─────────────────────────────────────────────────────────┘│
│                          │                                  │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              External Dependencies                      ││
│  │                                                         ││
│  │  MLX • Transformers • Selenium • BeautifulSoup         ││
│  │  DuckDuckGo Search • ReportLab • Streamlit             ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

## 🧱 Core Components

### 1. Base Agent Framework (`agent_creator/core/`)

#### BaseAgent (Abstract Base Class)
The foundation for all agents in the system.

```python
class BaseAgent(ABC):
    """Base class for all agents in the framework"""
    
    def __init__(self, config: AgentConfig)
    def execute_task(self, task: AgentTask) -> Any  # Abstract
    def create_task(self, description: str, parameters: Dict) -> str
    def run_task(self, task_id: str) -> Any
    def start(self) / stop(self)
```

**Key Features**:
- **Task Management**: Built-in task creation, tracking, and execution
- **Configuration Management**: Standardized configuration through AgentConfig
- **LLM Integration**: Automatic LLM interface initialization
- **Logging**: Integrated logging with agent-specific loggers
- **Lifecycle Management**: Start/stop functionality

#### AgentConfig
Configuration container for agents.

```python
@dataclass
class AgentConfig:
    name: str
    description: str
    capabilities: List[str]
    llm_config: Optional[LLMConfig]
    max_retries: int = 3
    timeout: int = 30
```

#### AgentTask
Represents a unit of work for an agent.

```python
@dataclass
class AgentTask:
    task_id: str
    description: str
    parameters: Dict[str, Any]
    created_at: datetime
    status: str  # pending, running, completed, failed
    result: Optional[Any]
    error: Optional[str]
```

### 2. Research Agent (`agent_creator/agents/research_agent.py`)

Specialized agent for AI-powered research tasks.

#### Core Capabilities
- **Web Search**: DuckDuckGo search integration
- **Content Analysis**: LLM-powered summarization and analysis
- **Citation Generation**: Academic citation formatting
- **Report Generation**: PDF and Jupyter notebook creation
- **Source Validation**: Relevance scoring and filtering

#### Key Classes

```python
@dataclass
class ResearchResult:
    query: str
    sources: List[Dict[str, Any]]
    summary: str
    citations: List[str]
    raw_data: List[Dict[str, Any]]
    timestamp: datetime

@dataclass
class Source:
    title: str
    url: str
    snippet: str
    content: str
    relevance_score: float
    citation: str
```

#### Research Pipeline
1. **Query Processing**: Parse and prepare search query
2. **Web Search**: Execute search using DuckDuckGo API
3. **Content Extraction**: Use webscraper for full content retrieval
4. **Analysis**: LLM-powered summarization and synthesis
5. **Citation Generation**: Format proper academic citations
6. **Report Generation**: Create PDF and notebook outputs

### 3. Webscraper Agent (`agent_creator/agents/webscraper_agent.py`)

Specialized agent for web content extraction.

#### Core Capabilities
- **Static Scraping**: requests + BeautifulSoup
- **Dynamic Scraping**: Selenium WebDriver
- **Batch Processing**: Multiple URL handling
- **Content Extraction**: Text, links, images, metadata
- **Error Handling**: Robust retry mechanisms

#### Key Classes

```python
@dataclass
class ScrapingResult:
    url: str
    success: bool
    title: str
    text: str
    html: str
    links: List[str]
    images: List[str]
    metadata: Dict[str, Any]
    error: Optional[str]
    timestamp: datetime
    response_time: float

@dataclass
class ScrapingConfig:
    timeout: int = 30
    max_retries: int = 3
    delay_between_requests: float = 1.0
    use_selenium: bool = False
    headless: bool = True
    user_agent: Optional[str] = None
    # ... additional configuration options
```

#### Scraping Pipeline
1. **URL Validation**: Validate and normalize URLs
2. **Method Selection**: Choose between requests or Selenium
3. **Content Retrieval**: Execute HTTP request or browser automation
4. **Content Parsing**: Extract text, links, images, metadata
5. **Result Packaging**: Create structured ScrapingResult
6. **Error Handling**: Retry logic and fallback mechanisms

### 4. LLM Interface (`agent_creator/utils/llm_interface.py`)

Provides unified interface to language models with MLX optimization.

#### Features
- **MLX Integration**: Optimized for Apple Silicon
- **HuggingFace Compatibility**: Support for any HF model
- **Fallback Mechanisms**: Graceful degradation when MLX unavailable
- **Configuration Management**: Flexible model configuration

```python
@dataclass
class LLMConfig:
    model_name: str = "microsoft/DialoGPT-medium"
    max_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    device: str = "auto"

class LLMInterface:
    def load_model(self) -> bool
    def generate_response(self, prompt: str, **kwargs) -> str
    def is_model_loaded(self) -> bool
    def get_model_info(self) -> Dict[str, Any]
```

## 🔄 Data Flow

### Research Workflow
```
User Query → Research Agent → Web Search → Webscraper Agent → 
Content Extraction → LLM Analysis → Citation Generation → 
Report Generation → PDF/Notebook Output
```

### Scraping Workflow
```
URL(s) → Webscraper Agent → Method Selection → Content Retrieval → 
HTML Parsing → Content Extraction → Metadata Collection → 
ScrapingResult → User/Research Agent
```

### Agent Communication
```
Research Agent ←→ Webscraper Agent
       ↓
   LLM Interface
       ↓
   MLX/HuggingFace Models
```

## 🎨 User Interfaces

### 1. Streamlit Web Application (`app.py`)

**Features**:
- **Agent Control Panel**: Initialize, start, stop agents
- **Research Interface**: Query input, configuration, progress tracking
- **Scraping Interface**: URL input, batch processing, result display
- **Analytics Dashboard**: Results visualization and statistics
- **Export Options**: Download generated files

**Architecture**:
- **Session State Management**: Persistent agent instances
- **Real-time Updates**: Progress bars and status indicators
- **Error Handling**: User-friendly error messages
- **Responsive Design**: Multi-column layout with tabs

### 2. Jupyter Notebook Interface

**Components**:
- **Setup Cells**: Import and initialization
- **Example Workflows**: Step-by-step demonstrations
- **Interactive Widgets**: Configuration and control
- **Visualization**: Results plotting and analysis

## 🔧 Extension Points

### Adding New Agent Types

1. **Create Agent Class**: Inherit from `BaseAgent`
2. **Implement execute_task()**: Define task execution logic
3. **Define Capabilities**: Specify agent capabilities
4. **Add Configuration**: Create agent-specific config classes
5. **Register in Framework**: Add imports and UI integration

Example:
```python
class CustomAgent(BaseAgent):
    def execute_task(self, task: AgentTask) -> Any:
        # Custom implementation
        pass
    
    def custom_capability(self, param: str) -> str:
        # Agent-specific method
        pass
```

### Adding New LLM Models

1. **Update LLMConfig**: Add model-specific parameters
2. **Implement Model Loading**: Add model loading logic
3. **Handle Model-Specific Features**: Tokenization, generation parameters
4. **Add Fallback Support**: Ensure graceful degradation

### Adding New Output Formats

1. **Create Generator Class**: Implement format-specific generation
2. **Update Agent Methods**: Add generation options
3. **Extend UI**: Add format selection options
4. **Handle Dependencies**: Manage format-specific libraries

## 🛡️ Error Handling & Resilience

### Failure Modes & Recovery

1. **Network Failures**:
   - Automatic retry with exponential backoff
   - Fallback to cached/mock data
   - User notification with recovery options

2. **Model Loading Failures**:
   - Fallback to simpler models
   - Mock response generation
   - Graceful degradation of features

3. **Scraping Failures**:
   - Method switching (requests ↔ Selenium)
   - User agent rotation
   - Rate limiting compliance

4. **Resource Exhaustion**:
   - Content length limiting
   - Memory management
   - Task queuing and prioritization

### Monitoring & Logging

- **Structured Logging**: JSON-formatted logs with context
- **Performance Metrics**: Response times, success rates
- **Error Tracking**: Detailed error context and stack traces
- **Resource Monitoring**: Memory usage, task queue status

## 🚀 Performance Considerations

### Optimization Strategies

1. **MLX Integration**: Apple Silicon optimization for LLM inference
2. **Async Operations**: Non-blocking I/O for web operations
3. **Content Caching**: Avoid redundant web requests
4. **Batch Processing**: Efficient multi-URL handling
5. **Memory Management**: Content size limiting and cleanup

### Scalability

- **Horizontal Scaling**: Multiple agent instances
- **Task Distribution**: Load balancing across agents
- **Resource Pooling**: Shared browser instances
- **Caching Strategies**: Result caching and reuse

## 🔮 Future Architecture Considerations

### Planned Enhancements

1. **Distributed Architecture**: Multi-node deployment
2. **Plugin System**: Dynamic capability loading
3. **Advanced Analytics**: ML-powered result analysis
4. **Real-time Collaboration**: Multi-user support
5. **API Gateway**: RESTful API for external integration

### Technology Evolution

- **Model Upgrades**: Support for larger, more capable models
- **Framework Integration**: Support for additional ML frameworks
- **Cloud Deployment**: Containerization and cloud-native features
- **Security Enhancements**: Authentication, authorization, audit logging

---

This architecture provides a solid foundation for current functionality while remaining flexible enough to support future enhancements and scaling requirements.