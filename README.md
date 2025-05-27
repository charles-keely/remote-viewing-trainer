# rv-cli - Remote Viewing CLI Trainer

A command line tool that is a voice activated 'remote viewing' trainer and tester.

## About Remote Viewing

Remote viewing is a protocol for perceiving and describing distant or unseen targets using mental perception. This tool helps train controlled remote viewing (CRV) skills by providing:

- Random target generation (A random image will be downloaded to /app/data/targets, and a target number will be assigned to this image)
- Session-based remote viewing exercises that guide you through a Controlled Remote Viewing session in 6 steps through voice prompts. Your answers will be recorded and stored as you say them.
- AI-powered scoring of remote viewing accuracy

## Requirements

- Python 3.12+
- PostgreSQL 16+
- OpenAI API key

## Dependencies

This project uses Poetry for dependency management. Key dependencies include:

- **FastAPI**: Web framework for the API server
- **SQLAlchemy**: SQL toolkit and ORM
- **Alembic**: Database migration tool
- **OpenAI**: Client for OpenAI API (GPT-4 Vision)
- **Pillow**: Python Imaging Library for image processing
- **Typer/Rich**: CLI interface and formatting
- **httpx**: Asynchronous HTTP client
- **numpy**: Numerical computing for embedding comparisons

Development dependencies:
- **black/ruff/isort**: Code formatting and linting
- **pytest**: Testing framework

For a complete list with versions, see the `pyproject.toml` file.

For users who prefer pip over Poetry, a `requirements.txt` file is also provided:
```bash
pip install -r requirements.txt
```

## Quick Setup

For a streamlined setup experience, run our automated setup script:

```bash
./scripts/setup.sh
```

This script will:
1. Check your Python version
2. Install Poetry if needed
3. Install all project dependencies
4. Configure PostgreSQL paths
5. Create an environment file
6. Initialize the database (if PostgreSQL is available)

## Manual Setup

If you prefer to set things up manually:

1. Install Poetry:
   ```
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Install dependencies:
   ```
   poetry install
   ```

3. Install PostgreSQL (required for database storage):
   ```
   # macOS with Homebrew
   brew install postgresql@16
   brew services start postgresql@16
   ```

4. Add PostgreSQL to your PATH:
   ```
   # For Intel Macs
   echo 'export PATH="/usr/local/opt/postgresql@16/bin:$PATH"' >> ~/.zshrc
   
   # OR for Apple Silicon Mac
   echo 'export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"' >> ~/.zshrc
   
   # Apply the changes
   source ~/.zshrc
   ```

5. Create environment file with your OpenAI API key:
   ```
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```

6. Initialize the database:
   ```
   make db-init
   ```

## Usage

### Start the API server

```
make dev
```

The API will run at http://127.0.0.1:8000

### Run a Voice-Activated Remote Viewing Session (Recommended)

To start a new voice-activated remote viewing session:

```
make vrun
```

This will guide you through a complete remote viewing session using voice prompts and speech recognition:

1. **Target Generation**: A random target image is automatically downloaded and assigned a Target Reference Number (TRN)
2. **Session Creation**: A new session is created and linked to your target
3. **Voice-Guided Note Collection**: The system will speak prompts and record your verbal responses through the 6 stages of Controlled Remote Viewing
4. **Automatic Scoring**: Your spoken notes are automatically transcribed and scored against the target image using AI
5. **Results Display**: View your accuracy scores across different categories

### Alternative: Text-Based Remote Viewing Session

If you prefer to type your notes instead of speaking them:

```
./rv new
```

This will guide you through a complete remote viewing session via text input:

1. **Target Generation**: A random target image is automatically downloaded and assigned a Target Reference Number (TRN)
2. **Session Creation**: A new session is created and linked to your target
3. **Note Collection**: You'll be prompted to enter your impressions/notes:
   - Type your impressions when prompted with "note (blank = finish)"
   - Press Enter after each note to save it
   - Leave blank and press Enter when you're done to finish the session
4. **Automatic Scoring**: Your notes are automatically scored against the target image using AI
5. **Results Display**: View your accuracy scores across different categories

**Example session flow:**
```
$ ./rv new
Session 123 – TRN 81751953
note (blank = finish): blue water
note (blank = finish): mountainous landscape  
note (blank = finish): peaceful feeling
note (blank = finish): [press Enter to finish]
Finishing session and scoring... (this may take a moment)

Session 123
Score: 78.5%

Rubric:
- concept: 85.2%
- color: 92.1%
- shape: 65.8%
- sensory: 71.0%

Notes:
blue water
mountainous landscape
peaceful feeling
```

### View a previous session

```
./rv show <session_id>
```

## Development

- Format code:
   ```
   make fmt
   ```

- Run tests:
   ```
   make test
   ```

- Create database migrations:
   ```
   make migrations m="description of changes"
   ```

## Scoring

Scoring uses OpenAI's GPT-4 Vision and text embeddings to evaluate similarity between your impressions and the actual target.

The scoring matrix includes:
- Concept match (symbolic accuracy)
- Color accuracy
- Shape accuracy
- Sensory impressions
- Overall similarity score

### Enhanced Scoring Mechanism

The Remote Viewing app now includes an enhanced scoring mechanism that provides better differentiation between the various aspects of an image:

1. **Category-specific evaluation**: Each category (color, shape, concept, sensory) is evaluated independently using specialized embeddings that focus on that particular aspect of the image.

2. **Threshold-based scoring**: A minimum similarity threshold is applied to ensure that casual matches don't receive undeserved points, making the scoring more discriminating.

3. **Improved differentiation**: The scoring system now better distinguishes between notes that accurately describe different aspects of the image, providing more meaningful feedback on your remote viewing accuracy.

4. **Comprehensive testing**: The scoring system has been thoroughly tested with a variety of scenarios to ensure it properly rewards accurate descriptions and penalizes inaccurate ones.

## Troubleshooting

### PostgreSQL Not Found

If you see "psql: command not found" when running `make db-init`:

1. Make sure PostgreSQL is installed:
   ```
   brew install postgresql@16
   ```
2. Start the PostgreSQL service:
   ```
   brew services start postgresql@16
   ```
3. Add PostgreSQL to your PATH (based on your Mac architecture):
   ```
   # For Intel Macs
   export PATH="/usr/local/opt/postgresql@16/bin:$PATH"
   
   # For Apple Silicon Macs
   export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"
   ```
4. For convenience, run our helper script:
   ```
   source scripts/setup_env.sh
   ```
   
### Poetry Issues

If you encounter issues with Poetry:

1. Ensure Poetry is installed correctly:
   ```
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Make sure Poetry is in your PATH:
   ```
   export PATH="$HOME/.poetry/bin:$PATH"
   ```

3. Try reinstalling the project dependencies:
   ```
   poetry install
   ```