-- Create targets table
CREATE TABLE IF NOT EXISTS targets (
    target_id VARCHAR PRIMARY KEY,
    image_url VARCHAR NOT NULL,
    caption JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL
);

-- Create sessions table
CREATE TABLE IF NOT EXISTS sessions (
    session_id SERIAL PRIMARY KEY,
    target_id VARCHAR NOT NULL REFERENCES targets(target_id),
    user_notes TEXT NOT NULL,
    sketch_path VARCHAR,
    stage_durations JSONB NOT NULL,
    rubric JSONB NOT NULL,
    total_score FLOAT NOT NULL,
    aols JSONB NOT NULL,
    ts TIMESTAMP DEFAULT NOW() NOT NULL
);

-- Create indices for better performance
CREATE INDEX IF NOT EXISTS idx_sessions_target_id ON sessions(target_id);
CREATE INDEX IF NOT EXISTS idx_targets_created_at ON targets(created_at); 