#!/bin/bash

# Agent Creator Setup Script
# This script helps set up the Agent Creator project locally

set -e

echo "🤖 Agent Creator Setup Script"
echo "=============================="

# Check if we're in a conda environment
if [[ -z "$CONDA_DEFAULT_ENV" ]]; then
    echo "⚠️  Warning: You're not in a conda environment."
    echo "   It's recommended to use conda for dependency management."
    echo "   Consider running: conda activate base"
    echo ""
fi

# Check Python version
python_version=$(python --version 2>&1 | cut -d' ' -f2)
echo "🐍 Python version: $python_version"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run tests
echo "🧪 Running tests..."
python -m pytest tests/ -v

# Check imports
echo "✅ Testing imports..."
python -c "from agent_creator import ResearchAgent, WebscraperAgent; print('✅ All imports successful')"

echo ""
echo "🎉 Setup complete! You can now:"
echo "   • Run the Streamlit app: streamlit run app.py"
echo "   • Start JupyterLab: jupyter lab"
echo "   • Open the demo notebook: demo_notebook.ipynb"
echo "   • Run tests: python -m pytest tests/"
echo ""
echo "📖 Check the README.md for more information!" 