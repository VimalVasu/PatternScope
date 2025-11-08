-- Create anomalies table
CREATE TABLE IF NOT EXISTS anomalies (
    id SERIAL PRIMARY KEY,
    detected_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    traffic_event_id INTEGER REFERENCES traffic_events(id),
    anomaly_type VARCHAR(100) NOT NULL,
    confidence_score FLOAT NOT NULL,
    affected_metrics JSONB,
    description TEXT,
    is_resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_anomalies_detected_at ON anomalies(detected_at);
CREATE INDEX IF NOT EXISTS idx_anomalies_traffic_event_id ON anomalies(traffic_event_id);
CREATE INDEX IF NOT EXISTS idx_anomalies_type ON anomalies(anomaly_type);
