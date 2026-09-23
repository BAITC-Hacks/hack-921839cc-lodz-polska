# AI analyst and executive report

This module explains completed simulation results. It does not implement an
alternative simulation engine and does not calculate official scores.

## Input and output

`ScenarioSnapshot` is the internal AI input shape. It contains computed
scores, budget totals, selected decision summaries, district before/after
scores, optional indicator/category deltas, and optional synergy labels. The
simulation service remains the source of truth for all values and validation.

The proposed HTTP boundaries, subject to the backend owner's shared API
contract, are:

- `POST /api/ai/analyze`: body `AnalysisRequest`; response `AnalysisResponse`.
- `POST /api/report/executive-brief`: body is a `ScenarioSnapshot` plus
  its validated `AnalysisResponse`; response `ExecutiveBrief`.

The route layer and provider adapter should be wired by the application owner
after the shared contract is available. Do not change the contract here.
`analyze_scenario(request, generate_json)` accepts an injected provider
function, validates its structured result, and prevents this package from
depending on API keys or a particular vendor SDK. An API handler must send only
the completed simulation result to that function, never raw decisions for
recalculation.

`build_executive_brief(scenario, analysis)` returns a structured object and
Markdown suitable for a report preview or export. It carries through engine
numbers verbatim.
