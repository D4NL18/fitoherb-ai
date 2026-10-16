# Checklist de Implementação: Assistente Virtual Inteligente (Chatbot Gemini)

## Passo 1 a 5: Governança, Especificação e Modelagem
- [x] Quebra de escopo em User Stories no `ROADMAP.md` (Product Owner)
- [x] Especificação das regras de negócio P-300 a P-311 (`.agents/docs/business_rules/chatbot_assistant.md`)
- [x] Contrato de API REST do Chatbot (`.agents/docs/api_contracts/chatbot_assistant.md`)
- [x] Design Plan da Interface com 8 estados (`.agents/docs/design/plans/chatbot_assistant.md`)
- [x] Parecer de Privacy by Design e LGPD (`.agents/docs/privacy/chatbot_assistant_privacy_review.md`)
- [x] Modelagem segura e impacto zero de migration de banco (`.agents/docs/db/product.md` atualizado)

---

## Passo 6 e 7: Microserviço FastAPI (`fitoherb-ai`)
- [x] Criar estrutura do domínio `app/domains/chat/`
- [x] Criar base de conhecimento estática institucional `company_profile.yaml`
- [x] Criar DTOs Pydantic v2 `ChatRequest`, `ChatResponse`, `ActionDto` com limite de 255 chars
- [x] Implementar `GuardrailsService` com detecção de injeção e curto-circuito de saúde (P-303)
- [x] Implementar `IntentRouter` para respostas estáticas instantâneas com 0 tokens (P-308)
- [x] Implementar `CatalogIndex` em memória com busca textual e resolução de sinônimos/facetas
- [x] Implementar `GeminiClient` dinâmico (`google-genai`) apontando para a versão estável do Gemini Flash
- [x] Implementar `ConversationCacheService` em memória L1 com chave SHA-256 e TTL
- [x] Implementar compactação automática de histórico a partir de 5 mensagens (P-307)
- [x] Implementar endpoint `POST /api/v1/chat/messages` e `GET /api/v1/chat/health`
- [x] Criar e executar suíte de testes unitários TDD (`tests/test_chat_assistant.py`) - 7/7 aprovados

---

## Passo 6 e 7: Backend Spring Boot (`fitoherb-backend-v2`)
- [x] Catálogo já atende com endpoint otimizado `/products/gallery` paginado e filtros
- [x] Suíte de testes unitários do backend validada sem quebras (`./gradlew test` - 100% verde)

---

## Passo 6 e 7: Frontend Angular (`fitoherb-frontend-v2`)
- [x] Criar interfaces de tipos `src/app/types/chat/chat.interface.ts`
- [x] Criar serviço `ChatService` com gerenciamento de estado via Signals e `sessionStorage`
- [x] Criar componente `ChatWidgetComponent` (botão flutuante no canto inferior direito)
- [x] Implementar lógica de auto-redirecionamento para a tela `/produtos` aplicando query params
- [x] Ajustar `GalleryComponent` para ler o parâmetro `search` diretamente da URL
- [x] Ancorar o chat flutuante no `AppComponent` sob a guarda do `@if (showLayout())`
- [x] Validar compilação de produção (`ng build --configuration production` - 100% verde)

---

## Passo 8 a 12: Auditorias, Testes Integrados e Release
- [x] Code Review de Clean Code e Auditoria de Código LGPD (zero PII, 255 chars, curto-circuito de saúde)
- [x] UX Review e Vibe Check (8 estados, cores florestais, Playfair/Outfit, sem slop)
- [x] Testes unitários do AI service passando 100% (29/29)
- [x] Subida das branches `feat/chatbot-gemini-assistant` para o GitHub nos repositórios
- [x] Geração dos links canônicos de Pull Request apontando para `develop`

---

## Evolução: Treinamento de Redes Sociais - WhatsApp e Instagram (`P-301`, `P-308`, `P-312`)

**Descritivo Detalhado:**
Capacitar o Assistente Virtual Fitoherb a informar com precisão os canais digitais e redes sociais oficiais da empresa — WhatsApp `(71) 99241-9709` (`https://wa.me/5571992419709`) e Instagram `@fitoherb` (`https://www.instagram.com/fitoherb`) — tanto em consultas diretas resolvidas com 0 tokens via `IntentRouter` quanto em consultas compostas enviadas ao Gemini via `ChatOrchestrator` e `company_profile.yaml`.

### Checklist Técnico Atômico por Especialidade (Etapas 2 e 3)

#### 1. Governança e Contratos (`architect` + `ai_specialist` + `privacy_officer`)
- [x] Atualizar `.agents/docs/api_contracts/chatbot_assistant.md` documentando as intenções `COMPANY_SOCIAL` e `COMPANY_CONTACT` no envelope `data`/`meta` com 100% de retrocompatibilidade.
- [x] Definir estratégia de prompt e roteamento semântico 0 tokens (`ai_specialist`).
- [x] Validar conformidade Privacy by Design / LGPD sobre exposição estrita de canais corporativos públicos (`privacy_officer`).

#### 2. Suíte de Testes TDD-First (`tester` — `tests/test_chat_assistant.py`)
- [x] Criar teste unitário para consulta direta de Instagram/redes sociais no `IntentRouter` (`"Qual o Instagram da Fitoherb?"`, `"Quais as redes sociais?"`), validando retorno de `@fitoherb`, `https://www.instagram.com/fitoherb`, `(71) 99241-9709` e intent `COMPANY_SOCIAL` ou `COMPANY_CONTACT`.
- [x] Criar teste unitário para consulta direta de WhatsApp no `IntentRouter` (`"Qual o WhatsApp da Fitoherb?"`, `"Tem zap de atendimento?"`), validando retorno de `(71) 99241-9709`, link `https://wa.me/5571992419709` e consumo de `0 tokens` (`meta.cache == "STATIC_KB"`).
- [x] Criar teste unitário no `ChatOrchestrator` validando que a `system_instruction` enviada ao Gemini e o fallback institucional incluem o WhatsApp `(71) 99241-9709` e o Instagram `@fitoherb`, sem travessões no meio de frases (`P-306`, `P-312`).

#### 3. Implementação e Base de Conhecimento (`developer` + `ai_specialist`)
- [x] Atualizar `app/domains/chat/knowledge/company_profile.yaml` adicionando campos estruturados `whatsapp`, `whatsapp_url`, `instagram` (`@fitoherb`), `instagram_url` (`https://www.instagram.com/fitoherb`) e atualizando `restricted_info_message`.
- [x] Atualizar `app/domains/chat/services/intent_router.py` para reconhecer termos de redes sociais (`instagram`, `insta`, `rede social`, `redes sociais`, `arroba`, `perfil oficial`) retornando `COMPANY_SOCIAL`, e enriquecer a rota `COMPANY_CONTACT` (`whatsapp`, `zap`, `wpp`, `telefone`, `contato`, `email`) com os números `(71) 3379-7717`, WhatsApp `(71) 99241-9709` (`https://wa.me/5571992419709`) e Instagram `@fitoherb` (`0 tokens`, sem travessões no meio das frases).
- [x] Atualizar `app/domains/chat/services/chat_orchestrator.py` injetando os canais oficiais (WhatsApp `(71) 99241-9709` / `https://wa.me/5571992419709`, Instagram `@fitoherb` / `https://www.instagram.com/fitoherb`, telefone `(71) 3379-7717` e e-mail `comercial@fitoherb.com.br`) na `system_instruction` do Gemini e na mensagem de fallback geral (`_execute_catalog_fallback`).
- [x] Executar `pytest` garantindo 100% de aprovação na suíte completa do `fitoherb-ai` (32/32 aprovados).
