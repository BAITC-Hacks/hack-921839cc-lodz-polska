"""Orchestrate structured analysis through an injected local model service."""
from collections.abc import Callable
from typing import Any

from .prompts import SYSTEM_PROMPT
from .schemas import AnalysisRequest, MeetingAnalysis


LocalJsonGenerator = Callable[[str, dict[str, Any]], dict[str, Any]]


def build_analysis_payload(request: AnalysisRequest) -> dict[str, Any]:
    """Serialize transcript input for the configured on-premise model service."""
    return {"meeting": request.meeting.dict()}


def analyze_meeting(
    request: AnalysisRequest,
    local_generate_json: LocalJsonGenerator,
) -> MeetingAnalysis:
    """Generate and validate a protocol without sending data to a cloud provider."""
    raw = local_generate_json(SYSTEM_PROMPT, build_analysis_payload(request))
    analysis = MeetingAnalysis.parse_obj(raw)
    if analysis.meeting_id != request.meeting.meeting_id:
        raise ValueError("Model output meeting_id does not match the input.")
    return analysis
