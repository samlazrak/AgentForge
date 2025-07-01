# Agent Creator - Quick Start Guide

Welcome to Agent Creator! This guide will help you get up and running quickly.

## Prerequisites

- Python 3.13+ (recommended to use conda)
- macOS with Apple Silicon (for MLX support)

## Quick Setup

1. **Clone and navigate to the repository:**
   ```bash
   git clone <repository-url>
   cd Agent-Creator
   ```

2. **Activate your conda environment:**
   ```bash
   conda activate base  # or your preferred environment
   ```

3. **Run the setup script:**
   ```bash
   ./setup.sh
   ```

   Or manually install:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Applications

### 1. Streamlit Web App
Launch the interactive web interface:
```bash
streamlit run app.py
```
Then open your browser to `http://localhost:8501`

### 2. JupyterLab
Start JupyterLab with the demo notebook:
```bash
jupyter lab
```
Then open `demo_notebook.ipynb` to see the agents in action.

### 3. Command Line Usage
```python
from agent_creator import ResearchAgent, WebscraperAgent
from agent_creator.core.base_agent import AgentConfig

# Create and start a research agent
config = AgentConfig(name="MyAgent", description="Research assistant")
agent = ResearchAgent(config)
agent.start()

# Create a research task
task_id = agent.create_task(
    description="Research AI trends",
    parameters={"type": "research", "query": "latest AI trends 2024"}
)

# Execute the task
result = agent.run_task(task_id)
print(result.summary)
```

## Key Features

- **Research Agent**: AI-powered web search and content analysis
- **Webscraper Agent**: Advanced web scraping with content extraction
- **MLX Integration**: Optimized for Apple Silicon
- **Multiple Interfaces**: Streamlit web app, Jupyter notebooks, CLI
- **PDF/Notebook Generation**: Export research results

## Testing

Run the test suite to verify everything is working:
```bash
python -m pytest tests/ -v
```

## Troubleshooting

### Common Issues

1. **Sentencepiece build errors**: 
   - Install via conda: `conda install -c conda-forge sentencepiece`
   - Or use the setup script which handles this

2. **Import errors**:
   - Ensure you're in the correct conda environment
   - Check that all dependencies are installed: `pip install -r requirements.txt`

3. **MLX not working**:
   - MLX requires Apple Silicon (M1/M2/M3) Macs
   - Ensure you have the latest macOS version

### Getting Help

- Check the main README.md for detailed documentation
- Run tests to verify your installation
- Check the demo notebook for usage examples

## Next Steps

1. Explore the Streamlit interface
2. Run through the demo notebook
3. Check out the test files for more usage examples
4. Read the main documentation in README.md

Happy researching! 🤖✨ 