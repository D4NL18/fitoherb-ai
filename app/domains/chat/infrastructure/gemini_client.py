import os
import json
import logging
from typing import Callable, Optional, List, Dict, Any
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Modelo principal (Gemini 4 Hydrogen) + cadeia de fallback da família Flash
PRIMARY_MODEL = "gemini-4-hydrogen"
DEFAULT_MODEL = PRIMARY_MODEL
FALLBACK_FLASH_MODELS = [
    "gemini-3.8-flash",
    "gemini-flash-latest",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
]
CANDIDATE_MODELS = [PRIMARY_MODEL, *FALLBACK_FLASH_MODELS]

# Aliases de retrocompatibilidade
DEFAULT_FLASH_MODEL = PRIMARY_MODEL
CANDIDATE_FLASH_MODELS = FALLBACK_FLASH_MODELS


def _build_thinking_config(candidate_model: str, types_module: Any) -> Optional[Any]:
    """
    Constrói a configuração de thinking compatível com a geração do modelo candidato.
    - Gemini 4 (Hydrogen), Gemini 3.x e aliases modernos: NUNCA envia thinking_budget=0
      (incompatível com Gemini 4). Usa thinking_level="low" quando suportado pelo SDK,
      ou omite thinking_config caso contrário.
    - Modelos legados Gemini 2.5: desativa thinking via thinking_budget=0 para baixa latência.
    """
    thinking_cls = getattr(types_module, "ThinkingConfig", None)
    if thinking_cls is None:
        return None

    model_lower = (candidate_model or "").lower()
    model_fields = getattr(thinking_cls, "model_fields", None)

    if model_lower.startswith("gemini-2.5"):
        if isinstance(model_fields, dict) and "thinking_budget" not in model_fields:
            return None
        try:
            return thinking_cls(thinking_budget=0)
        except Exception:
            return None

    # Gemini 4 Hydrogen, Gemini 3.x e aliases modernos
    if isinstance(model_fields, dict):
        if "thinking_level" not in model_fields:
            return None
        try:
            return thinking_cls(thinking_level="low")
        except Exception:
            return None

    try:
        return thinking_cls(thinking_level="low")
    except TypeError:
        return None


class GeminiChatDecision(BaseModel):
    reply: str = Field(description="Resposta curta e direta em portugues, maximo 2 a 3 frases, sem travessao no meio das frases e sem palavras dificeis. Trate todas as marcas com igual neutralidade.")
    should_redirect: bool = Field(description="True se o usuario estiver perguntando ou buscando produtos do catalogo.")
    catalog_search: str = Field(default="", description="Termo de busca semantico limpo e contextualizado para filtrar o catalogo no backend (ex: whey 100%, creatina, whey 100% morango). Vazio se nao for busca de produtos.")
    category_slug: Optional[str] = Field(default=None, description="Slug da categoria se identificada.")
    supplier_slug: Optional[str] = Field(default=None, description="Slug do fornecedor se identificado.")


