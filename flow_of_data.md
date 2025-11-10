# Flow of Data: Tracking One Normal Event Through PatternScope

This document tracks a single normal traffic event containing a red car detection through every stage of the PatternScope system, showing the exact data format at each transformation point.

---

## Step 1: Edge Device - Event Generation
**Location:** `edge-mock/publisher.py:86-100` (`generate_event()`)

**Output Format:** Python Dictionary

```python
{
    'timestamp': '2025-01-09T14:23:45.123456',
    'location_id': 3,
    'vehicle_count': 42,
    'avg_speed': 38.47,
    'min_speed': 28.92,
    'max_speed': 52.13,
    'color_counts': {
        'white': 10,
        'black': 9,
        'silver': 7,
        'gray': 6,
        'red': 4,
        'blue': 3,
        'brown': 2,
        'green': 1
    },
    'inter_arrival_stats': {
        'mean': 85.71,
        'std': 34.28,
        'min': 17.14,
        'max': 214.29
    },
    'traffic_density_score': 0.562,
    'raw_features': {
        'weather': 'clear',
        'visibility': 'good'
    }
}
```

**Notes:**
- Normal event (2pm, midday traffic)
- 4 red cars detected out of 42 total vehicles
- Average speed 38.47 km/h (normal range)
- Density score 0.562 (moderate traffic)

---

## Step 2: HTTP POST Request to Backend
**Location:** `edge-mock/publisher.py:113-138` (`publish_event()`)

**Request Format:**
```http
POST http://backend:3000/ingest/traffic HTTP/1.1
Host: backend:3000
Content-Type: application/json
Content-Length: 456

{
    "timestamp": "2025-01-09T14:23:45.123456",
    "location_id": 3,
    "vehicle_count": 42,
    "avg_speed": 38.47,
    "min_speed": 28.92,
    "max_speed": 52.13,
    "color_counts": {
        "white": 10,
        "black": 9,
        "silver": 7,
        "gray": 6,
        "red": 4,
        "blue": 3,
        "brown": 2,
        "green": 1
    },
    "inter_arrival_stats": {
        "mean": 85.71,
        "std": 34.28,
        "min": 17.14,
        "max": 214.29
    },
    "traffic_density_score": 0.562,
    "raw_features": {
        "weather": "clear",
        "visibility": "good"
    }
}
```

**Console Output:**
```
✓ Published event: location=3, vehicles=42, speed=38.5
```

---

## Step 3: Backend Receives & Validates
**Location:** `backend/src/routes/traffic.ts:17-34` (Schema Validation)

**TypeScript Interface:**
```typescript
interface TrafficEvent {
  timestamp: string;           // Required
  location_id: number;         // Required
  vehicle_count: number;       // Required
  avg_speed?: number;          // Optional
  min_speed?: number;          // Optional
  max_speed?: number;          // Optional
  color_counts?: object;       // Optional
  inter_arrival_stats?: object; // Optional
  traffic_density_score?: number; // Optional
  raw_features?: object;       // Optional
}
```

**Validation Result:**
```typescript
{
  isValid: true,
  validatedData: {
    timestamp: '2025-01-09T14:23:45.123456',
    location_id: 3,
    vehicle_count: 42,
    avg_speed: 38.47,
    min_speed: 28.92,
    max_speed: 52.13,
    color_counts: { white: 10, black: 9, silver: 7, gray: 6, red: 4, blue: 3, brown: 2, green: 1 },
    inter_arrival_stats: { mean: 85.71, std: 34.28, min: 17.14, max: 214.29 },
    traffic_density_score: 0.562,
    raw_features: { weather: 'clear', visibility: 'good' }
  }
}
```

**Validation Status:** ✓ PASSED (All required fields present, types correct)

---

## Step 4: Database Persistence
**Location:** `backend/src/routes/traffic.ts:44-66` (INSERT Query)

**SQL Query Executed:**
```sql
INSERT INTO traffic_events (
    timestamp,
    location_id,
    vehicle_count,
    avg_speed,
    min_speed,
    max_speed,
    color_counts,
    inter_arrival_stats,
    traffic_density_score,
    raw_features
) VALUES (
    '2025-01-09T14:23:45.123456',
    3,
    42,
    38.47,
    28.92,
    52.13,
    '{"white": 10, "black": 9, "silver": 7, "gray": 6, "red": 4, "blue": 3, "brown": 2, "green": 1}'::jsonb,
    '{"mean": 85.71, "std": 34.28, "min": 17.14, "max": 214.29}'::jsonb,
    0.562,
    '{"weather": "clear", "visibility": "good"}'::jsonb
)
RETURNING id;
```

