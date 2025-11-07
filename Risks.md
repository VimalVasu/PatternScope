* Risk hotspots where Claude Code is likely to misfire
* Updated PRD with explicit “do-not-screw-this-up” notes for Claude
* Final checklist for you to paste as a one-shot task

---

## 1. Where Claude Code is Most Likely to Screw Up

Brutally honest list:

1. **Ambiguous Tech Stack Choice**

   * You said “Node or Python”; PRD allowed both.
   * Claude will sometimes scaffold both or partially switch mid-file.

2. **Edge vs Backend Confusion**

   * Risk: it shoves camera capture, detection, analysis, and DB writes into one script.
   * Or it ignores the Jetson constraints and uses nonsense packages or GPU assumptions.

3. **Ollama Integration**

   * Common failure points:

     * Wrong base URL.
     * Tries to use cloud APIs instead of local.
     * Blocks main thread waiting for LLM.
     * No fallback/mocking for tests.

4. **Docker Networking & host.docker.internal**

   * Especially fragile:

     * Using `localhost` inside containers instead of service names.
     * Assuming `host.docker.internal` works everywhere.
     * Breaking Ollama or DB connectivity.

5. **Schema Drift Between Services**

   * Ingest API, DB, and analysis each define their own shape for `traffic_events`.
   * Claude often:

     * renames fields,
     * changes types (e.g., string vs JSONB),
     * or forgets required columns.

6. **Phase Violations**

   * You explicitly want phased cycles.
   * Claude tends to:

     * mix Phase 2+ logic into Phase 1,
     * add UI features not yet supported by backend,
     * or build E2E tests that depend on unfinished behavior.

7. **E2E + Test Environment**

   * Risk:

     * Writes Playwright tests that assume seed data that doesn’t exist.
     * No dedicated `docker-compose.test.yml`.
     * Uses unstable selectors and magic waits.

8. **Jetson & CV Models**

   * It might:

     * pull random YOLO models without install notes,
     * assume x86 runtime,
     * ignore perf constraints,
     * not separate mock vs real capture cleanly.

9. **LLM Overreach in Core Logic**

   * It might try to use the LLM for anomaly scoring instead of deterministic stats/ML.
   * That makes things slow, flaky, and untestable.

Below is the **same PRD**, upgraded with explicit recommendation notes aimed at Claude (and any agent) to keep it tight and deterministic.

---