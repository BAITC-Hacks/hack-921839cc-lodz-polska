"""Orchestration for AI analysis; scoring remains owned by the simulation engine."""
from collections.abc import Callable
from typing import Any

from .prompts import SYSTEM_PROMPT
from .schemas import AnalysisRequest, AnalysisResponse


JsonGenerator = Callable[[str, dict[str, Any]], dict[str, Any]]


def build_analysis_payload(request: AnalysisRequest) -> dict[str, Any]:
    """Build the data-only payload passed to a model provider."""
    return {
        "scenario": request.scenario.dict(),
        "question": request.question,
    }


def analyze_scenario(
    request: AnalysisRequest,
    generate_json: JsonGenerator,
) -> AnalysisResponse:
    """Ask an injected provider for schema-shaped analysis and validate it.

    The provider adapter is injected so the application can select its configured
    LLM client without coupling this module to credentials or a vendor SDK.
    """
    raw = generate_json(SYSTEM_PROMPT, build_analysis_payload(request))
    return AnalysisResponse.parse_obj(raw)