**Query Result:**
```
id: 1523
```

**HTTP Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
    "success": true,
    "id": 1523,
    "message": "Traffic event recorded successfully"
}
```

---

### Database State After Insert

**Table:** `traffic_events`

**Schema Definition** (`db/migrations/001_init.sql:2-20`):
```sql
CREATE TABLE traffic_events (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    location_id INTEGER NOT NULL,
    vehicle_count INTEGER NOT NULL,
    avg_speed NUMERIC(5,2),
    min_speed NUMERIC(5,2),
    max_speed NUMERIC(5,2),
    color_counts JSONB,
    inter_arrival_stats JSONB,
    traffic_density_score NUMERIC(4,3),
    raw_features JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_traffic_timestamp ON traffic_events(timestamp);
CREATE INDEX idx_traffic_location ON traffic_events(location_id);
CREATE INDEX idx_traffic_timestamp_location ON traffic_events(timestamp, location_id);
```

**Current Table Contents** (showing context with multiple rows):

| id | timestamp | location_id | vehicle_count | avg_speed | min_speed | max_speed | color_counts | inter_arrival_stats | traffic_density_score | raw_features | created_at |
|----|-----------|-------------|---------------|-----------|-----------|-----------|--------------|---------------------|----------------------|--------------|------------|
| 1520 | 2025-01-09T14:13:30 | 1 | 35 | 42.30 | 32.15 | 58.45 | `{"white": 8, "black": 7, ...}` | `{"mean": 102.86, ...}` | 0.485 | `{"weather": "cloudy", ...}` | 2025-01-09T14:13:31 |
| 1521 | 2025-01-09T14:13:40 | 2 | 48 | 36.20 | 25.60 | 51.80 | `{"white": 12, "black": 10, ...}` | `{"mean": 75.00, ...}` | 0.620 | `{"weather": "clear", ...}` | 2025-01-09T14:13:41 |
| 1522 | 2025-01-09T14:13:50 | 5 | 28 | 45.10 | 35.20 | 62.30 | `{"white": 7, "black": 6, ...}` | `{"mean": 128.57, ...}` | 0.395 | `{"weather": "rainy", ...}` | 2025-01-09T14:13:51 |
| **1523** | **2025-01-09T14:23:45** | **3** | **42** | **38.47** | **28.92** | **52.13** | **`{"white": 10, "black": 9, "silver": 7, "gray": 6, "red": 4, "blue": 3, "brown": 2, "green": 1}`** | **`{"mean": 85.71, "std": 34.28, "min": 17.14, "max": 214.29}`** | **0.562** | **`{"weather": "clear", "visibility": "good"}`** | **2025-01-09T14:23:46** |
| 1524 | 2025-01-09T14:23:55 | 4 | 52 | 33.80 | 22.40 | 48.90 | `{"white": 13, "black": 11, ...}` | `{"mean": 69.23, ...}` | 0.715 | `{"weather": "clear", ...}` | 2025-01-09T14:23:56 |

**Notes:**
- Our tracked event is row **1523** (highlighted in bold)
- Red car data stored in JSONB `color_counts` field: `"red": 4`
- Indexes automatically updated on `timestamp`, `location_id`, and composite `(timestamp, location_id)`

---

## Step 5: Analysis Service Fetches Events
**Location:** `analysis/services/db.py:21-53` (`fetch_traffic_events()`)

**SQL Query Executed:**
```sql
SELECT
    id,
    timestamp,
    location_id,
    vehicle_count,
    avg_speed,
    min_speed,
    max_speed,
    traffic_density_score
FROM traffic_events
WHERE timestamp >= '2025-01-09T14:00:00'
  AND timestamp <= '2025-01-09T15:00:00'
ORDER BY timestamp ASC;
```

**Query Result** (Raw SQL Result Set):
```
   id  |      timestamp      | location_id | vehicle_count | avg_speed | min_speed | max_speed | traffic_density_score
-------|---------------------|-------------|---------------|-----------|-----------|-----------|----------------------
  1520 | 2025-01-09 14:13:30 |           1 |            35 |     42.30 |     32.15 |     58.45 |                 0.485
  1521 | 2025-01-09 14:13:40 |           2 |            48 |     36.20 |     25.60 |     51.80 |                 0.620
  1522 | 2025-01-09 14:13:50 |           5 |            28 |     45.10 |     35.20 |     62.30 |                 0.395
  1523 | 2025-01-09 14:23:45 |           3 |            42 |     38.47 |     28.92 |     52.13 |                 0.562
  1524 | 2025-01-09 14:23:55 |           4 |            52 |     33.80 |     22.40 |     48.90 |                 0.715
  (5 rows)
```

**Notes:**
- Fetches 1-hour window of data
- Color data NOT fetched (not needed for anomaly detection)
- Our event (id=1523) included in the batch

---

## Step 6: DataFrame Conversion
**Location:** `analysis/services/db.py:49` (`pd.read_sql_query()`)

**Pandas DataFrame Structure:**
```python
import pandas as pd

# DataFrame dtypes
dtypes:
    id                        int64
    timestamp        datetime64[ns]
    location_id              int64
    vehicle_count            int64
    avg_speed              float64
    min_speed              float64
    max_speed              float64
    traffic_density_score  float64
dtype: object

# DataFrame shape
(5, 8)  # 5 rows, 8 columns
```

**DataFrame Contents:**
```
      id           timestamp  location_id  vehicle_count  avg_speed  min_speed  max_speed  traffic_density_score
0   1520 2025-01-09 14:13:30            1             35      42.30      32.15      58.45                  0.485
1   1521 2025-01-09 14:13:40            2             48      36.20      25.60      51.80                  0.620
2   1522 2025-01-09 14:13:50            5             28      45.10      35.20      62.30                  0.395
3   1523 2025-01-09 14:23:45            3             42      38.47      28.92      52.13                  0.562
4   1524 2025-01-09 14:23:55            4             52      33.80      22.40      48.90                  0.715
```

**Accessing Our Event:**
```python
df.loc[3]
# Output:
# id                              1523
# timestamp         2025-01-09 14:23:45
# location_id                        3
# vehicle_count                     42
# avg_speed                      38.47
# min_speed                      28.92
# max_speed                      52.13
# traffic_density_score          0.562
# Name: 3, dtype: object
```

---

## Step 7: Anomaly Detection Algorithms
**Location:** `analysis/services/analysis.py:69-203` (Four detection methods)

### 7a. Z-Score Detection
**Location:** `analysis/services/analysis.py:69-98`

**Algorithm:** Flags values > 3.0 standard deviations from mean

**Calculations for our event (id=1523):**
```python
# Vehicle Count Analysis
mean_vehicle_count = 41.0
std_vehicle_count = 9.32
z_score_vehicle_count = (42 - 41.0) / 9.32 = 0.107

# Avg Speed Analysis
mean_avg_speed = 39.17
std_avg_speed = 4.41
z_score_avg_speed = (38.47 - 39.17) / 4.41 = -0.159

# Traffic Density Analysis
mean_density = 0.5554
std_density = 0.1217
z_score_density = (0.562 - 0.5554) / 0.1217 = 0.054

# Threshold: |z_score| > 3.0
```

**Result:**
```python
{
    'is_anomaly': False,
    'max_z_score': 0.159,
    'threshold': 3.0
}
```
✗ No anomaly detected (all z-scores well below threshold)

---

### 7b. IQR Detection
**Location:** `analysis/services/analysis.py:100-131`

**Algorithm:** Flags values outside Q1 - 1.5×IQR to Q3 + 1.5×IQR range

**Calculations for our event (id=1523):**
```python
# Vehicle Count Analysis
Q1_vehicle = 35.0
Q3_vehicle = 52.0
IQR_vehicle = 17.0
lower_bound = 35.0 - 1.5 * 17.0 = 9.5
upper_bound = 52.0 + 1.5 * 17.0 = 77.5
value = 42  # Within bounds [9.5, 77.5]

# Avg Speed Analysis
Q1_speed = 36.2
Q3_speed = 42.3
IQR_speed = 6.1
lower_bound = 36.2 - 1.5 * 6.1 = 27.05
upper_bound = 42.3 + 1.5 * 6.1 = 51.45
value = 38.47  # Within bounds [27.05, 51.45]

# Traffic Density Analysis
Q1_density = 0.485
Q3_density = 0.620
IQR_density = 0.135
lower_bound = 0.485 - 1.5 * 0.135 = 0.2825
upper_bound = 0.620 + 1.5 * 0.135 = 0.8225
value = 0.562  # Within bounds [0.2825, 0.8225]
```

**Result:**
```python
{
    'is_anomaly': False,
    'bounds_exceeded': [],
    'method': 'IQR'
}
```
✗ No anomaly detected (all values within IQR bounds)

---

### 7c. Isolation Forest Detection
**Location:** `analysis/services/analysis.py:133-167`

**Algorithm:** Uses decision trees to isolate outliers (contamination=0.1, min_samples=10)

**Feature Matrix:**
```python
X = [[vehicle_count, avg_speed, traffic_density_score], ...]
X[3] = [42, 38.47, 0.562]  # Our event
```

**Model Training:**
```python
from sklearn.ensemble import IsolationForest

model = IsolationForest(contamination=0.1, random_state=42)
model.fit(X)
predictions = model.predict(X)
scores = model.score_samples(X)
```

**Prediction for our event:**
```python
predictions[3] = 1  # 1 = inlier, -1 = outlier
scores[3] = -0.185  # Anomaly score (higher = more normal)
```

**Result:**
```python
{
    'is_anomaly': False,
    'anomaly_score': -0.185,
    'prediction': 1,  # Inlier
    'method': 'IsolationForest'
}
```
✗ No anomaly detected (classified as inlier)

---

### 7d. Local Outlier Factor (LOF) Detection
**Location:** `analysis/services/analysis.py:169-203`

**Algorithm:** Compares local density to neighbors (n_neighbors=20, contamination=0.1)

**Feature Matrix:**
```python
X = [[vehicle_count, avg_speed, traffic_density_score], ...]
X[3] = [42, 38.47, 0.562]  # Our event
```

**Model Training:**
```python
from sklearn.neighbors import LocalOutlierFactor

model = LocalOutlierFactor(n_neighbors=20, contamination=0.1)
predictions = model.fit_predict(X)
scores = model.negative_outlier_factor_
```

**Prediction for our event:**
```python
predictions[3] = 1  # 1 = inlier, -1 = outlier
scores[3] = -1.023  # Negative outlier factor (closer to -1 = more normal)
```

**Result:**
```python
{
    'is_anomaly': False,
    'lof_score': -1.023,
    'prediction': 1,  # Inlier
    'method': 'LOF'
}
```
✗ No anomaly detected (local density similar to neighbors)

---

### Ensemble Result Summary
**Location:** `analysis/services/analysis.py:205-215` (Deduplication)

**Combined Results:**
```python
anomalies_detected = []  # Empty list - no algorithms flagged event 1523
```

**Deduplication Output:**
```python
deduplicated_anomalies = []  # Nothing to deduplicate
```

**Final Status:** ✓ Event 1523 passed all anomaly detection tests (NORMAL EVENT)

---

## Step 8: Anomaly Storage
**Location:** `analysis/services/db.py:55-84` (`insert_anomalies()`)

**Action:** SKIPPED - No anomalies detected for event 1523

**Database State:** `anomalies` table NOT updated for this event

---

### Database State After Analysis

**Table:** `anomalies`

**Schema Definition** (`db/migrations/002_anomalies.sql:2-17`):
```sql
CREATE TABLE anomalies (
    id SERIAL PRIMARY KEY,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    traffic_event_id INTEGER NOT NULL,
    anomaly_type VARCHAR(50) NOT NULL,
    confidence_score NUMERIC(4,3) NOT NULL,
    affected_metrics JSONB,
    description TEXT,
    is_resolved BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (traffic_event_id) REFERENCES traffic_events(id) ON DELETE CASCADE
);

CREATE INDEX idx_anomalies_event ON anomalies(traffic_event_id);
CREATE INDEX idx_anomalies_type ON anomalies(anomaly_type);
```

**Current Table Contents** (showing other events' anomalies for context):

| id | detected_at | traffic_event_id | anomaly_type | confidence_score | affected_metrics | description | is_resolved | created_at |
|----|-------------|------------------|--------------|------------------|------------------|-------------|-------------|------------|
| 45 | 2025-01-09T14:05:20 | 1515 | high_speed | 0.924 | `["avg_speed", "max_speed"]` | Unusual speed pattern detected: avg_speed=72.3 (z-score=4.2) | false | 2025-01-09T14:10:15 |
| 46 | 2025-01-09T14:15:42 | 1518 | high_density | 0.887 | `["vehicle_count", "traffic_density_score"]` | Extreme vehicle count: 125 vehicles detected (IQR outlier) | false | 2025-01-09T14:20:30 |
| 47 | 2025-01-09T14:18:12 | 1519 | low_speed | 0.856 | `["avg_speed", "min_speed"]` | Significantly low speeds detected: avg_speed=12.4 (LOF=-2.8) | false | 2025-01-09T14:20:30 |

**Notes:**
- Event 1523 is NOT in the anomalies table (normal event)
- Foreign key `traffic_event_id` references `traffic_events(id)`
- Other events (1515, 1518, 1519) have detected anomalies shown for context

---

## Step 9: LLM Insight Generation
**Location:** `analysis/services/llm_client.py:19-62`

**Action:** SKIPPED - No anomalies detected in this batch, OR LLM runs on batch with other anomalies but not triggered by event 1523

**Database State:** `trend_suggestions` table NOT updated based on event 1523

---

### Database State After LLM Processing

**Table:** `trend_suggestions`

**Schema Definition** (`db/migrations/003_trend_suggestions.sql:2-17`):
```sql
CREATE TABLE trend_suggestions (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    time_period_start TIMESTAMP NOT NULL,
    time_period_end TIMESTAMP NOT NULL,
    suggestion_type VARCHAR(50),
    confidence_level VARCHAR(20),
    description TEXT NOT NULL,
    related_anomalies JSONB,
    action_taken BOOLEAN DEFAULT false
);

CREATE INDEX idx_trend_period ON trend_suggestions(time_period_start, time_period_end);
```

**Current Table Contents** (showing suggestions from other time periods):

| id | created_at | time_period_start | time_period_end | suggestion_type | confidence_level | description | related_anomalies | action_taken |
|----|------------|-------------------|-----------------|-----------------|------------------|-------------|-------------------|--------------|
| 12 | 2025-01-09T14:10:20 | 2025-01-09T13:00:00 | 2025-01-09T14:00:00 | traffic_safety | high | Unusual high-speed patterns detected during typical hours. Recommend reviewing speed limit signage and considering enforcement. Multiple vehicles exceeded safe speeds, particularly on location 1. | `[45]` | false |
| 13 | 2025-01-09T14:20:35 | 2025-01-09T14:00:00 | 2025-01-09T15:00:00 | congestion_alert | medium | High vehicle density detected at location 2. Consider adjusting signal timing or investigating potential traffic diversion from nearby routes. Low-speed patterns suggest possible congestion. | `[46, 47]` | false |

**Notes:**
- Suggestions reference anomaly IDs in `related_anomalies` JSONB field
- Event 1523 is NOT referenced (no anomalies to trigger suggestions)

---

## Step 10: Dashboard API Requests
**Location:** `dashboard/src/App.jsx:26-34` (`fetchData()`)

**React Component initiates parallel API calls:**

### Request 1: Dashboard Summary
```http
GET http://backend:3000/dashboard/summary?start=2025-01-09T14:00:00&end=2025-01-09T15:00:00 HTTP/1.1
Host: backend:3000
Accept: application/json
```

### Request 2: Dashboard Timeseries
```http
GET http://backend:3000/dashboard/timeseries?start=2025-01-09T14:00:00&end=2025-01-09T15:00:00 HTTP/1.1
Host: backend:3000
Accept: application/json
```

### Request 3: Trend Suggestions
```http
GET http://backend:3000/trends/suggestions?start=2025-01-09T14:00:00&end=2025-01-09T15:00:00 HTTP/1.1
Host: backend:3000
Accept: application/json
```

**JavaScript Code:**
```javascript
const fetchData = async () => {
    setLoading(true);
    try {
        const [summaryData, timeseriesData, trendsData] = await Promise.all([
            getDashboardSummary(dateRange.start, dateRange.end),
            getDashboardTimeseries(dateRange.start, dateRange.end),
            getTrendSuggestions(dateRange.start, dateRange.end)
        ]);
        // ... update state
    } catch (error) {
        console.error('Error fetching dashboard data:', error);
    } finally {
        setLoading(false);
    }
};
```

---

## Step 11: Backend Data Aggregation
**Location:** `backend/src/routes/dashboard.ts`

### 11a. Dashboard Summary Endpoint
**Location:** `backend/src/routes/dashboard.ts:6-68`

**SQL Query 1 - Traffic Summary:**
```sql
SELECT
    COUNT(*) as event_count,
    SUM(vehicle_count) as total_vehicles,
    AVG(avg_speed) as average_speed,
    MIN(timestamp) as period_start,
    MAX(timestamp) as period_end
FROM traffic_events
WHERE timestamp >= '2025-01-09T14:00:00'
  AND timestamp <= '2025-01-09T15:00:00';
```

**Query Result:**
```
 event_count | total_vehicles | average_speed |    period_start     |     period_end
-------------|----------------|---------------|---------------------|---------------------
           5 |            205 |        39.174 | 2025-01-09 14:13:30 | 2025-01-09 14:23:55
```

**SQL Query 2 - Anomaly Count:**
```sql
SELECT COUNT(*) as anomaly_count
FROM anomalies
WHERE detected_at >= '2025-01-09T14:00:00'
  AND detected_at <= '2025-01-09T15:00:00';
```

**Query Result:**
```
 anomaly_count
---------------
             3
```

**Notes:**
- Event 1523 contributes to: event_count (+1), total_vehicles (+42), average_speed calculation
- Event 1523 does NOT contribute to anomaly_count (0 anomalies)

---

### 11b. Dashboard Timeseries Endpoint
**Location:** `backend/src/routes/dashboard.ts:70-116`

**SQL Query:**
```sql
SELECT
    DATE_TRUNC('hour', timestamp) as time_bucket,
    SUM(vehicle_count) as vehicle_count,
    AVG(avg_speed) as avg_speed,
    COUNT(*) as event_count
FROM traffic_events
WHERE timestamp >= '2025-01-09T14:00:00'
  AND timestamp <= '2025-01-09T15:00:00'
GROUP BY time_bucket
ORDER BY time_bucket;
```

**Query Result:**
```
     time_bucket     | vehicle_count | avg_speed | event_count
---------------------|---------------|-----------|-------------
 2025-01-09 14:00:00 |           205 |    39.174 |           5
```

**Notes:**
- All 5 events (including 1523) fall in 14:00:00 hour bucket
- Event 1523 contributes: +42 vehicles, avg_speed calculation, +1 event_count

---

### 11c. Trends Endpoint
**Location:** `backend/src/routes/trends.ts:6-56`

**SQL Query:**
```sql
SELECT
    id,
    created_at,
    time_period_start,
    time_period_end,
    suggestion_type,
    confidence_level,
    description,
    related_anomalies,
    action_taken
FROM trend_suggestions
WHERE time_period_start >= '2025-01-09T14:00:00'
  AND time_period_end <= '2025-01-09T15:00:00'
ORDER BY created_at DESC;
```

**Query Result:**
```
 id |     created_at      | time_period_start  |  time_period_end   | suggestion_type | confidence_level | description | related_anomalies | action_taken
----|---------------------|--------------------|--------------------|-----------------|------------------|-------------|-------------------|-------------
 13 | 2025-01-09 14:20:35 | 2025-01-09 14:00:00| 2025-01-09 15:00:00| congestion_alert| medium           | High vehicle density detected... | [46, 47] | false
```

**Notes:**
- Returns suggestion id=13 triggered by anomalies 46 and 47 (NOT event 1523)

---

## Step 12: API Responses to Dashboard
**Location:** Network responses received by `dashboard/src/services/api.js`

### Response 1: Dashboard Summary
**HTTP Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "success": true,
    "data": {
        "event_count": 5,
        "total_vehicles": 205,
        "average_speed": 39.174,
        "period_start": "2025-01-09T14:13:30.000Z",
        "period_end": "2025-01-09T14:23:55.000Z",
        "anomaly_count": 3
    }
}
```

**JavaScript Variable:**
```javascript
summaryData = {
    event_count: 5,
    total_vehicles: 205,
    average_speed: 39.174,
    period_start: "2025-01-09T14:13:30.000Z",
    period_end: "2025-01-09T14:23:55.000Z",
    anomaly_count: 3
}
```

---

### Response 2: Dashboard Timeseries
**HTTP Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "success": true,
    "data": [
        {
            "time_bucket": "2025-01-09T14:00:00.000Z",
            "vehicle_count": 205,
            "avg_speed": 39.174,
            "event_count": 5
        }
    ]
}
```

**JavaScript Variable:**
```javascript
timeseriesData = [
    {
        time_bucket: "2025-01-09T14:00:00.000Z",
        vehicle_count: 205,
        avg_speed: 39.174,
        event_count: 5
    }
]
```

---

### Response 3: Trend Suggestions
**HTTP Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "success": true,
    "data": [
        {
            "id": 13,
            "created_at": "2025-01-09T14:20:35.000Z",
            "time_period_start": "2025-01-09T14:00:00.000Z",
            "time_period_end": "2025-01-09T15:00:00.000Z",
            "suggestion_type": "congestion_alert",
            "confidence_level": "medium",
            "description": "High vehicle density detected at location 2. Consider adjusting signal timing or investigating potential traffic diversion from nearby routes. Low-speed patterns suggest possible congestion.",
            "related_anomalies": [46, 47],
            "action_taken": false
        }
    ]
}
```

