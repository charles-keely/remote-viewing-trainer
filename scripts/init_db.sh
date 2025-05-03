#!/bin/bash
set -e

# Check if psql is available
if ! command -v psql >/dev/null 2>&1; then
    echo "Error: PostgreSQL command-line tools (psql) not found!"
    echo "Please install PostgreSQL or add it to your PATH."
    echo ""
    echo "For macOS with Homebrew:"
    echo "  brew install postgresql@16"
    echo "  brew services start postgresql@16"
    echo ""
    echo "To add PostgreSQL to your PATH temporarily, run:"
    echo "  source scripts/setup_env.sh"
    echo ""
    echo "To add permanently, add one of these lines to your ~/.zshrc or ~/.bash_profile:"
    echo "  export PATH=\"/usr/local/opt/postgresql@16/bin:\$PATH\"  # Intel Mac"
    echo "  export PATH=\"/opt/homebrew/opt/postgresql@16/bin:\$PATH\"  # Apple Silicon Mac"
    exit 1
fi

# Get current user - on macOS, Homebrew PostgreSQL typically uses your login user
DEFAULT_ADMIN_USER=$(whoami)
PGUSER=${PGUSER:-$DEFAULT_ADMIN_USER}
PGPASSWORD=${PGPASSWORD:-""}

echo "Using database user: $PGUSER"

# Check if database exists
DB_EXISTS=$(psql -U $PGUSER -tAc "SELECT 1 FROM pg_database WHERE datname='rv'" postgres || echo "0")

if [ "$DB_EXISTS" != "1" ]; then
    echo "Creating database and role..."
    psql -U $PGUSER -c "CREATE DATABASE rv" postgres
    echo "Database created."
else
    echo "Database already exists, skipping creation."
fi

# Create tables directly using SQL script
echo "Creating database tables..."
psql -U $PGUSER -d rv -f "$(dirname "$0")/create_tables.sql"
echo "Database tables created."

echo "Database setup complete." 