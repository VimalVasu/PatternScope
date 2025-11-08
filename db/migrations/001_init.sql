-- Create traffic_events table
CREATE TABLE IF NOT EXISTS traffic_events (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    location_id INTEGER NOT NULL,
    vehicle_count INTEGER NOT NULL,
    avg_speed FLOAT,
    min_speed FLOAT,
    max_speed FLOAT,
    color_counts JSONB,
    inter_arrival_stats JSONB,
    traffic_density_score FLOAT,
    raw_features JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_traffic_events_timestamp ON traffic_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_traffic_events_location_id ON traffic_events(location_id);
CREATE INDEX IF NOT EXISTS idx_traffic_events_timestamp_location ON traffic_events(timestamp, location_id);
