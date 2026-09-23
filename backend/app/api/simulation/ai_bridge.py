"""Integrator-owned adapter: frontend camelCase -> verified AI snake_case facts.

The AI owner's routers are deliberately not mounted: they accept client numbers.
Their service and report builder are reused without editing AI-owned files.
"""

import importlib
import logging
from collections.abc import Callable
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.api.simulation.routes import invalid_response
from app.models.schemas import Analysis, AnalyzeRequest, ErrorResponse, ExplainRequest
from app.simulation.catalog import Catalog
from app.simulation.service import ai_snapshot, simulate

logger = logging.getLogger(__name__)
Generator = Callable[[str, dict[str, Any]], dict[str, Any]]


def unavailable(message: str = "AI-анализ временно недоступен. Расчётные результаты сохранены."):
    return JSONResponse(
        status_code=503,
        content=ErrorResponse(message=message, code="AI_UNAVAILABLE").model_dump(by_alias=True),
    )


def create_ai_bridge(catalog: Catalog, generator: Generator | None) -> APIRouter:
    router = APIRouter(tags=["AI integration"])

    def run(decisions, question):
        result = simulate(decisions, catalog, finalize=True)
        if result.validation.status == "invalid":
            return invalid_response(result.validation.errors)
        if generator is None:
            return unavailable()
        try:
            schemas = importlib.import_module("app.ai.schemas")
            service = importlib.import_module("app.ai.service")
            request = schemas.AnalysisRequest(scenario=ai_snapshot(result, catalog), question=question)
            analysis = service.analyze_scenario(request, generator)
            return request.scenario, analysis
        except Exception as exc:
            # Log only the class: provider messages can contain credentials or prompt data.
            logger.warning("AI integration failed (%s)", type(exc).__name__)
            return unavailable()

    def response(decisions, question):
        outcome = run(decisions, question)
        if isinstance(outcome, JSONResponse):
            return outcome
        _, analysis = outcome
        return Analysis(
            summary=analysis.answer
            or (
                analysis.strengths[0].text
                if analysis.strengths
                else "AI-анализ сценария сформирован; выводы приведены ниже."
            ),
            strengths=[f.text for f in analysis.strengths],
            risks=[f.text for f in analysis.risks],
            tradeoffs=[f.text for f in analysis.tradeoffs],
            recommendations=analysis.recommendations,
        )

    @router.post(
        "/api/ai/analyze",
        response_model=Analysis,
        responses={503: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
    )
    def analyze(request: AnalyzeRequest):
        # Ignore ALL supplied costs, scores, IDs of cached scenarios and validation flags.
        return response(request.simulation.decisions, request.question)

    @router.post(
        "/api/explain",
        response_model=Analysis,
        responses={503: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
    )
    def explain(request: ExplainRequest):
        return response(request.decisions, request.question)

    @router.post(
        "/api/report/executive-brief",
        responses={503: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
    )
    def report(request: ExplainRequest):
        outcome = run(request.decisions, request.question)
        if isinstance(outcome, JSONResponse):
            return outcome
        scenario, analysis = outcome
        try:
            module = importlib.import_module("app.report.executive_brief")
            return module.build_executive_brief(scenario, analysis)
        except Exception as exc:
            logger.warning("Report integration failed (%s)", type(exc).__name__)
            return unavailable("Генерация отчёта временно недоступна. Расчёт работает.")

    return router
