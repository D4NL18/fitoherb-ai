import re
import yaml
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

COMPANY_PROFILE_PATH = Path(__file__).parent.parent / "knowledge" / "company_profile.yaml"


class IntentRouter:
    """
    Roteador de Intenções Determinístico (P-308).
    Classifica saudações e consultas institucionais e retorna respostas imediatas
    baseadas na base de conhecimento sem consumir tokens de LLM.
    """

    def __init__(self):
        self.profile: Dict[str, Any] = {}
        self._load_profile()

    def _load_profile(self):
        if COMPANY_PROFILE_PATH.exists():
            with open(COMPANY_PROFILE_PATH, "r", encoding="utf-8") as f:
                self.profile = yaml.safe_load(f) or {}

    def route_static(self, text: str) -> Optional[Tuple[str, str]]:
        """
        Retorna (reply, intent) se a pergunta puder ser respondida estaticamente,
        ou None se exigir busca no catálogo ou LLM.
        """
        lower = text.lower().strip()

        # Saudações simples
        if re.search(r"^(ol[aá]|oi|bom dia|boa tarde|boa noite|e a[ií]|opa)[\s!.]*$", lower):
            return (
                "Olá! Sou o assistente virtual da Fitoherb. Como posso ajudar você com informações sobre nossa empresa ou produtos?",
                "GREETING"
            )

        # Localização e Endereço
        if re.search(r"\b(onde\s+(fica|est[aá]|localiza)|qual\s+(o\s+)?endere[cç]o|sede|cidade|bairro|como\s+chegar)\b", lower):
            addr = self.profile.get("address", "Rua Itaeté, 434 - Pitangueiras, Lauro de Freitas - BA")
            return (
                f"Nossa sede e centro de distribuição ficam em Lauro de Freitas, na Região Metropolitana de Salvador: {addr}.",
                "COMPANY_LOCATION"
            )

        # Contato, Telefone e E-mail
        if re.search(r"\b(telefone|contato|whatsapp|e-?mail|falar\s+com|como\s+falar|n[uú]mero)\b", lower):
            tel1 = self.profile.get("phone_primary", "(71) 3379-7717")
            tel2 = self.profile.get("phone_secondary", "(71) 99241-9709")
            mail = self.profile.get("email_commercial", "comercial@fitoherb.com.br")
            return (
                f"Você pode falar com nossa equipe comercial pelos telefones {tel1} ou {tel2}, e pelo e-mail {mail}.",
                "COMPANY_CONTACT"
            )

        # Quem somos / Sobre a empresa / História
        if re.search(r"\b(quem\s+[eé]|o\s+que\s+[eé]|sobre\s+a|hist[oó]ria\s+da)\s+fitoherb\b", lower) or re.search(r"^(quem\s+s[aã]o\s+voc[eê]s|o\s+que\s+voc[eê]s\s+fazem)[\s?.]*$", lower):
            exp = self.profile.get("years_experience", "mais de 28 anos de mercado")
            seg = self.profile.get("segment", "distribuição de fitoterápicos, nutracêuticos e suplementação")
            cov = self.profile.get("coverage", "Bahia e Sergipe")
            return (
                f"A Fitoherb Nordeste Distribuidora atua há {exp} na {seg}, atendendo os estados da {cov} com foco nos canais farma, alimentar e lojas de produtos naturais.",
                "COMPANY_ABOUT"
            )

        # Estados atendidos / Cobertura geográfica
        if re.search(r"\b(onde\s+atendem|regi[aã]o|estados?|quais\s+cidades|atendem\s+em)\b", lower):
            cov = self.profile.get("coverage", "Bahia e Sergipe")
            return (
                f"Atendemos com distribuição estruturada e logística ágil os estados da {cov}.",
                "COMPANY_COVERAGE"
            )

        return None
