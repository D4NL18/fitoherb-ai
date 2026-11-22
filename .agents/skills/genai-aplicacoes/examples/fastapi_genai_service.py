"""
Serviço FastAPI assíncrono para aplicações de IA Generativa (texto e imagem).

Demonstra:
- Validação rigorosa de entrada e saída com Pydantic v2 (limites de payload e enums).
- Cliente assíncrono (AsyncOpenAI) com timeout explícito.
- Tratamento padronizado de erros (rate limit, timeout, falha de upstream) sem vazar stacktraces.
- Envelope de resposta consistente com metadados de rastreamento.
"""

from __future__ import annotations

import logging
import os
import uuid
from enum import Enum
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from openai import APIConnectionError, APITimeoutError, AsyncOpenAI, RateLimitError
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger("genai_service")
logging.basicConfig(level=logging.INFO)

MAX_PROMPT_CHARS = 4_000
MAX_IMAGE_PROMPT_CHARS = 1_500
REQUEST_TIMEOUT_SECONDS = 30.0


class ImageSize(str, Enum):
    SQUARE = "1024x1024"
    LANDSCAPE = "1792x1024"
    PORTRAIT = "1024x1792"


class ImageQuality(str, Enum):
    STANDARD = "standard"
    HD = "hd"


class TextGenerationRequest(BaseModel):
    prompt: str = Field(..., min_length=3, max_length=MAX_PROMPT_CHARS)
    system_prompt: str = Field(
        default="Você é um assistente técnico objetivo e preciso.",
        max_length=1_000,
    )
    model: str = Field(default="gpt-4o-mini", pattern=r"^[a-zA-Z0-9._-]+$")
    temperature: float = Field(default=0.3, ge=0.0, le=1.5)
    max_tokens: int = Field(default=600, ge=16, le=2_000)

    @field_validator("prompt", "system_prompt")
    @classmethod
    def strip_and_validate_non_empty(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("O campo não pode conter apenas espaços em branco.")
        return cleaned


class ImageGenerationRequest(BaseModel):
    prompt: str = Field(..., min_length=5, max_length=MAX_IMAGE_PROMPT_CHARS)
    size: ImageSize = Field(default=ImageSize.SQUARE)
    quality: ImageQuality = Field(default=ImageQuality.STANDARD)

    @field_validator("prompt")
    @classmethod
    def strip_prompt(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("O prompt de imagem não pode estar vazio.")
        return cleaned


class ApiEnvelope(BaseModel):
    data: dict[str, Any]
    meta: dict[str, Any]


app = FastAPI(
    title="GenAI Service API",
    version="1.0.0",
    description="API assíncrona para geração de texto e imagem com validação Pydantic v2.",
)


def get_openai_client() -> AsyncOpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Provedor de IA não configurado no ambiente.",
        )
    return AsyncOpenAI(api_key=api_key, timeout=REQUEST_TIMEOUT_SECONDS, max_retries=2)


@app.exception_handler(RateLimitError)
async def handle_rate_limit(_request: Request, _exc: RateLimitError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": "RATE_LIMIT_EXCEEDED",
            "message": "Limite de requisições ao provedor de IA atingido. Tente novamente em instantes.",
        },
    )


@app.exception_handler(APITimeoutError)
async def handle_timeout(_request: Request, _exc: APITimeoutError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        content={
            "error": "UPSTREAM_TIMEOUT",
            "message": "O provedor de IA excedeu o tempo limite de resposta.",
        },
    )


@app.exception_handler(APIConnectionError)
async def handle_connection_error(_request: Request, _exc: APIConnectionError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={
            "error": "UPSTREAM_UNAVAILABLE",
            "message": "Não foi possível conectar ao provedor de IA.",
        },
    )


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/generate/text", response_model=ApiEnvelope)
async def generate_text(payload: TextGenerationRequest) -> ApiEnvelope:
    request_id = str(uuid.uuid4())
    client = get_openai_client()

    logger.info("text_generation_started request_id=%s model=%s", request_id, payload.model)
    completion = await client.chat.completions.create(
        model=payload.model,
        messages=[
            {"role": "system", "content": payload.system_prompt},
            {"role": "user", "content": payload.prompt},
        ],
        temperature=payload.temperature,
        max_tokens=payload.max_tokens,
    )

    content = completion.choices[0].message.content or ""
    usage = completion.usage
    return ApiEnvelope(
        data={"content": content, "model": payload.model},
        meta={
            "request_id": request_id,
            "prompt_tokens": usage.prompt_tokens if usage else None,
            "completion_tokens": usage.completion_tokens if usage else None,
        },
    )


@app.post("/v1/generate/image", response_model=ApiEnvelope)
async def generate_image(payload: ImageGenerationRequest) -> ApiEnvelope:
    request_id = str(uuid.uuid4())
    client = get_openai_client()

    logger.info(
        "image_generation_started request_id=%s size=%s quality=%s",
        request_id,
        payload.size.value,
        payload.quality.value,
    )
    response = await client.images.generate(
        model="dall-e-3",
        prompt=payload.prompt,
        size=payload.size.value,
        quality=payload.quality.value,
        n=1,
        response_format="url",
    )

    image_item = response.data[0]
    return ApiEnvelope(
        data={
            "image_url": image_item.url,
            "revised_prompt": image_item.revised_prompt,
        },
        meta={
            "request_id": request_id,
            "size": payload.size.value,
            "quality": payload.quality.value,
            "url_ttl_minutes": 60,
        },
    )
