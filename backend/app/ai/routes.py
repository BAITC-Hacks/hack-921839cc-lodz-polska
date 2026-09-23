"""FastAPI routes for explaining completed simulation scenarios."""
from fastapi import APIRouter

from .openai_provider import create_openai_json_generator
from .schemas import AnalysisRequest, AnalysisResponse
from .service import JsonGenerator, analyze_scenario


def create_ai_router(generate_json: JsonGenerator | None = None) -> APIRouter:
    """Create the analyst router with an injected or default OpenAI adapter."""
    provider = generate_json or create_openai_json_generator()
    router = APIRouter()

    @router.post("/api/ai/analyze", response_model=AnalysisResponse)
    def analyze(request: AnalysisRequest) -> AnalysisResponse:
        return analyze_scenario(request, provider)

    return router
