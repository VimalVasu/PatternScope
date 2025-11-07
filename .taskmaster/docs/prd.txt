

## Updated PRD with Guardrails for Claude Code

### 0. Meta Instructions for Any Dev Agent (Read This First)

* **Use ONE backend stack:** TypeScript + Node + Fastify (or Express). Do **not** mix Python backend code.
* **Use Python only in `analysis/` and `edge/` services.**
* **Implement in phases. Do not implement Phase N+1 features in earlier phases.**
* **Always keep `traffic_events` schema consistent across:**

  * DB migration
  * `/ingest/traffic` request body
  * analysis queries
* **Use deterministic ML/stats for anomalies. Only use Ollama for natural language summaries.**

---

## 1. Product Overview

**Working Name:** PatternScope

**Objective:** Local-first system to:

* Ingest structured traffic observations (derived from camera feed).
* Store all data permanently.
* Run local ML anomaly detection.
* Use local LLM (Ollama) to produce human-readable “suggested trends".
* Visualize metrics + suggestions minimally on a web dashboard.

**Non-goals v1:**

* No multi-tenant auth.
* No cloud-only services.
* No heavy UI.

**Recommendation (Claude Code):**
Keep everything runnable via `docker-compose up` on a single machine. No external SaaS is required or assumed.

---

## 2. Architecture

### 2.1 Stack

* `edge/`: Python + OpenCV. Publishes JSON to backend.
* `backend/`: Node + TypeScript + Fastify (pick & stick).
* `db/`: Postgres via Docker.
* `analysis/`: Python (pandas, numpy, scikit-learn) + Ollama HTTP.
* `dashboard/`: React (Vite or Next) + simple charts.
* `tests-e2e/`: Playwright.

**Recommendation (Claude Code):**

* Do **not** introduce Flask/Django for backend.
* Do **not** put Ollama calls inside the backend request path. Keep them in `analysis/`.
* Use Docker service names (`backend`, `db`, `analysis`, `ollama`) instead of `localhost`.

### 2.2 Repo Layout

```txt
patternscope/
  edge/
  backend/
  analysis/
  dashboard/
  db/
  tests-e2e/
  docker-compose.yml
  README.md
```

**Recommendation (Claude Code):**

* Respect this structure exactly.
* No extra top-level apps.
* Each folder has its own `README` with how to run tests inside that service.

---

## 3. Data Model

### 3.1 `traffic_events` Table

Columns:

* `id SERIAL PRIMARY KEY`
* `timestamp TIMESTAMPTZ NOT NULL`
* `location_id TEXT NOT NULL DEFAULT 'cam-1'`
* `vehicle_count INT NOT NULL`
* `avg_speed DOUBLE PRECISION`
* `min_speed DOUBLE PRECISION`
* `max_speed DOUBLE PRECISION`
* `color_counts JSONB`
* `inter_arrival_stats JSONB`
* `traffic_density_score DOUBLE PRECISION`
* `raw_features JSONB`

**Recommendation (Claude Code):**

* Put this in a migration file `db/migrations/001_init.sql`.
* Use **the exact same names** in:

  * TypeScript types in `backend`.
  * Python models in `analysis`.
* Do not add columns ad-hoc in code without changing migrations.

### 3.2 `anomalies`, `trend_suggestions`

Keep as in previous PRD.

**Recommendation (Claude Code):**

* For `trend_suggestions.description`, store LLM output verbatim.
* For tests, allow injecting a fake “LLM client” to avoid real Ollama calls.

---

## 4. Phased Development Cycles

### Phase 0 — Skeleton & Environment

**Goal:** Minimal but correct multi-service skeleton.

**Deliverables:**

* `docker-compose.yml` with services:

  * `db`, `backend`, `dashboard`, `analysis`, `edge-mock`, `ollama` (if needed).
* Boilerplate `Dockerfile` for each.
* Health-check endpoints:

  * `GET /health` for backend.
  * Root route 200 for dashboard.
  * `analysis` `/health`.

**Recommendation (Claude Code):**

* Do **not** implement ingestion or AI logic here.
* All services must start even if they “do nothing” yet.
* Use env var templates: `.env.example` in each service.
* For Ollama: assume it runs as `ollama` Docker service or on host; make base URL configurable.

**Tests:**

* Simple script run by CI:

  * `docker-compose build`
  * `docker-compose up -d`
  * Curl backend `/health`.

---

### Phase 1 — Ingestion API & Mock Data Flow

**Goal:** Accept JSON traffic events and persist them.

**Scope:**

1. **Backend**

   * `POST /ingest/traffic`

     * Validates JSON body.
     * Writes 1 row into `traffic_events`.
   * `GET /metrics/traffic?start&end`

     * Returns:

       * total vehicle_count,
       * avg_speed,
       * timeseries if needed.

2. **DB**

   * Apply `001_init.sql` migration on startup.

