# AI analyst and executive report

This module explains completed simulation results. It does not implement an
alternative simulation engine and does not calculate official scores.

## Input and output

ScenarioSnapshot is the internal AI input shape. It contains computed scores,
budget totals, selected decision summaries, district before/after scores,
optional indicator/category values, and optional synergy labels. The
simulation service remains the source of truth for all values and validation.

The proposed HTTP boundaries, subject to the backend owner's shared API
contract, are:

- POST /api/ai/analyze: body AnalysisRequest; response AnalysisResponse.
- POST /api/report/executive-brief: body contains a ScenarioSnapshot and
  validated AnalysisResponse; response ExecutiveBrief.

create_ai_router() and create_report_router() expose FastAPI routers. Mount
them from the application entry point with app.include_router(...) after the
backend owner confirms the shared contract. The repository currently has no
application entry point, so they are not mounted automatically.

## Model provider

Install the openai Python package and set OPENAI_API_KEY in the server
environment. Never commit the key. OPENAI_MODEL is optional; it defaults to
gpt-6-astra. create_ai_router() uses this provider by default; pass a
generate_json callable to inject another configured provider.

The provider uses the Responses API with a Pydantic structured output model.
The prompt and input contain only the completed simulation result and optional
analysis question. The model explains results; it never recalculates scores or
policy effects.

## Examples

- examples/analysis_request.json shows the precomputed scenario sent to the AI.
- examples/analysis_response.json shows the expected structured analysis.

These are illustrative demo values from the project plan, not a live model
response or a new simulation run. Replace them with the simulation engine's
actual response when the shared API contract is ready.

build_executive_brief(scenario, analysis) returns structured fields and
Markdown suitable for a report preview or export. The report includes overall
score, budget, district comparison, selected decisions, AI findings, synergies,
and recommendations. It carries engine numbers through verbatim.