class GeminiClient:
    """
    Cliente oficial unificado da API do Google Gemini utilizando google-genai (P-309).
    Utiliza o Gemini 4 Hydrogen como modelo principal e possui resiliência com fallback
    automático para a família Gemini Flash para evitar quebras por depreciação ou indisponibilidade.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model_name = model or os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
        self._client = None
        self._init_client()

    def _init_client(self):
        if not self.api_key:
            logger.warning("GEMINI_API_KEY não informada. Cliente operando em modo offline.")
            return

        try:
            from google import genai
            self._client = genai.Client(api_key=self.api_key)

            # Descoberta dinâmica priorizando Gemini 4 Hydrogen e família Flash (sem TTS/Image)
            available_models = []
            try:
                for m in self._client.models.list():
                    name = m.name.replace("models/", "") if hasattr(m, "name") else ""
                    lower_name = name.lower()
                    is_supported_family = (
                        "hydrogen" in lower_name
                        or "flash" in lower_name
                        or name in CANDIDATE_MODELS
                    )
                    if is_supported_family and "tts" not in lower_name and "image" not in lower_name:
                        available_models.append(name)
            except Exception as list_err:
                logger.debug(f"Não foi possível listar modelos remotamente: {list_err}")

            # Prioriza sempre a ordem de CANDIDATE_MODELS (gemini-4-hydrogen em 1º lugar)
            if available_models:
                for preferred in CANDIDATE_MODELS:
                    if preferred in available_models:
                        self.model_name = preferred
                        break

            logger.info(
                f"Cliente Google GenAI inicializado com sucesso com o modelo {self.model_name} "
                f"(principal: {PRIMARY_MODEL}, fallback: família Flash)."
            )
        except Exception as e:
            logger.error(f"Erro ao inicializar google.genai: {e}")
            self._client = None

    @property
    def is_ready(self) -> bool:
        return self._client is not None

    def _format_contents(
        self,
        user_message: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> List[Any]:
        from google.genai import types

        contents = []
        if history:
            for h in history:
                role = "user" if h.get("role") == "user" else "model"
                contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=h.get("content", ""))]
                    )
                )

        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_message)]
            )
        )
        return contents

    def _execute_with_model_fallback(
        self,
        contents: List[Any],
        config_builder: Callable[[str], Any]
    ) -> Any:
        models_to_try = [self.model_name] + [m for m in CANDIDATE_MODELS if m != self.model_name]
        last_error = None

        for candidate_model in models_to_try:
            try:
                config = config_builder(candidate_model)
                response = self._client.models.generate_content(
                    model=candidate_model,
                    contents=contents,
                    config=config
                )
                if candidate_model != self.model_name:
                    logger.info(f"Migrado dinamicamente para o modelo estável {candidate_model}")
                    self.model_name = candidate_model
                return response
            except Exception as exc:
                last_error = exc
                logger.warning(f"Erro ao chamar Google GenAI ({candidate_model}): {exc}. Tentando próximo modelo...")
                continue

        logger.error(f"Todos os modelos candidatos (Gemini 4 Hydrogen e família Flash) falharam. Último erro: {last_error}")
        raise last_error

    def generate_chat_response(
        self,
        system_instruction: str,
        user_message: str,
        history: Optional[List[Dict[str, str]]] = None,
        max_output_tokens: int = 250
    ) -> str:
        """
        Executa chamada com foco em brevidade e objetividade (P-306),
        utilizando Gemini 4 Hydrogen como principal e família Flash como fallback.
        """
        if not self._client:
            raise RuntimeError("Cliente Gemini não inicializado ou sem API key.")

        from google.genai import types

        contents = self._format_contents(user_message, history)

        def build_config(candidate_model: str) -> Any:
            config_kwargs: Dict[str, Any] = {
                "system_instruction": system_instruction,
                "temperature": 0.2,
                "max_output_tokens": max_output_tokens,
            }
            thinking_cfg = _build_thinking_config(candidate_model, types)
            if thinking_cfg is not None:
                config_kwargs["thinking_config"] = thinking_cfg
            return types.GenerateContentConfig(**config_kwargs)

        response = self._execute_with_model_fallback(contents, build_config)
        return response.text or ""

    def generate_chat_decision(
        self,
        system_instruction: str,
        user_message: str,
        history: Optional[List[Dict[str, str]]] = None,
        max_output_tokens: int = 350
    ) -> GeminiChatDecision:
        """
        Gera uma decisão estruturada com Structured Output (P-309),
        utilizando Gemini 4 Hydrogen como principal e família Flash como fallback.
        A própria LLM interpreta a semântica da frase do usuário, decide se deve
        redirecionar e extrai o termo de busca contextualizado (catalog_search).
        """
        if not self._client:
            raise RuntimeError("Cliente Gemini não inicializado ou sem API key.")

        from google.genai import types

        contents = self._format_contents(user_message, history)

        def build_config(candidate_model: str) -> Any:
            config_kwargs: Dict[str, Any] = {
                "system_instruction": system_instruction,
                "temperature": 0.1,
                "max_output_tokens": max_output_tokens,
                "response_mime_type": "application/json",
                "response_schema": GeminiChatDecision,
            }
            thinking_cfg = _build_thinking_config(candidate_model, types)
            if thinking_cfg is not None:
                config_kwargs["thinking_config"] = thinking_cfg
            return types.GenerateContentConfig(**config_kwargs)

        response = self._execute_with_model_fallback(contents, build_config)
        raw_json = response.text or "{}"
        data = json.loads(raw_json)
        return GeminiChatDecision(**data)