3. **Mock Publisher (`edge-mock`)**

   * Sends valid random JSON every N seconds to `/ingest/traffic`.

**Recommendation (Claude Code):**

* Validate payload server-side; respond 400 on invalid.
* Do **not** auto-create tables in code; rely on migrations.
* Mock publisher:

  * lives in its own container `edge-mock`.
  * uses `http://backend:PORT/ingest/traffic`, **not** `localhost`.

**Tests:**

* Unit:

  * Schema validation.
  * Repository/DB write.
* Integration:

  * Run backend + db.
  * Call `/ingest/traffic` with sample payload.
  * Query DB to confirm insert.
* E2E (Playwright API-only or Node script):

  * Start `backend + db + edge-mock`.
  * Assert `traffic_events` row count > 0.

---

### Phase 2 — AI Analysis Engine

**Goal:** Deterministic anomaly detection + LLM-based summarization.

**Scope:**

1. **Analysis Service** (`analysis/`)

   * Scheduled job or `/run-analysis` endpoint.
   * Pulls `traffic_events` for period.
   * Computes:

     * basic rolling stats,
     * anomalies using:

       * z-score,
       * IQR,
       * or Isolation Forest / KNN on numeric features.
   * Writes rows into `anomalies`.

2. **Trend Suggestions via Ollama**

   * Summarize anomalies + recurring patterns.
   * Output bullet-style suggestions into `trend_suggestions`.

**Recommendation (Claude Code):**

* **Do not** use LLM to classify raw events or detect anomalies.

  * Use scikit-learn/stats only.
* Implement LLM client with:

  * URL + model from env.
  * Timeout + basic error handling.
* Add an interface so in tests:

  * the LLM client is replaced by a stub returning fixed text.
* Do not hardwire Ollama to `localhost` inside containers; use env.

**Tests:**

* Unit:

  * Given fixed synthetic dataset, anomaly detector returns expected anomalies.
* Integration:

  * Hit `/run-analysis` after seeding events.
  * Verify anomalies + trend_suggestions created.
* E2E:

  * Start stack with stub LLM.
  * Run ingest → run analysis → confirm new suggestions.

---

### Phase 3 — Dashboard UI

**Goal:** Minimal UI for metrics + suggestions.

**Views:**

1. Controls:

   * Start datetime, end datetime inputs.
   * Refresh button.
2. KPIs:

   * Total vehicles.
   * Avg speed.
   * # anomalies.
3. Chart:

   * vehicle_count over time.
4. Trend Suggestions:

   * List of suggestions from `trend_suggestions`.

**API Dependencies:**

* `GET /dashboard/summary?start&end`
* `GET /dashboard/timeseries?start&end`
* `GET /trends/suggestions?start&end`

**Recommendation (Claude Code):**

* No extra filters, no auth.
* Use a thin `api.ts` client module.
* In Playwright, **wait for specific text** (e.g. “Total Vehicles”) instead of arbitrary timeouts.

**Tests:**

* Unit:

  * Components with mocked API.
* E2E:

  * Seed data.
  * Visit dashboard.
  * Select date range.
  * Click refresh.
  * Assert:

    * KPIs show non-zero values.
    * At least one suggestion is rendered.

---

### Phase 4 — Real Camera Integration

**Goal:** Swap mock with real Jetson camera pipeline.

**Scope:**

* `capture.py`: read camera frames.
* `detector.py`: extract:

  * #cars,
  * rough speeds,
  * color distribution.
* `publisher.py`: convert into JSON and POST to backend.

**Recommendation (Claude Code):**

* Keep this **configurable and isolated**:

  * `config.yaml` or env for camera index, ROI, frame rate.
* Do not hardcode file paths or assume x86.
* Provide:

  * one implementation for mock mode (existing),
  * one for real mode (to be tuned by you).
* Clearly mark:

```python
# YOUR_INPUT_REQUIRED:
# - tune detection thresholds
# - choose model/approach compatible with Jetson Nano
```

**Tests:**

* Local offline:

  * Run detector on recorded sample video.
  * Assert JSON structure matches ingestion schema.
* Robustness:

  * Handle camera disconnect without crashing publisher.

---

## 5. Consolidated “Claude Safety” Notes

When you paste this PRD into Claude Code (or similar), prepend:

1. **Use TypeScript Node backend + Python analysis only.**
2. **Implement strictly by phases.**
3. **Centralize schema; no silent renames.**
4. **Use deterministic anomaly math; LLM only for narrative.**
5. **Make everything Dockerized, configurable, and testable without real camera or real LLM.**
6. **Provide stub/mocks for:**

   * Ollama calls,
   * camera feed,
   * initial data.

But my spicy take is: if you enforce these guardrails and reject any code that violates stack choice, schema, or phase boundaries, you’ll train your agents into being actual junior engineers instead of autocomplete that happens to compile. Let me know what to adjust next time so I can serve you better.
