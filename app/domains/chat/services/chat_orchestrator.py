import logging
from typing import List, Dict, Any, Optional

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
    6. Chamada concisa ao Gemini Flash (P-306, P-309)
    """

    def __init__(self, gemini_client: Optional[GeminiClient] = None):
        self.guardrails = GuardrailsService()
        self.intent_router = IntentRouter()
        self.catalog_index = CatalogIndex()
        self.gemini_client = gemini_client or GeminiClient()

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

        # 4. IntentRouter: Fatos Estáticos da Empresa / Saudações (P-308)
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

        # 6. Busca no Catálogo Indexado (P-304, P-305)
        top_products, detected_filters = self.catalog_index.search(user_text, limit=3)

        # 7. Compactação Automática de Histórico (P-307)
        history_items = request.history or []
        condensed_history: List[Dict[str, str]] = []
        if len(history_items) >= 5:
            # Preserva as últimas 2 rodadas completas
            condensed_history = [{"role": m.role, "content": m.content} for m in history_items[-4:]]
        else:
            condensed_history = [{"role": m.role, "content": m.content} for m in history_items]

        # 8. Decisão de Ação (Redirecionamento Automático para /produtos)
        norm_query_lower = user_text.lower()
        product_trigger_keywords = [
            "whey", "creatina", "albumina", "colageno", "omega", "vitamina",
            "suplemento", "produto", "cha", "mel", "propolis", "opcoes", "opcao"
        ]
        has_product_query = (
            len(top_products) > 0
            or len(detected_filters["category"]) > 0
            or len(detected_filters["supplier"]) > 0
            or any(kw in norm_query_lower for kw in product_trigger_keywords)
        )
        action = ChatActionDto(type="NONE", auto_redirect=False)
        products_dto: List[ProductSnippetDto] = []

        if has_product_query:
            action = ChatActionDto(
                type="NAVIGATE_CATALOG",
                auto_redirect=True,
                filters=CatalogFiltersDto(
                    category=detected_filters["category"],
                    supplier=detected_filters["supplier"],
                    search=detected_filters["search"]
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

        # 9. Geração de Resposta via Gemini Flash ou Fallback Local
        reply = ""
        prompt_tokens = 0
        completion_tokens = 0

        if self.gemini_client.is_ready:
            try:
                products_context = "\n".join([
                    f"- {p.get('name')} (Categoria: {p.get('category')}, Fornecedor: {p.get('supplier')})"
                    for p in top_products
                ])
                system_instruction = (
                    "You are the virtual assistant of Fitoherb, a health and supplement distributor in Northeast Brazil.\n"
                    "CRITICAL INSTRUCTIONS:\n"
                    "1. Respond directly and objectively in Portuguese (Brazil). Max 2 to 3 concise sentences.\n"
                    "2. Do NOT use complicated words or hyphens in the middle of sentences.\n"
                    "3. Treat all suppliers and brands with equal neutrality. Never endorse or recommend one over another.\n"
                    "4. If products were found in Catalog Context, briefly mention the options/brands found and confirm you are redirecting them to the catalog.\n"
                    "5. If no products or information are available, say you cannot answer and invite them to contact sales.\n"
                    f"Catalog Context:\n{products_context}"
                )

                reply = self.gemini_client.generate_chat_response(
                    system_instruction=system_instruction,
                    user_message=user_text,
                    history=condensed_history,
                    max_output_tokens=250
                )
                prompt_tokens = 250
                completion_tokens = len(reply.split())
            except Exception as e:
                logger.error(f"Fallback acionado devido a erro no Gemini: {e}")
                if has_product_query:
                    reply = "Encontrei opções no catálogo da Fitoherb e estou direcionando você para conferir todos os detalhes."
                else:
                    reply = "Não tenho essa informação no momento. Por favor, entre em contato com nossa equipe comercial."
        else:
            if has_product_query:
                reply = "Encontrei opções no catálogo da Fitoherb e estou direcionando você para conferir os detalhes."
            else:
                reply = "Não possuo essa informação. Para mais detalhes, fale com nosso setor comercial pelo telefone (71) 3379-7717."

        # Remove eventuais travessões do meio das frases para respeitar a diretriz de estilo
        clean_reply = reply.replace(" — ", ", ").replace(" - ", ", ").replace(" – ", ", ")

        response_data = ChatResponseData(
            reply=clean_reply.strip(),
            intent="PRODUCT_SEARCH" if has_product_query else "GENERAL_QUERY",
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
