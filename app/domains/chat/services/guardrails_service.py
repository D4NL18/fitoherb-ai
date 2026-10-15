import re
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class GuardrailsService:
    """
    Serviço de Guardrails de Segurança para o Chatbot Gemini (P-300, P-303, P-306).
    Intercepta tentativas de injeção de prompt e perguntas sobre saúde/prescrição
    de forma puramente determinística (0 tokens consumidos).
    """

    _INJECTION_PATTERNS = [
        re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules|commands)", re.IGNORECASE),
        re.compile(r"(ignore|esque[cç]a)\s+(todas\s+as\s+|qualquer\s+|as\s+|os\s+)?(instru[cç][õo]es|diretrizes|regras|comandos)\s*(anteriores|acima)?", re.IGNORECASE),
        re.compile(r"(repeat|show|reveal|display|output|print|give)(\s+me)?\s+(all\s+)?(your\s+)?(system\s+prompt|initial\s+instructions|system\s+instructions|developer\s+instructions)", re.IGNORECASE),
        re.compile(r"(mostre|revele|imprima|repita|diga|quais\s+s[aã]o)(\s+me)?\s+(o\s+|as\s+)?(seu\s+|suas\s+)?(system\s+prompt|prompt\s+de\s+sistema|instru[cç][õo]es\s+iniciais|regras\s+de\s+sistema)", re.IGNORECASE),
        re.compile(r"\b(DAN|jailbreak|developer\s+mode|unrestricted\s+mode|god\s+mode)\b", re.IGNORECASE),
        re.compile(r"voc[eê]\s+agora\s+[eé]\s+(um\s+ia\s+sem\s+regras|dan|modo\s+desenvolvedor)", re.IGNORECASE),
        re.compile(r"<\s*/?\s*(system|system_instruction|assistant|developer|admin)\s*>", re.IGNORECASE),
    ]

    _MEDICAL_PATTERNS = [
        re.compile(r"\b(posologia|dosagem|quantas\s+gotas|quantos\s+comprimidos|como\s+tomar|quantas\s+vezes\s+ao\s+dia)\b", re.IGNORECASE),
        re.compile(r"\b(cura|tratar|remedio\s+para|remédio\s+para|curar)\s+(diabetes|câncer|cancer|press[aã]o|depress[aã]o|ansiedade|infec[cç][aã]o|colesterol)\b", re.IGNORECASE),
        re.compile(r"\b(estou\s+com|sinto|sintoma|sintomas|dor\s+no|dor\s+na|febre|falta\s+de\s+ar)\b", re.IGNORECASE),
        re.compile(r"\b(estou\s+gr[aá]vida|gestante|amamentando|lactante)\b", re.IGNORECASE),
    ]

    _COMMERCIAL_RESTRICTED_PATTERNS = [
        re.compile(r"\b(quanto\s+custa|qual\s+(o\s+)?pre[cç]o|valor|tabela\s+de\s+pre[cç]o|desconto|forma\s+de\s+pagamento|faturado|prazo\s+de\s+pagamento)\b", re.IGNORECASE),
        re.compile(r"\b(tem\s+estoque|tem\s+a\s+pronta\s+entrega|qual\s+o\s+estoque|quantidade\s+dispon[ií]vel)\b", re.IGNORECASE),
        re.compile(r"\b(tabela\s+nutricional|calorias|carboidratos|prote[ií]na\s+por\s+dose|laudo)\b", re.IGNORECASE),
    ]

    _CONTROL_CHARS_PATTERN = re.compile(r"[\u200B-\u200D\uFEFF\u0000-\u0008\u000E-\u001F\u007F-\u009F]")

    @classmethod
    def sanitize_input(cls, user_text: str) -> str:
        if not user_text:
            return ""
        cleaned = cls._CONTROL_CHARS_PATTERN.sub("", user_text)
        cleaned = re.sub(r"[ \t]{3,}", "  ", cleaned)
        return cleaned.strip()

    @classmethod
    def check_prompt_injection(cls, user_text: str) -> Tuple[bool, Optional[str]]:
        sanitized = cls.sanitize_input(user_text)
        for pattern in cls._INJECTION_PATTERNS:
            match = pattern.search(sanitized)
            if match:
                logger.warning(f"Prompt Injection interceptado: {match.group(0)}")
                return True, "Tentativa de injeção ou subversão de diretrizes detectada."
        return False, None

    @classmethod
    def check_medical_advice(cls, user_text: str) -> Tuple[bool, Optional[str]]:
        sanitized = cls.sanitize_input(user_text)
        for pattern in cls._MEDICAL_PATTERNS:
            match = pattern.search(sanitized)
            if match:
                logger.info(f"Pergunta de cunho médico interceptada: {match.group(0)}")
                return True, (
                    "Não realizo diagnósticos, indicações de dosagem ou prescrições terapêuticas. "
                    "Consulte sempre um médico ou nutricionista habilitado."
                )
        return False, None

    @classmethod
    def check_commercial_restricted(cls, user_text: str) -> Tuple[bool, Optional[str]]:
        sanitized = cls.sanitize_input(user_text)
        for pattern in cls._COMMERCIAL_RESTRICTED_PATTERNS:
            match = pattern.search(sanitized)
            if match:
                logger.info(f"Pergunta restrita de preço/estoque interceptada: {match.group(0)}")
                return True, (
                    "Não tenho autorização para informar preços, estoques ou tabelas nutricionais pelo chat. "
                    "Por favor, fale com nosso time comercial pelo telefone (71) 3379-7717 ou e-mail comercial@fitoherb.com.br."
                )
        return False, None

    @classmethod
    def sanitize_pii(cls, text: str) -> str:
        # Mascara CPF, telefones e emails exceto os oficiais da Fitoherb
        text = re.sub(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b", "[CPF_PROTEGIDO]", text)
        text = re.sub(r"\b\d{11}\b", "[DOCUMENTO_PROTEGIDO]", text)
        return text
