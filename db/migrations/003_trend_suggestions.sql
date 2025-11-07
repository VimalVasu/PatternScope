-- Create trend_suggestions table
CREATE TABLE IF NOT EXISTS trend_suggestions (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    time_period_start TIMESTAMPTZ NOT NULL,
    time_period_end TIMESTAMPTZ NOT NULL,
    suggestion_type VARCHAR(100),
    confidence_level FLOAT,
    description TEXT NOT NULL,
    related_anomalies INTEGER[],
    action_taken BOOLEAN DEFAULT FALSE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_trend_suggestions_created_at ON trend_suggestions(created_at);
CREATE INDEX IF NOT EXISTS idx_trend_suggestions_time_period ON trend_suggestions(time_period_start, time_period_end);
CREATE INDEX IF NOT EXISTS idx_trend_suggestions_type ON trend_suggestions(suggestion_type);