**JavaScript Variable:**
```javascript
trendsData = [
    {
        id: 13,
        created_at: "2025-01-09T14:20:35.000Z",
        time_period_start: "2025-01-09T14:00:00.000Z",
        time_period_end: "2025-01-09T15:00:00.000Z",
        suggestion_type: "congestion_alert",
        confidence_level: "medium",
        description: "High vehicle density detected at location 2. Consider adjusting signal timing or investigating potential traffic diversion from nearby routes. Low-speed patterns suggest possible congestion.",
        related_anomalies: [46, 47],
        action_taken: false
    }
]
```

---

## Step 13: Dashboard Component Rendering
**Location:** `dashboard/src/components/`

### React State After Data Fetch:
```javascript
const [summaryData, setSummaryData] = useState({
    event_count: 5,
    total_vehicles: 205,
    average_speed: 39.174,
    anomaly_count: 3
});

const [timeseriesData, setTimeseriesData] = useState([
    {
        time_bucket: "2025-01-09T14:00:00.000Z",
        vehicle_count: 205,
        avg_speed: 39.174,
        event_count: 5
    }
]);

const [trendsData, setTrendsData] = useState([
    {
        id: 13,
        suggestion_type: "congestion_alert",
        confidence_level: "medium",
        description: "High vehicle density detected at location 2. Consider adjusting signal timing...",
        related_anomalies: [46, 47]
    }
]);
```

