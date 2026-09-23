"""OpenAI Responses API adapter for schema-constrained city analysis."""
import json
import os
from collections.abc import Callable
from typing import Any

from .schemas import AnalysisResponse
from .service import JsonGenerator


def create_openai_json_generator(
    client: Any | None = None,
    model: str | None = None,
) -> JsonGenerator:
    """Return a lazy provider adapter using the OpenAI Python SDK.

    Set OPENAI_API_KEY in the process environment. OPENAI_MODEL can override
    the default model. Client creation is deferred until the first request so
    importing or mounting the router does not require credentials.
    """
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
