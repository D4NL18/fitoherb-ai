import os
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# Versão estável padrão do Gemini Flash (mais recente e econômica)
DEFAULT_FLASH_MODEL = "gemini-2.5-flash"


class GeminiClient:
    """
    Cliente oficial unificado da API do Google Gemini utilizando google-genai (P-309).
    Configura chave de API de forma segura e seleciona a versão estável do Gemini Flash.
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
        """
        if not self._client:
            raise RuntimeError("Cliente Gemini não inicializado ou sem API key.")

        try:
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
                temperature=0.1,
                max_output_tokens=max_output_tokens,
            )

            response = self._client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config
            )

            return response.text or ""

        except Exception as exc:
            logger.error(f"Erro ao chamar Google GenAI ({self.model_name}): {exc}")
            raise exc
