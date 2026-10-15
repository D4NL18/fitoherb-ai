import os
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# Lista de modelos Flash prioritários por ordem de novidade/estabilidade
CANDIDATE_FLASH_MODELS = [
    "gemini-flash-latest",
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash"
]
DEFAULT_FLASH_MODEL = "gemini-flash-latest"


class GeminiClient:
    """
    Cliente oficial unificado da API do Google Gemini utilizando google-genai (P-309).
    Seleciona dinamicamente a versão estável mais recente do Gemini Flash e possui
    resiliência com fallback automático para evitar quebras por depreciação.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model_name = model or os.getenv("GEMINI_MODEL", DEFAULT_FLASH_MODEL)
        self._client = None
        self._init_client()

    def _init_client(self):
        if not self.api_key:
            logger.warning("GEMINI_API_KEY não informada. Cliente operando em modo offline.")
            return

        try:
            from google import genai
            self._client = genai.Client(api_key=self.api_key)

            # Descoberta dinâmica do melhor modelo Flash disponível
            available_flash = []
            try:
                for m in self._client.models.list():
                    name = m.name.replace("models/", "") if hasattr(m, "name") else ""
                    if "flash" in name.lower() and "tts" not in name.lower() and "image" not in name.lower():
                        available_flash.append(name)
            except Exception as list_err:
                logger.debug(f"Não foi possível listar modelos remotamente: {list_err}")

            # Se o modelo configurado não estiver entre os candidatos válidos, seleciona o mais recente
            if available_flash:
                for preferred in CANDIDATE_FLASH_MODELS:
                    if preferred in available_flash:
                        self.model_name = preferred
                        break
            
            logger.info(f"Cliente Google GenAI inicializado com sucesso com o modelo {self.model_name}.")
        except Exception as e:
            logger.error(f"Erro ao inicializar google.genai: {e}")
            self._client = None

    @property
    def is_ready(self) -> bool:
        return self._client is not None

    def generate_chat_response(
        self,
        system_instruction: str,
        user_message: str,
        history: Optional[List[Dict[str, str]]] = None,
        max_output_tokens: int = 250
    ) -> str:
        """
        Executa chamada com foco em brevidade e objetividade (P-306).
        Garante thinking_budget=0 para evitar consumo de tokens de CoT e possui
        fallback em cascata para candidatos mais recentes caso o modelo atual expire.
        """
        if not self._client:
            raise RuntimeError("Cliente Gemini não inicializado ou sem API key.")

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

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.2,
            max_output_tokens=max_output_tokens,
            thinking_config=types.ThinkingConfig(thinking_budget=0)
        )

        # Tenta o modelo atual e depois os modelos candidatos se houver erro 404/NOT_FOUND
        models_to_try = [self.model_name] + [m for m in CANDIDATE_FLASH_MODELS if m != self.model_name]
        last_error = None

        for candidate_model in models_to_try:
            try:
                response = self._client.models.generate_content(
                    model=candidate_model,
                    contents=contents,
                    config=config
                )
                if candidate_model != self.model_name:
                    logger.info(f"Migrado dinamicamente para o modelo estável {candidate_model}")
                    self.model_name = candidate_model
                return response.text or ""
            except Exception as exc:
                last_error = exc
                logger.warning(f"Erro ao chamar Google GenAI ({candidate_model}): {exc}. Tentando próximo modelo...")
                continue

        logger.error(f"Todos os modelos Flash falharam. Último erro: {last_error}")
        raise last_error

