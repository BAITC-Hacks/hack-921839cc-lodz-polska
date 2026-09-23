# AI analyst and executive report

This module explains completed simulation results. It does not implement an
alternative simulation engine and does not calculate official scores.

## Input and output

`ScenarioSnapshot` is the internal AI input shape. It contains computed
scores, budget totals, selected decision summaries, district before/after
scores, optional indicator/category values, and optional synergy labels. The
simulation service remains the source of truth for all values and validation.

The proposed HTTP boundaries, subject to the backend owner's shared API
contract, are:

- `POST /api/ai/analyze`: body `AnalysisRequest`; response `AnalysisResponse`.
- `POST /api/report/executive-brief`: body contains a `ScenarioSnapshot` and
  validated `AnalysisResponse`; response `ExecutiveBrief`.

`create_ai_router(generate_json)` and `create_report_router()` expose FastAPI
routers for these paths. The application entry point should include both after
the backend owner confirms the shared contract. The routers are not mounted
automatically because the repository currently has no application entry point.

`analyze_scenario(request, generate_json)` accepts an injected provider
function and validates its structured result. This keeps credentials and vendor
SDK choices outside this module. The provider must receive only the completed
simulation result, never raw decisions for recalculation.

`build_executive_brief(scenario, analysis)` returns structured fields and
Markdown suitable for a report preview or export. It carries engine numbers
through verbatim.
