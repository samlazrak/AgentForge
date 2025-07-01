# Pyenv Setup for Agent-Creator

This project uses **pyenv** to manage Python versions and ensure consistent development environments across different systems.

## What is Pyenv?

Pyenv is a Python version management tool that allows you to:
- Install and switch between multiple Python versions
- Set different Python versions for different projects
- Avoid conflicts between system Python and project-specific Python versions

## Quick Setup

### Option 1: Automated Setup (Recommended)

Run the provided setup script:

```bash
./pyenv_setup.sh
```

This script will:
1. Install pyenv if not already installed
2. Install required build dependencies
3. Install Python 3.13.3
4. Configure your shell
5. Set Python 3.13.3 as the local version for this project

### Option 2: Manual Setup

1. **Install pyenv:**
   ```bash
   curl https://pyenv.run | bash
   ```

2. **Add pyenv to your shell configuration:**
   ```bash
   echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
   echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
   echo 'eval "$(pyenv init - bash)"' >> ~/.bashrc
   ```

3. **Restart your shell or source the configuration:**
   ```bash
   source ~/.bashrc
   ```

4. **Install build dependencies (Ubuntu/Debian):**
   ```bash
   sudo apt update
   sudo apt install -y build-essential libssl-dev zlib1g-dev libbz2-dev \
       libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev \
       libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev
   ```

5. **Install Python 3.13.3:**
   ```bash
   pyenv install 3.13.3
   ```

6. **Set Python version for this project:**
   ```bash
   pyenv local 3.13.3
   ```

## Verification

After setup, verify everything is working:

```bash
python --version    # Should output: Python 3.13.3
pip --version      # Should show pip for Python 3.13.3
pyenv versions     # Should show 3.13.3 as active
```

## Project Configuration

The project includes a `.python-version` file that automatically activates Python 3.13.3 when you enter the project directory (if pyenv is properly configured).

## Installing Project Dependencies

Once pyenv is set up, install the project dependencies:

```bash
pip install -r requirements.txt
```

## Troubleshooting

### Common Issues

1. **"pyenv: command not found"**
   - Make sure pyenv is added to your PATH
   - Restart your shell or run `source ~/.bashrc`

2. **Python build failures**
   - Make sure all build dependencies are installed
   - Check the [pyenv troubleshooting guide](https://github.com/pyenv/pyenv/wiki/Common-build-problems)

3. **SSL certificate errors**
   - Make sure `libssl-dev` is installed
   - Try rebuilding Python after installing dependencies

### Additional Resources

- [Pyenv Documentation](https://github.com/pyenv/pyenv)
- [Common Build Problems](https://github.com/pyenv/pyenv/wiki/Common-build-problems)

## Why Python 3.13.3?

This project uses Python 3.13.3 because:
- It includes the latest performance improvements
- Has enhanced error messages and debugging features
- Supports all the modern Python features used in this project
- Provides compatibility with all dependencies in `requirements.txt`