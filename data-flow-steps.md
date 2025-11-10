# Data Flow: Red Car Detection → Dashboard

## 1. Edge Device/Camera Observation
The edge device (or simulator) observes the red car passing through the monitored location and captures it as part of the color distribution data for that observation interval.

**Code Location:**
- `edge-mock/publisher.py:18-19` - Color list and probabilities definition
- `edge-mock/publisher.py:48-58` - Color count generation logic

---

## 2. Event Generation
The edge device generates a structured traffic event containing timestamp, location ID, vehicle count, speed statistics (min/avg/max), and a color distribution JSON object that includes the red car detection along with other colors observed.

**Code Location:**
- `edge-mock/publisher.py:21-100` - `TrafficDataGenerator.generate_event()` method
- `edge-mock/publisher.py:69-84` - Anomaly injection logic (5% chance)

---

## 3. REST API Ingestion
The event is published via HTTP POST to the Fastify-based TypeScript backend service at its REST API endpoint.

**Code Location:**
- `edge-mock/publisher.py:103-150` - `TrafficPublisher` class handles HTTP POST
- `backend/src/routes/traffic.ts:37-82` - POST `/ingest/traffic` endpoint

---

## 4. Schema Validation
The backend validates the incoming event against a JSON schema, ensuring required fields (timestamp, location, vehicle_count) are present and the data structure is correct.

**Code Location:**
- `backend/src/routes/traffic.ts:4-15` - `TrafficEvent` interface definition
- `backend/src/routes/traffic.ts:17-34` - `trafficEventSchema` validation rules

---

## 5. Database Persistence
The validated event is inserted into the PostgreSQL `traffic_events` table, with the color distribution stored in a JSONB column for flexible querying. Indexes on timestamp and location fields are automatically updated.

**Code Location:**
- `backend/src/routes/traffic.ts:44-66` - INSERT query execution
- `db/migrations/001_init.sql:2-20` - `traffic_events` table schema with indexes

---

## 6. Analysis Service Polling
The Python analysis service fetches recent events from the database within a specified time window, pulling the red car data along with other traffic observations.

**Code Location:**
- `analysis/services/db.py:21-53` - `fetch_traffic_events()` method
- `analysis/services/db.py:25-47` - SQL SELECT query with date range filtering

---

## 7. Data Frame Conversion
Events are converted into a pandas DataFrame for efficient numerical processing, with color distribution data extracted and potentially used as features.

**Code Location:**
- `analysis/services/db.py:49` - `pd.read_sql_query()` DataFrame conversion

---

## 8. Ensemble Anomaly Detection
Four parallel detection algorithms run analyzing whether the red car observation—combined with other metrics like vehicle count, speed, and color patterns—represents an anomaly.

**Code Location:**
- `analysis/services/analysis.py:69-98` - `_detect_zscore()` - Z-score detection (threshold: 3.0 σ)
- `analysis/services/analysis.py:100-131` - `_detect_iqr()` - Interquartile Range detection
- `analysis/services/analysis.py:133-167` - `_detect_isolation_forest()` - Isolation Forest (contamination=0.1)
- `analysis/services/analysis.py:169-203` - `_detect_lof()` - Local Outlier Factor (n_neighbors=20)

---

## 9. Anomaly Deduplication & Storage
If multiple algorithms flag the same event, the system keeps the highest confidence score and stores the anomaly record in the `anomalies` table with a foreign key reference to the original event.

**Code Location:**
- `analysis/services/analysis.py:205-215` - `_deduplicate_anomalies()` method
- `analysis/services/db.py:55-84` - `insert_anomalies()` method
- `db/migrations/002_anomalies.sql:2-17` - `anomalies` table schema

---

## 10. LLM Insight Generation
If anomalies are detected, the system builds a contextual prompt and sends it to the locally-hosted Ollama LLM, which generates human-readable insights and recommendations about the unusual traffic pattern.

**Code Location:**
- `analysis/services/llm_client.py:19-62` - `OllamaClient.generate_trend_suggestions()` method
- `analysis/services/llm_client.py:64-105` - `_build_prompt()` - Prompt construction
- `analysis/services/llm_client.py:107-127` - `_call_ollama()` - API call to `http://ollama:11434/api/generate`

---

## 11. Trend Suggestion Storage
The LLM-generated text is stored in the `trend_suggestions` table, linked to the anomaly record that triggered it.

**Code Location:**
- `analysis/services/db.py:86-114` - `insert_trend_suggestion()` method
- `analysis/services/llm_client.py:38-48` - Stores LLM response
- `db/migrations/003_trend_suggestions.sql:2-17` - `trend_suggestions` table schema

---

## 12. Dashboard API Requests
The React dashboard makes parallel API calls to backend endpoints requesting summary statistics, time-series data, detected anomalies, and AI-generated suggestions for the selected time range.

**Code Location:**
- `dashboard/src/App.jsx:26-34` - `fetchData()` function with `Promise.all()` for parallel requests
- `dashboard/src/services/api.js:10-17` - `getDashboardSummary()` - GET `/dashboard/summary`
- `dashboard/src/services/api.js:19-25` - `getDashboardTimeseries()` - GET `/dashboard/timeseries`
- `dashboard/src/services/api.js:28-35` - `getTrendSuggestions()` - GET `/trends/suggestions`

---

## 13. Data Aggregation & Response
The backend queries PostgreSQL, performs aggregations (hourly buckets, averages, counts), and returns JSON responses containing the red car's contribution to the overall traffic metrics.

**Code Location:**
- `backend/src/routes/dashboard.ts:6-68` - GET `/dashboard/summary` endpoint with COUNT, SUM, AVG aggregations
- `backend/src/routes/dashboard.ts:70-116` - GET `/dashboard/timeseries` endpoint with `DATE_TRUNC('hour')` grouping
- `backend/src/routes/trends.ts:6-56` - GET `/trends/suggestions` endpoint

---

## 14. Dashboard Rendering
The React frontend receives the data and updates KPI cards, time-series charts, anomaly highlights, and AI suggestions in plain language.

**Code Location:**
- `dashboard/src/components/KPICards.jsx:1-40` - Displays event_count, total_vehicles, average_speed, anomaly_count
- `dashboard/src/components/TimeSeriesChart.jsx:1-76` - Recharts line chart with dual Y-axes (vehicle count & speed)
- `dashboard/src/components/TrendSuggestions.jsx:1-52` - Displays AI-generated suggestions with confidence levels

---

## 15. User Visualization
The operator sees the red car's data point integrated into the broader traffic patterns on their screen, with color distribution potentially visible in detailed event views or contributing to anomaly detection patterns.

**Code Location:**
- `dashboard/src/components/DateRangeSelector.jsx:1-48` - Time range selection controls
- `dashboard/src/App.jsx` - Main component orchestrating all visualizations
