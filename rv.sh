#!/bin/bash
# rv-cli runner script

# Load environment variables
if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

# Run the CLI app
poetry run python -m app.cli.main "$@" 