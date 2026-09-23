import importlib
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.simulation.ai_bridge import Generator, create_ai_bridge
from app.api.simulation.routes import create_router
from app.models.schemas import ErrorResponse, Issue
from app.simulation.catalog import Catalog, load_catalog

logger = logging.getLogger(__name__)


def configured_generator() -> Generator | None:
    load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)
    if not os.getenv("OPENAI_API_KEY"):
        return None
    try:
        provider = importlib.import_module("app.ai.openai_provider")
        sdk = importlib.import_module("openai")
        # The provider stays AI-owned; the integrator sets an explicit timeout/retry budget.
        return provider.create_openai_json_generator(client=sdk.OpenAI(timeout=15.0, max_retries=0))
    except Exception as exc:
        logger.warning("AI module unavailable (%s); simulation remains active", type(exc).__name__)
        return None


def create_app(
    *,
    catalog: Catalog | None = None,
    ai_generator: Generator | None = None,
    cors_origins: list[str] | None = None,
) -> FastAPI:
    catalog = catalog or load_catalog()
    application = FastAPI(
        title="AKIM AI — Аким на 5 часов",
        version="1.0.0",
        description="Учебная симуляция на синтетических данных. Детерминированные расчёты; AI объясняет готовые факты.",
    )
    origins = (
        cors_origins
        if cors_origins is not None
        else [
            origin.strip()
            for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
            if origin.strip()
        ]
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    @application.exception_handler(RequestValidationError)
    async def invalid_request(_request: Request, exc: RequestValidationError):
        errors = [
            Issue(code="INVALID_REQUEST", message=".".join(map(str, error["loc"])) + ": " + error["msg"])
            for error in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                message="Неверный формат запроса. Проверьте поля по API-контракту.",
                code="INVALID_REQUEST",
                errors=errors,
            ).model_dump(by_alias=True),
        )

    @application.get("/api/health", tags=["Health"])
    def health():
        return {
            "status": "ok",
            "modelVersion": catalog.version,
            "dataChecksum": catalog.checksum,
            "aiConfigured": ai_generator is not None,
        }

    application.include_router(create_router(catalog))
    application.include_router(create_ai_bridge(catalog, ai_generator))
    return application


app = create_app(ai_generator=configured_generator())
