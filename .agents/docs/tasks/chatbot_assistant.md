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
