#!/bin/bash
# Setup environment for rv-cli project

# Detect architecture for PostgreSQL path
if [[ $(uname -m) == 'arm64' ]]; then
  # Apple Silicon Mac
  PG_PATH="/opt/homebrew/opt/postgresql@16/bin"
else
  # Intel Mac
  PG_PATH="/usr/local/opt/postgresql@16/bin"
fi

# Add PostgreSQL to PATH
echo "Adding PostgreSQL to your PATH..."
export PATH="$PG_PATH:$PATH"

# Suggest adding to shell profile
SHELL_PROFILE=""
if [[ $SHELL == *"zsh"* ]]; then
  SHELL_PROFILE="$HOME/.zshrc"
elif [[ $SHELL == *"bash"* ]]; then
  SHELL_PROFILE="$HOME/.bash_profile"
fi

if [ -n "$SHELL_PROFILE" ]; then
  echo ""
  echo "To permanently add PostgreSQL to your PATH, add this line to $SHELL_PROFILE:"
  echo ""
  echo "export PATH=\"$PG_PATH:\$PATH\""
  echo ""
fi

# Check if psql is now available
if command -v psql >/dev/null 2>&1; then
  echo "PostgreSQL command-line tools are now available!"
  echo "PostgreSQL version: $(psql --version)"
else
  echo "WARNING: PostgreSQL command-line tools are still not in your PATH."
  echo "You may need to install PostgreSQL first using:"
  echo "  brew install postgresql@16"
  echo "  brew services start postgresql@16"
fi

# Source this script with:
# source scripts/setup_env.sh 