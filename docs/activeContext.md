# Active Context

## Current Status & Milestones
* **Development Phase**: Completed comprehensive system audit and bug fixing.
* **Current Milestone**: E2E Verification & Stabilization.
* **Target Date**: 23/05/2026 (Internal E2E pass deadline).

## Key Updates & Fixes
1. **Dynamic Origin for Frontend API (`client.js`)**:
   * *Problem*: `BASE_URL` in `client.js` was hardcoded to `http://127.0.0.1:8000/api`, causing CORS issues and violating the "no direct backend port calling from browser" rule in `TASKS.md`. Since the backend service port 8000 is not exposed externally in `docker-compose.yml`, this would have broken the production stack.
   * *Fix*: Replaced it with `window.location.origin + '/api'` to allow same-origin routing via Nginx (port 80).
2. **Citation Formatting instructions**:
   * *Problem*: The frontend `ChatScene.js` extracts citation metadata from response text using a regex matching the `- filename, Trang X` pattern. However, the backend LLM prompts did not instruct the generator to produce citations in this format.
   * *Fix*: Updated `_SYSTEM_PROMPT` in `chat_runtime.py` and `SYSTEM_PROMPT` in `step4_generator.py` to enforce the `- tên_file, Trang X` format.
3. **Pandas downcasting Warning**:
   * *Problem*: Processing tabular data generated a deprecation warning regarding object downcasting.
   * *Fix*: Added `pd.set_option('future.no_silent_downcasting', True)` in `tabular_parser.py`.

## Next Steps
* Run integration tests using Docker Compose to verify Nginx routing and Celery worker operation.
* Conduct evaluation sweeps using `ragas_eval.py`.
