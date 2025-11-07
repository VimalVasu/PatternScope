# PatternScope

A comprehensive traffic monitoring and anomaly detection system with AI-powered insights.

## Features

- **Real-time Traffic Monitoring**: Ingest and analyze traffic data from multiple sources
- **Anomaly Detection**: Multi-algorithm approach using Z-score, IQR, Isolation Forest, and LOF
- **AI-Powered Insights**: LLM-generated trend suggestions and recommendations
- **Interactive Dashboard**: Real-time visualization of traffic metrics and anomalies
- **Microservices Architecture**: Scalable, containerized services

## Architecture

- **Backend**: TypeScript + Fastify REST API
- **Analysis Service**: Python + FastAPI for anomaly detection
- **Dashboard**: React + Vite for data visualization
- **Database**: PostgreSQL for data persistence
- **LLM**: Ollama for trend summarization
- **Edge Mock**: Simulated traffic data publisher

## Quick Start

### Prerequisites

- Docker and Docker Compose
- At least 4GB of available RAM
- Ports 3000, 5432, 8000, 8080, 11434 available

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd PatternScope
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Start all services:
```bash
docker-compose up -d
```

4. Wait for services to be healthy:
```bash
docker-compose ps
```

5. Pull Ollama model (optional, for LLM features):
```bash
docker exec -it patternscope-ollama ollama pull llama2
```

### Access the Application

- **Dashboard**: http://localhost:8080
- **Backend API**: http://localhost:3000
- **Analysis Service**: http://localhost:8000
- **API Documentation**:
  - Backend: http://localhost:3000/health
  - Analysis: http://localhost:8000/docs

## API Endpoints

### Backend Service (Port 3000)

- `GET /health` - Health check
- `POST /ingest/traffic` - Ingest traffic events
- `GET /metrics/traffic?start=&end=` - Get traffic metrics
- `GET /dashboard/summary?start=&end=` - Dashboard summary
- `GET /dashboard/timeseries?start=&end=` - Timeseries data
- `GET /trends/suggestions?start=&end=` - Trend suggestions

### Analysis Service (Port 8000)

- `GET /health` - Health check
- `POST /run-analysis` - Run anomaly detection

## Development

### Backend

```bash
cd backend
npm install
npm run dev
```

### Analysis Service

```bash
cd analysis
pip install -r requirements.txt
python main.py
```

### Dashboard

```bash
cd dashboard
npm install
npm run dev
```

### Edge Mock

```bash
cd edge-mock
pip install -r requirements.txt
python publisher.py
```

## Database Schema

### traffic_events
- `id`: Serial primary key
- `timestamp`: Timestamp with timezone
- `location_id`: Integer
- `vehicle_count`: Integer
- `avg_speed`, `min_speed`, `max_speed`: Float
- `color_counts`: JSONB
- `inter_arrival_stats`: JSONB
- `traffic_density_score`: Float
- `raw_features`: JSONB

### anomalies
- `id`: Serial primary key
- `detected_at`: Timestamp
- `traffic_event_id`: Foreign key to traffic_events
- `anomaly_type`: String (zscore, iqr, isolation_forest, lof)
- `confidence_score`: Float
- `affected_metrics`: JSONB
- `description`: Text

### trend_suggestions
- `id`: Serial primary key
- `created_at`: Timestamp
- `time_period_start`, `time_period_end`: Timestamp
- `suggestion_type`: String
- `confidence_level`: Float
- `description`: Text
- `related_anomalies`: Integer array

## Testing

The edge-mock service automatically generates realistic traffic data with:
- Time-of-day variations (rush hour patterns)
- Random anomalies (5% injection rate)
- Realistic speed and vehicle count distributions
- Color distribution based on real-world statistics

## Monitoring

View logs for each service:
```bash
docker-compose logs -f <service-name>
```

Available services: `db`, `backend`, `analysis`, `edge-mock`, `dashboard`, `ollama`

## Troubleshooting

### Services won't start
```bash
docker-compose down
docker-compose up -d
```

### Database connection issues
```bash
docker-compose restart db
```

### Ollama model not found
```bash
docker exec -it patternscope-ollama ollama pull llama2
```

### Clear all data and restart
```bash
docker-compose down -v
docker-compose up -d
```

## License

MIT License

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
