"""OpenAI Responses API adapter for schema-constrained city analysis."""
import json
import os
from pathlib import Path
from typing import Any

from .schemas import AnalysisResponse
from .service import JsonGenerator


def _load_local_backend_env() -> None:
    """Load simple KEY=VALUE entries from backend/.env without overriding env."""
    env_path = Path(__file__).resolve().parents[2] / ".env"
    try:
        lines = env_path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return

    for line in lines:
        item = line.strip()
        if not item or item.startswith("#"):
            continue
        if item.startswith("export "):
            item = item[7:].lstrip()
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        if key:
            os.environ.setdefault(key, value)


def create_openai_json_generator(
    client: Any | None = None,
    model: str | None = None,
) -> JsonGenerator:
    """Return a lazy provider adapter using the OpenAI Python SDK.

    Reads backend/.env if present. Environment variables already set by the
    host take precedence. Keep the local file out of Git; client creation is
    deferred until the first analysis request.
    """
    _load_local_backend_env()
    selected_model = model or os.getenv("OPENAI_MODEL", "gpt-6-astra")
    active_client = client

    def generate(system_prompt: str, payload: dict[str, Any]) -> dict[str, Any]:
        nonlocal active_client
        if active_client is None:
            try:
                from openai import OpenAI
            except ImportError as exc:
                raise RuntimeError(
                    "The AI endpoint requires the 'openai' Python package."
                ) from exc
            active_client = OpenAI()

        response = active_client.responses.parse(
            model=selected_model,
            input=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": json.dumps(payload, ensure_ascii=False),
                },
            ],
            text_format=AnalysisResponse,
        )
        parsed = response.output_parsed
        if parsed is None:
            raise RuntimeError(
                "The AI provider returned no structured analysis "
                "(the response may be a refusal or incomplete)."
            )
        return parsed.dict()

    return generate
