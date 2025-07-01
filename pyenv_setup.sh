#!/bin/bash
# Pyenv Setup Script for Agent-Creator Project
# This script installs and configures pyenv with Python 3.13.3

set -e

echo "Setting up pyenv for Agent-Creator project..."

# Check if pyenv is already installed
if command -v pyenv >/dev/null 2>&1; then
    echo "✓ pyenv is already installed"
else
    echo "Installing pyenv..."
    curl https://pyenv.run | bash
fi

# Add pyenv to shell configuration if not already present
BASHRC="$HOME/.bashrc"
if ! grep -q "PYENV_ROOT" "$BASHRC"; then
    echo "Adding pyenv configuration to ~/.bashrc..."
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> "$BASHRC"
    echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> "$BASHRC"
    echo 'eval "$(pyenv init - bash)"' >> "$BASHRC"
fi

# Source the configuration for current session
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - bash)"

# Install system dependencies for building Python (Ubuntu/Debian)
if command -v apt >/dev/null 2>&1; then
    echo "Installing build dependencies..."
    sudo apt update
    sudo apt install -y build-essential libssl-dev zlib1g-dev libbz2-dev \
        libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev \
        libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev
fi

# Install Python 3.13.3 if not already installed
if ! pyenv versions | grep -q "3.13.3"; then
    echo "Installing Python 3.13.3..."
    pyenv install 3.13.3
else
    echo "✓ Python 3.13.3 is already installed"
fi

# Set local Python version for the project
echo "Setting Python 3.13.3 as local version for this project..."
pyenv local 3.13.3

# Verify installation
echo "Verifying installation..."
python --version
python -m pip --version

echo "✓ Pyenv setup complete!"
echo "Python 3.13.3 is now active for this project."
echo ""
echo "To activate pyenv in a new shell session, run:"
echo "source ~/.bashrc"
echo ""
echo "Or restart your shell."