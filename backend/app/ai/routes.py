"""FastAPI routes for explaining completed simulation scenarios."""
from fastapi import APIRouter

from .schemas import AnalysisRequest, AnalysisResponse
from .service import JsonGenerator, analyze_scenario


def create_ai_router(generate_json: JsonGenerator) -> APIRouter:
    """Create the analyst router with the application's configured LLM adapter."""
    router = APIRouter()

    @router.post("/api/ai/analyze", response_model=AnalysisResponse)
    def analyze(request: AnalysisRequest) -> AnalysisResponse:
        return analyze_scenario(request, generate_json)

    return router
