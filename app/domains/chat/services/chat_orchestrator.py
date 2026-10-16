import logging
from typing import List, Dict, Any, Optional, Tuple

from app.domains.chat.schemas.chat_dto import (
    ChatRequest,
    ChatResponse,
    ChatResponseData,
    ChatActionDto,
    CatalogFiltersDto,
    ProductSnippetDto,
    ChatMessageItem
)
from app.domains.chat.services.guardrails_service import GuardrailsService
from app.domains.chat.services.intent_router import IntentRouter
from app.domains.chat.services.cache_service import ConversationCacheService
from app.domains.chat.infrastructure.catalog_index import CatalogIndex
from app.domains.chat.infrastructure.gemini_client import GeminiClient

logger = logging.getLogger(__name__)


class ChatOrchestrator:
    """
    Orquestrador Central do Chatbot Gemini (Passo 7).
    Executa a esteira completa:
    1. Guardrails (Injeção de prompt, Saúde, Preços restritos)
    2. IntentRouter estático (0 tokens)
    3. Cache L1
    4. Compactação de Histórico (P-307)
    5. Busca no Catálogo Indexado (P-304, P-305)
    6. Chamada concisa ao Gemini Flash (P-306, P-309, P-312)
    """

    def __init__(self, gemini_client: Optional[GeminiClient] = None):
        self.guardrails = GuardrailsService()
        self.intent_router = IntentRouter()
        self.catalog_index = CatalogIndex()
        self.gemini_client = gemini_client or GeminiClient()

    def _resolve_contextual_query(self, user_text: str, history: List[ChatMessageItem]) -> str:
        norm_msg = user_text.lower().strip()
        product_topics = ["whey 100%", "whey", "creatina", "colageno", "colágeno", "albumina", "omega 3", "ômega 3", "omega", "vitamina", "mel", "propolis", "cha"]

        # Se a mensagem atual já possui um tópico de produto explícito, mantém
        if any(pt in norm_msg for pt in ["whey", "creatina", "colageno", "colágeno", "albumina", "omega", "ômega", "vitamina", "mel", "propolis", "cha"]):
            return user_text

        # Palavras indicativas de sabor, apresentação ou acompanhamento
        attribute_keywords = [
            "morango", "chocolate", "baunilha", "cookies", "limao", "limão",
            "maracuja", "maracujá", "banana", "coco", "doce de leite", "neutro",
            "sem sabor", "refil", "pote", "saco", "isolado", "concentrado", "hidrolisado",
            "tem de", "tem sabor", "qual o sabor", "quais os sabores", "sabor", "sabores"
        ]
        is_contextual = any(ak in norm_msg for ak in attribute_keywords) or len(norm_msg.split()) <= 4

        if is_contextual and history:
            for item in reversed(history):
                if item.role == "user":
                    prev_text = item.content.lower()
                    for pt in product_topics:
                        if pt in prev_text:
                            from app.domains.chat.infrastructure.catalog_index import extract_clean_search
                            clean_curr = extract_clean_search(user_text)
                            return f"{pt} {clean_curr}".strip()

        return user_text

    def _execute_catalog_fallback(
        self,
        user_text: str,
        history: List[ChatMessageItem]
    ) -> Tuple[str, ChatActionDto, List[ProductSnippetDto], str]:
        effective_query = self._resolve_contextual_query(user_text, history)
        top_products, detected_filters = self.catalog_index.search(effective_query, limit=5)
        search_query = detected_filters["search"] or effective_query
        has_product_query = len(top_products) > 0 or any(
            kw in user_text.lower() for kw in ["whey", "creatina", "produto", "opcoes"]
        )

        products_dto: List[ProductSnippetDto] = []
        if has_product_query:
            intent = "PRODUCT_SEARCH"
            reply = "Temos opções disponíveis em nosso catálogo e estou direcionando você para conferir todos os detalhes."
            action = ChatActionDto(
                type="NAVIGATE_CATALOG",
                auto_redirect=True,
                filters=CatalogFiltersDto(
                    category=detected_filters["category"],
                    supplier=detected_filters["supplier"],
                    search=search_query
                )
            )
            for p in top_products:
                products_dto.append(
                    ProductSnippetDto(
                        name=p.get("name", ""),
                        slug=p.get("slug", ""),
                        image_url=p.get("image_url", ""),
                        category=p.get("category", ""),
                        supplier=p.get("supplier", "")
                    )
                )
        else:
            intent = "GENERAL_QUERY"
            reply = (
                "Não tenho essa informação no momento. Por favor, entre em contato com nossa equipe comercial "
                "pelo telefone (71) 3379-7717, pelo WhatsApp (71) 99241-9709 (https://wa.me/5571992419709) "
                "ou pelo Instagram @fitoherb (https://www.instagram.com/fitoherb)."
            )
            action = ChatActionDto(type="NONE", auto_redirect=False)

        return reply, action, products_dto, intent

    def process_message(self, request: ChatRequest) -> ChatResponse:
        user_text = request.message.strip()

        # 1. Guardrail: Injeção de Prompt
        is_inj, inj_msg = self.guardrails.check_prompt_injection(user_text)
        if is_inj:
            return ChatResponse(
                data=ChatResponseData(
                    reply="Não posso processar essa instrução. Posso ajudar com informações sobre a Fitoherb ou nosso catálogo.",
                    intent="INJECTION_BLOCKED"
                ),
                meta={"guardrail": "INJECTION_BLOCKED", "tokens": {"prompt_tokens": 0, "completion_tokens": 0}}
            )

        # 2. Guardrail: Aconselhamento Médico (P-303)
        is_med, med_msg = self.guardrails.check_medical_advice(user_text)
        if is_med:
            return ChatResponse(
                data=ChatResponseData(
                    reply=med_msg or "Consulte um profissional de saúde qualificado.",
                    intent="MEDICAL_RESTRICTED"
                ),
                meta={"guardrail": "MEDICAL_RESTRICTED", "tokens": {"prompt_tokens": 0, "completion_tokens": 0}}
            )

        # 3. Guardrail: Informações Comerciais Restritas (P-302)
        is_comm, comm_msg = self.guardrails.check_commercial_restricted(user_text)
        if is_comm:
            return ChatResponse(
                data=ChatResponseData(
                    reply=comm_msg or "Consulte nosso time comercial.",
                    intent="COMMERCIAL_RESTRICTED"
                ),
                meta={"guardrail": "COMMERCIAL_RESTRICTED", "tokens": {"prompt_tokens": 0, "completion_tokens": 0}}
            )

        # 4. IntentRouter: Fatos Estáticos da Empresa / Saudações (P-308, P-312)
        static_route = self.intent_router.route_static(user_text)
        if static_route:
            reply_text, intent_name = static_route
            return ChatResponse(
                data=ChatResponseData(
                    reply=reply_text,
                    intent=intent_name,
                    suggestions=["Onde fica a Fitoherb?", "Quais as opções de Whey?", "Como falar com o comercial?"]
                ),
                meta={"cache": "STATIC_KB", "tokens": {"prompt_tokens": 0, "completion_tokens": 0}}
            )

        # 5. Cache L1 (P-310)
        cached = ConversationCacheService.get(user_text)
        if cached:
            return ChatResponse(
                data=ChatResponseData(**cached),
                meta={"cache": "HIT", "tokens": {"prompt_tokens": 0, "completion_tokens": 0}}
            )

        # 6. Compactação Automática de Histórico (P-307)
        history_items = request.history or []
        condensed_history: List[Dict[str, str]] = []
        if len(history_items) >= 5:
            # Preserva as últimas 2 rodadas completas
            condensed_history = [{"role": m.role, "content": m.content} for m in history_items[-4:]]
        else:
            condensed_history = [{"role": m.role, "content": m.content} for m in history_items]

        # 7. Interpretação Semântica e Decisão de Roteamento via Gemini Structured Output (P-309, P-312)
        action = ChatActionDto(type="NONE", auto_redirect=False)
        products_dto: List[ProductSnippetDto] = []
        reply = ""
        prompt_tokens = 0
        completion_tokens = 0
        intent = "GENERAL_QUERY"

        if self.gemini_client.is_ready:
            try:
                system_instruction = (
                    "Você é o assistente virtual oficial da Fitoherb, distribuidora de suplementos e produtos naturais no Nordeste.\n"
                    "Seu objetivo é orientar clientes e ajudá-los a encontrar produtos no catálogo com máxima naturalidade.\n\n"
                    "CANAIS OFICIAIS E REDES SOCIAIS DA FITOHERB (P-301, P-312):\n"
                    "Telefone fixo comercial: (71) 3379-7717\n"
                    "WhatsApp oficial: (71) 99241-9709 (link direto: https://wa.me/5571992419709)\n"
                    "Instagram oficial: @fitoherb (link direto: https://www.instagram.com/fitoherb)\n"
                    "E-mail comercial: comercial@fitoherb.com.br\n"
                    "Endereço: Rua Itaeté, 434, Pitangueiras, Lauro de Freitas/BA, CEP: 42701-360\n\n"
                    "DIRETRIZES OBRIGATÓRIAS:\n"
                    "1. Responda em português (Brasil) em no máximo 2 a 3 frases curtas e diretas.\n"
                    "2. NUNCA use palavras difíceis e NUNCA use travessões (-) ou meias-riscas (—) no meio das frases.\n"
                    "3. Trate todas as marcas parceiras com absoluta neutralidade e igualdade.\n"
                    "   Marcas parceiras oficiais: Integralmedica, Black Skull, Max Titanium, Probiotica, FTW, Flora Nativa, Mandiervas, Katigua, Apisnutri, Chamel, Vital Atman, Unilife.\n"
                    "4. INTERPRETAÇÃO DO FILTRO (catalog_search):\n"
                    "   * O que o usuário digita é livre e não é fixo. Interprete o que ele realmente quer buscar.\n"
                    "   * Se a intenção for buscar produtos, defina 'should_redirect': true e preencha 'catalog_search' com o termo limpo e semântico para filtrar o catálogo (ex: 'whey 100%', 'creatina', 'colageno', 'mel propolis').\n"
                    "   * Se for uma pergunta de acompanhamento ou continuidade (ex: usuário estava falando de whey 100% e agora pergunta 'tem de morango?' ou 'e de chocolate?'), junte o contexto anterior em 'catalog_search' (ex: 'whey 100% morango').\n"
                    "   * Se NÃO for sobre produtos (ex: localização, contato, redes sociais, institucional), defina 'should_redirect': false e 'catalog_search': ''.\n"
                    "5. Se perguntarem sobre WhatsApp, Instagram ou redes sociais (inclusive em perguntas compostas com produtos), informe sempre @fitoherb (https://www.instagram.com/fitoherb) e WhatsApp (71) 99241-9709 (https://wa.me/5571992419709).\n"
                    "6. Se perguntarem algo fora do escopo (preço, tabela nutricional completa), informe que não possui essa informação e convide a contatar a equipe comercial pelos canais oficiais."
                )

                decision = self.gemini_client.generate_chat_decision(
                    system_instruction=system_instruction,
                    user_message=user_text,
                    history=condensed_history,
                    max_output_tokens=350
                )
                reply = decision.reply
                prompt_tokens = 250
                completion_tokens = len(reply.split())

                if decision.should_redirect and decision.catalog_search:
                    search_query = decision.catalog_search.strip()
                    intent = "PRODUCT_SEARCH"
                    top_products, _ = self.catalog_index.search(search_query, limit=5)
                    for p in top_products:
                        products_dto.append(
                            ProductSnippetDto(
                                name=p.get("name", ""),
                                slug=p.get("slug", ""),
                                image_url=p.get("image_url", ""),
                                category=p.get("category", ""),
                                supplier=p.get("supplier", "")
                            )
                        )

                    action = ChatActionDto(
                        type="NAVIGATE_CATALOG",
                        auto_redirect=True,
                        filters=CatalogFiltersDto(
                            category=[decision.category_slug] if decision.category_slug else [],
                            supplier=[decision.supplier_slug] if decision.supplier_slug else [],
                            search=search_query
                        )
                    )
            except Exception as e:
                logger.error(f"Erro ao processar Structured Output no Gemini: {e}. Acionando fallback...")
                reply, action, products_dto, intent = self._execute_catalog_fallback(user_text, request.history or [])
        else:
            reply, action, products_dto, intent = self._execute_catalog_fallback(user_text, request.history or [])

        # Remove eventuais travessões do meio das frases para respeitar a diretriz de estilo (P-306)
        clean_reply = reply.replace(" — ", ", ").replace(" - ", ", ").replace(" – ", ", ")

        response_data = ChatResponseData(
            reply=clean_reply.strip(),
            intent=intent,
            action=action,
            products=products_dto,
            suggestions=["O que é a Fitoherb?", "Onde fica a distribuidora?", "Falar com o comercial"]
        )

        # Salva no cache L1
        ConversationCacheService.set(user_text, response_data.model_dump())

        return ChatResponse(
            data=response_data,
            meta={
                "cache": "MISS",
                "model": getattr(self.gemini_client, "model_name", "local-fallback"),
                "tokens": {"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens}
            }
        )
