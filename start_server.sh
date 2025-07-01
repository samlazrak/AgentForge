#!/bin/bash

# Agent Creator - Server Startup Script
# This script organizes research files and starts the Streamlit server

echo "🤖 Agent Creator - Server Startup"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found in current directory"
    echo "💡 Make sure you're in the Agent-Creator project directory"
    exit 1
fi

# Organize research files if the script exists
if [ -f "move_research_files.py" ]; then
    echo "🗂️  Organizing research files..."
    python3 move_research_files.py
else
    echo "⚠️  move_research_files.py not found, skipping file organization"
fi

echo ""
echo "🚀 Starting Agent Creator Streamlit application..."
echo "================================================="
echo "📱 The app will open in your browser automatically"
echo "🔗 Manual URL: http://localhost:8501"
echo "⏹️  Press Ctrl+C to stop the server"
echo "================================================="

# Start Streamlit
exec streamlit run app.py \
    --server.address localhost \
    --server.port 8501 \
    --browser.gatherUsageStats false 