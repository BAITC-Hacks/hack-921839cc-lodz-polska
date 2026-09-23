# AI analyst and executive report

This module explains completed simulation results and suggests possible next
measures. It does not implement an alternative simulation engine and does not
calculate official scores.

## Input and output

ScenarioSnapshot is the internal AI input shape. It contains computed scores,
budget totals, selected decision summaries, district before/after scores,
optional indicator/category values, and optional synergy labels. The
simulation service remains the source of truth for all values and validation.

The HTTP routes are:

- POST /api/ai/analyze: body AnalysisRequest; response AnalysisResponse.
- POST /api/ai/advice: body AdviceRequest; response AdviceResponse.
- POST /api/report/executive-brief: body contains a ScenarioSnapshot and
  validated AnalysisResponse; response ExecutiveBrief.

The City Council advice endpoint returns only suggested measure and district
IDs drawn from the candidate set. District selection and measure combination
validity must still be checked by the deterministic backend validator.

## Model provider

The provider reads backend/.env when the AI router is created; host environment
variables take precedence. backend/.env is ignored by Git. Never put the key
in source code or commit it.

OPENAI_MODEL is optional; it defaults to gpt-6-astra. The provider uses the
Responses API with Pydantic structured output. Analysis and advice prompts
contain only supplied scenario facts and candidate data. The model explains
results and suggests options; it never recalculates scores or policy effects.

## Examples

- examples/analysis_request.json shows a precomputed scenario sent to the AI.
- examples/analysis_response.json shows the expected structured analysis.
- examples/advice_request.json shows the current-state/candidate contract for
  the City Council endpoint.

The analysis fixtures are illustrative demo values from the project plan, not
a new simulation run. Replace them with the simulation engine's actual response
when the shared API contract is ready.

build_executive_brief(scenario, analysis) returns structured fields and
Markdown suitable for a report preview or export. The report carries engine
numbers through verbatim.

