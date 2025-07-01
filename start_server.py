#!/usr/bin/env python3
"""
Server startup script for Agent Creator Streamlit application.
This script will:
1. Run the research file organization script
2. Start the Streamlit server
3. Handle graceful shutdown
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

def run_move_research_files():
    """Run the move_research_files.py script to organize files."""
    print("🗂️  Organizing research files...")
    try:
        result = subprocess.run([sys.executable, "move_research_files.py"], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        if result.stderr:
            print("Warnings:", result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Error organizing research files: {e}")
        print("Output:", e.stdout)
        print("Error:", e.stderr)
    except FileNotFoundError:
        print("⚠️  move_research_files.py not found, skipping file organization")

def start_streamlit():
    """Start the Streamlit application."""
    print("\n🚀 Starting Agent Creator Streamlit application...")
    print("=" * 60)
    print("📱 The app will open in your browser automatically")
    print("🔗 Manual URL: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        # Start streamlit with app.py
        cmd = [sys.executable, "-m", "streamlit", "run", "app.py", 
               "--server.address", "localhost", 
               "--server.port", "8501",
               "--browser.gatherUsageStats", "false"]
        
        return subprocess.Popen(cmd)
        
    except FileNotFoundError:
        print("❌ Error: Streamlit is not installed.")
        print("💡 Install it with: pip install streamlit")
        return None
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")
        return None

def main():
    """Main function."""
    print("🤖 Agent Creator - Server Startup")
    print("=" * 40)
    
    # Check if app.py exists
    if not Path("app.py").exists():
        print("❌ Error: app.py not found in current directory")
        print("💡 Make sure you're in the Agent-Creator project directory")
        return 1
    
    # Organize research files first
    run_move_research_files()
    
    # Start Streamlit server
    streamlit_process = start_streamlit()
    
    if streamlit_process is None:
        return 1
    
    try:
        # Wait for the process to complete
        streamlit_process.wait()
    except KeyboardInterrupt:
        print("\n\n⏹️  Shutting down server...")
        streamlit_process.terminate()
        
        # Give it a moment to terminate gracefully
        try:
            streamlit_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print("🔪 Force killing server...")
            streamlit_process.kill()
            streamlit_process.wait()
        
        print("✅ Server stopped successfully")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 