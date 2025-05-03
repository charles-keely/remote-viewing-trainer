#!/bin/bash
# Complete setup script for rv-cli

set -e  # Exit on any error

echo "========== RV-CLI Setup =========="
echo ""

# 1. Check Python version
PYTHON_VERSION=$(python3 --version)
echo "Using $PYTHON_VERSION"

if ! [[ $PYTHON_VERSION == *"3.12"* ]]; then
  echo "Warning: This project is designed for Python 3.12+. You're using $(python3 --version)"
  echo "You may continue, but some features might not work correctly."
  read -p "Continue anyway? [y/N] " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Setup aborted. Please install Python 3.12+ and try again."
    exit 1
  fi
fi

# 2. Install Poetry if not installed
if ! command -v poetry &> /dev/null; then
  echo "Poetry not found. Installing..."
  curl -sSL https://install.python-poetry.org | python3 -
  source "$HOME/.poetry/env"
else
  echo "Poetry is already installed: $(poetry --version)"
fi

# 3. Install project dependencies
echo "Installing project dependencies with Poetry..."
poetry install

# 4. Check for PostgreSQL
if ! command -v psql &> /dev/null; then
  echo "PostgreSQL command-line tools not found."
  
  # Detect Mac architecture for proper path
  if [[ $(uname -m) == 'arm64' ]]; then
    # Apple Silicon Mac
    PG_PATH="/opt/homebrew/opt/postgresql@16/bin"
    PG_PATH_EXPORT='export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"'
  else
    # Intel Mac
    PG_PATH="/usr/local/opt/postgresql@16/bin"
    PG_PATH_EXPORT='export PATH="/usr/local/opt/postgresql@16/bin:$PATH"'
  fi
  
  echo "Adding PostgreSQL PATH export to shell profile..."
  if [ -f "$HOME/.zshrc" ]; then
    echo $PG_PATH_EXPORT >> "$HOME/.zshrc"
    echo "Added to ~/.zshrc"
  elif [ -f "$HOME/.bash_profile" ]; then
    echo $PG_PATH_EXPORT >> "$HOME/.bash_profile"
    echo "Added to ~/.bash_profile"
  else
    echo $PG_PATH_EXPORT >> "$HOME/.profile"
    echo "Added to ~/.profile"
  fi
  
  echo "You need to install PostgreSQL. Run these commands:"
  echo "  brew install postgresql@16"
  echo "  brew services start postgresql@16"
  echo ""
  echo "Then start a new terminal or run: source ~/.zshrc"
  echo "After that, run: make db-init"
else
  echo "PostgreSQL is installed: $(psql --version)"
  
  # 5. Set up environment file if not exists
  if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env and add your OpenAI API key"
  else
    echo ".env file already exists"
  fi
  
  # 6. Attempt to initialize database
  echo "Initializing database..."
  make db-init || {
    echo "Database initialization failed."
    echo "You may need to start PostgreSQL with: brew services start postgresql@16"
    echo "Then try again with: make db-init"
  }
fi

echo ""
echo "Setup completed!"
echo "To run the API server: make dev"
echo "To run a remote viewing session: ./rv new"
echo "" 