"""FastAPI route factory for the on-premise meeting analysis service."""
from fastapi import APIRouter

from .schemas import AnalysisRequest, MeetingAnalysis
from .service import LocalJsonGenerator, analyze_meeting


def create_ai_router(local_generate_json: LocalJsonGenerator) -> APIRouter:
    """Create routes using the application's configured local model adapter."""
    router = APIRouter()

    @router.post("/api/meetings/analyze", response_model=MeetingAnalysis)
    def analyze(request: AnalysisRequest) -> MeetingAnalysis:
        return analyze_meeting(request, local_generate_json)

    return router
