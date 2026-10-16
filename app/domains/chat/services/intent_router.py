import re
import yaml
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

COMPANY_PROFILE_PATH = Path(__file__).parent.parent / "knowledge" / "company_profile.yaml"

PRODUCT_BYPASS_KEYWORDS = (
    "whey",
    "creatina",
    "colageno",
    "colágeno",
    "albumina",
    "omega",
    "ômega",
    "vitamina",
    "mel",
    "propolis",
    "própolis",
    "cha",
    "chá",
    "suplemento",
    "suplementos",
    "produto",
    "produtos",
    "opcoes",
    "opções",
    "catalogo",
    "catálogo",
)


class IntentRouter:
    """
    Roteador de Intenções Determinístico (P-308, P-312).
    Classifica saudações e consultas institucionais e retorna respostas imediatas
    baseadas na base de conhecimento sem consumir tokens de LLM.
    Faz bypass para o Orquestrador quando há consulta composta envolvendo produtos.
    """

    def __init__(self):
        self.profile: Dict[str, Any] = {}
        self._load_profile()

    def _load_profile(self):
        if COMPANY_PROFILE_PATH.exists():
            with open(COMPANY_PROFILE_PATH, "r", encoding="utf-8") as f:
                self.profile = yaml.safe_load(f) or {}

    def _has_product_mention(self, lower_text: str) -> bool:
        for kw in PRODUCT_BYPASS_KEYWORDS:
            if re.search(rf"\b{re.escape(kw)}\b", lower_text):
                return True
        return False

    def route_static(self, text: str) -> Optional[Tuple[str, str]]:
        """
        Retorna (reply, intent) se a pergunta puder ser respondida estaticamente,
        ou None se exigir busca no catálogo ou LLM (ex: perguntas compostas com produtos).
        """
        lower = text.lower().strip()

        # Bypass imediato se a pergunta mencionar produtos ou catálogo (consulta composta)
        if self._has_product_mention(lower):
            return None

        # Saudações simples
        if re.search(r"^(ol[aá]|oi|bom dia|boa tarde|boa noite|e a[ií]|opa)[\s!.]*$", lower):
            return (
                "Olá! Sou o assistente virtual da Fitoherb. Como posso ajudar você com informações sobre nossa empresa ou produtos?",
                "GREETING"
            )

        # Redes Sociais / Instagram (P-308, P-312)
        if re.search(r"\b(instagram|insta|redes?\s+sociais?|arroba|perfil\s+oficial)\b|@fitoherb", lower):
            ig = self.profile.get("instagram", "@fitoherb")
            ig_url = self.profile.get("instagram_url", "https://www.instagram.com/fitoherb")
            wpp = self.profile.get("whatsapp", "(71) 99241-9709")
            wpp_url = self.profile.get("whatsapp_url", "https://wa.me/5571992419709")
            return (
                f"Nosso Instagram oficial é {ig} ({ig_url}) e nosso WhatsApp de atendimento é {wpp} ({wpp_url}).",
                "COMPANY_SOCIAL"
            )

        # Localização e Endereço
        if re.search(r"\b(onde\s+(fica|est[aá]|localiza)|qual\s+(o\s+)?endere[cç]o|sede|cidade|bairro|como\s+chegar)\b", lower):
            addr = self.profile.get("address", "Rua Itaeté, 434, Pitangueiras, Lauro de Freitas/BA")
            clean_addr = addr.replace(" — ", ", ").replace(" - ", ", ")
            return (
                f"Nossa sede e centro de distribuição ficam em Lauro de Freitas, na Região Metropolitana de Salvador: {clean_addr}.",
                "COMPANY_LOCATION"
            )

        # Contato, Telefone, WhatsApp e E-mail (P-301, P-308, P-312)
        if re.search(r"\b(telefone|contato|whatsapp|zap|wpp|e-?mail|falar\s+com|como\s+falar|n[uú]mero)\b", lower):
            tel1 = self.profile.get("phone_primary", "(71) 3379-7717")
            wpp = self.profile.get("whatsapp", self.profile.get("phone_secondary", "(71) 99241-9709"))
            wpp_url = self.profile.get("whatsapp_url", "https://wa.me/5571992419709")
            mail = self.profile.get("email_commercial", "comercial@fitoherb.com.br")
            ig = self.profile.get("instagram", "@fitoherb")
            ig_url = self.profile.get("instagram_url", "https://www.instagram.com/fitoherb")
            return (
                f"Você pode falar com nossa equipe comercial pelo telefone {tel1}, pelo WhatsApp {wpp} ({wpp_url}), pelo e-mail {mail} ou pelo Instagram {ig} ({ig_url}).",
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
