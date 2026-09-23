# AI analyst and executive report

This package explains and summarizes results calculated by the deterministic simulation engine. It does not calculate scores, budgets, indicator changes, or policy validity.

## Production integration

The production API is mounted by `app.api.simulation.ai_bridge` from `app.main`. That adapter is owned by the backend/integration role. It re-validates submitted decisions, recalculates the scenario with the simulation engine, and only then passes the engine-generated `ScenarioSnapshot` to this package.

The public routes in the shared API contract are:

- `POST /api/ai/analyze`: the frontend sends scenario decisions; the adapter rebuilds the trusted snapshot and returns structured findings with evidence.
- `POST /api/explain`: accepts decisions and an optional question; the adapter rebuilds the snapshot and returns a concise analysis.
- `POST /api/report/executive-brief`: accepts decisions and an optional question; the adapter rebuilds the snapshot, runs analysis, and returns `ExecutiveBrief` fields plus Markdown.

Do not mount `create_ai_router()` or `create_report_router()` alongside the production adapter. The standalone routers accept AI input models directly and are for isolated module checks only; mounting both creates duplicate routes and can bypass the backend's source-of-truth recalculation.

## City Council advice

`advise_scenario()` accepts an `AdviceRequest` and returns up to three measure/district suggestions. It checks that suggested IDs exist in the candidate set supplied to it, are not already selected, and match city/district scope.

The advice service does not decide whether a suggested plan is valid. Before presenting or applying a suggestion, the backend adapter must build the request from trusted catalog/current-state data and run the suggested decisions through the simulation validator. Never accept candidate facts or scores from the browser as authoritative. The current shared API contract does not expose `/api/ai/advice`; the integrator must add and document that route before the frontend can call it.

## Data and model boundaries

`ScenarioSnapshot` contains engine-computed scores, budget totals, decisions, district before/after values, optional category/indicator facts, critical-indicator counts, and synergies. Prompts treat user text and JSON values as untrusted input. The model may explain supplied facts and suggest next steps, but must not invent or recompute numerical outcomes.

The executive brief is a structured JSON response with a Markdown body for preview/export. This package does not generate PDF or DOCX files.

## Provider configuration

The OpenAI provider reads `backend/.env` when configured; process environment variables take precedence. Keep the API key only in local `backend/.env`, which must remain untracked. Never place keys in source code, `.env.example`, fixtures, or commit history.

`OPENAI_MODEL` is optional and defaults to `gpt-6-astra`. Install AI dependencies with `pip install -r backend/requirements-ai.txt` (from the repository root) or follow the backend setup instructions.

## Examples and checks

- `examples/analysis_request.json` and `examples/analysis_response.json` show the internal analysis contract.
- `examples/advice_request.json` shows the internal advice/candidate contract.
- Fixtures are synthetic and illustrative; production values must come from the simulation engine.
- Run `python backend/scripts/check_ai_contract.py` after the AI package and backend adapter are in the same checkout. The script accepts `--ai-root` for a separate AI checkout.