---

### 13a. KPI Cards Component
**Location:** `dashboard/src/components/KPICards.jsx:1-40`

**Component Props:**
```javascript
<KPICards data={summaryData} />
```

**Rendered Output (Conceptual):**
```
┌─────────────────────────────────────────────────────────────────────┐
│  📊 TOTAL EVENTS      🚗 TOTAL VEHICLES   ⚡ AVG SPEED   ⚠️  ANOMALIES │
│       5                    205               39.2 km/h        3      │
└─────────────────────────────────────────────────────────────────────┘
```

**HTML Structure:**
```html
<div class="kpi-cards">
    <div class="kpi-card">
        <h3>Total Events</h3>
        <p class="kpi-value">5</p>
    </div>
    <div class="kpi-card">
        <h3>Total Vehicles</h3>
        <p class="kpi-value">205</p>
    </div>
    <div class="kpi-card">
        <h3>Average Speed</h3>
        <p class="kpi-value">39.2 km/h</p>
    </div>
    <div class="kpi-card">
        <h3>Anomalies Detected</h3>
        <p class="kpi-value">3</p>
    </div>
</div>
```

**Notes:** Event 1523's data is aggregated into these KPIs:
- Total Events: 5 (includes event 1523)
- Total Vehicles: 205 (includes event 1523's 42 vehicles)
- Average Speed: 39.2 km/h (includes event 1523's 38.47 km/h in calculation)
- Anomalies: 3 (does NOT include event 1523 - it's not an anomaly)

---

### 13b. Time Series Chart Component
**Location:** `dashboard/src/components/TimeSeriesChart.jsx:1-76`

**Component Props:**
```javascript
<TimeSeriesChart data={timeseriesData} />
```

**Chart Data Format (Recharts):**
```javascript
{
    data: [
        {
            time: "Jan 9, 2:00 PM",  // Formatted from time_bucket
            vehicles: 205,            // vehicle_count
            speed: 39.17             // avg_speed
        }
    ],
    xAxis: "time",
    yAxisLeft: "vehicles",
    yAxisRight: "speed"
}
```

**Rendered Output (Conceptual):**
```
Vehicle Count & Speed Over Time
────────────────────────────────────────────────────────────
250 │                                                    │ 50
    │                                                    │
200 │              ●                                     │ 40
    │                                                    │
150 │                                                    │ 30
    │                                                    │
100 │                                                    │ 20
    │                                                    │
 50 │                                                    │ 10
    │                                                    │
  0 └────────────────────────────────────────────────────┘ 0
    14:00        14:15        14:30        14:45        15:00
         ─── Vehicle Count (left axis)  ─── Avg Speed (right axis)
```

**Notes:**
- Single data point at 14:00 hour containing aggregated data
- Event 1523 contributes to the plotted point (205 vehicles, 39.17 km/h avg)

---

### 13c. Trend Suggestions Component
**Location:** `dashboard/src/components/TrendSuggestions.jsx:1-52`

**Component Props:**
```javascript
<TrendSuggestions suggestions={trendsData} />
```

**Rendered Output (Conceptual):**
```
┌─────────────────────────────────────────────────────────────────┐
│ AI-Generated Insights                                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 🔔 Congestion Alert (Medium Confidence)                        │
│ Generated: Jan 9, 2025 at 2:20 PM                              │
│                                                                 │
│ High vehicle density detected at location 2. Consider          │
│ adjusting signal timing or investigating potential traffic     │
│ diversion from nearby routes. Low-speed patterns suggest       │
│ possible congestion.                                            │
│                                                                 │
│ Related anomalies: 2                                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**HTML Structure:**
```html
<div class="trend-suggestions">
    <h2>AI-Generated Insights</h2>
    <div class="suggestion-card">
        <div class="suggestion-header">
            <span class="suggestion-type">Congestion Alert</span>
            <span class="confidence-badge medium">Medium Confidence</span>
        </div>
        <p class="suggestion-time">Generated: Jan 9, 2025 at 2:20 PM</p>
        <p class="suggestion-description">
            High vehicle density detected at location 2. Consider adjusting
            signal timing or investigating potential traffic diversion from
            nearby routes. Low-speed patterns suggest possible congestion.
        </p>
        <p class="suggestion-meta">Related anomalies: 2</p>
    </div>
</div>
```

**Notes:**
- This suggestion was NOT triggered by event 1523
- Event 1523 was normal and didn't generate anomalies or suggestions

---

## Step 14: User Visualization - Final Display

### What the User Sees (Complete Dashboard View):

```
═════════════════════════════════════════════════════════════════════════
                         PatternScope Dashboard
═════════════════════════════════════════════════════════════════════════

Date Range: [2025-01-09 14:00] to [2025-01-09 15:00]  [Refresh ↻]

─────────────────────────────────────────────────────────────────────────
                              Key Metrics
─────────────────────────────────────────────────────────────────────────

    📊 TOTAL EVENTS       🚗 TOTAL VEHICLES    ⚡ AVG SPEED     ⚠️  ANOMALIES
          5                     205              39.2 km/h           3

─────────────────────────────────────────────────────────────────────────
                     Vehicle Count & Speed Over Time
─────────────────────────────────────────────────────────────────────────

250 │                                                             │ 50
    │                                                             │
200 │              ●                                              │ 40
    │                                                             │
150 │                                                             │ 30
    │                                                             │
100 │                                                             │ 20
    │                                                             │
 50 │                                                             │ 10
    │                                                             │
  0 └─────────────────────────────────────────────────────────────┘ 0
    14:00         14:15         14:30         14:45         15:00
         ─── Vehicle Count (left axis)    ─── Avg Speed (right axis)

─────────────────────────────────────────────────────────────────────────
                        AI-Generated Insights
─────────────────────────────────────────────────────────────────────────

 🔔 Congestion Alert (Medium Confidence)
 Generated: Jan 9, 2025 at 2:20 PM

 High vehicle density detected at location 2. Consider adjusting signal
 timing or investigating potential traffic diversion from nearby routes.
 Low-speed patterns suggest possible congestion.

 Related anomalies: 2

═════════════════════════════════════════════════════════════════════════
```

---

## Summary: Event 1523's Journey

### Data Transformations:
1. **Python Dict** → 2. **JSON over HTTP** → 3. **TypeScript Interface** → 4. **PostgreSQL Row** → 5. **SQL Result Set** → 6. **Pandas DataFrame** → 7. **NumPy Arrays** (ML algorithms) → 8. **Aggregated SQL Results** → 9. **JSON API Response** → 10. **React Component Props** → 11. **Rendered HTML/SVG**

### Event 1523's Contribution to Dashboard:
- ✅ **Total Events**: Counted (+1)
- ✅ **Total Vehicles**: Added 42 vehicles to total of 205
- ✅ **Average Speed**: Contributed 38.47 km/h to average of 39.17 km/h
- ✅ **Timeseries Chart**: Part of the single data point at 14:00 hour
- ❌ **Anomalies**: Not flagged (passed all detection algorithms)
- ❌ **AI Insights**: Did not trigger any LLM suggestions

### Red Car Data Preservation:
- **Stored in database**: `color_counts.red = 4` in JSONB column
- **Not used in anomaly detection**: Color data not fetched for analysis
- **Available for future queries**: Can be queried from `traffic_events` table
- **Potential use cases**: Color distribution analysis, trend detection over time

### Final Status:
**Event 1523 successfully traversed the entire PatternScope pipeline as a NORMAL event, contributing to aggregate statistics but not triggering any anomaly alerts or AI-generated insights.**
