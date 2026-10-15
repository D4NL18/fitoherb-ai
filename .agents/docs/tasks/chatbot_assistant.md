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
- [ ] Criar estrutura do domínio `app/domains/chat/`
- [ ] Criar base de conhecimento estática institucional `company_profile.yaml`
- [ ] Criar DTOs Pydantic v2 `ChatRequest`, `ChatResponse`, `ActionDto` com limite de 255 chars
- [ ] Implementar `GuardrailsService` com detecção de injeção e curto-circuito de saúde (P-303)
- [ ] Implementar `IntentRouter` para respostas estáticas instantâneas com 0 tokens (P-308)
- [ ] Implementar `CatalogIndex` em memória com busca textual e resolução de sinônimos/facetas
- [ ] Implementar `GeminiClient` dinâmico (`google-genai`) apontando para a versão estável do Gemini Flash
- [ ] Implementar `ConversationCacheService` em memória L1 com chave SHA-256 e TTL
- [ ] Implementar compactação automática de histórico a partir de 5 mensagens (P-307)
- [ ] Implementar endpoint `POST /api/v1/chat/messages` e `GET /api/v1/chat/health`
- [ ] Criar e executar suíte de testes unitários TDD (`tests/test_chat_assistant.py`)

---

## Passo 6 e 7: Backend Spring Boot (`fitoherb-backend-v2`)
- [ ] Criar DTO `CatalogIndexItemRes` contendo projeção enxuta para indexação
- [ ] Criar método no `ProductService` e `ProductRepository` com busca paginada/completa para o catálogo indexado
- [ ] Expor endpoint seguro com ETag: `GET /products/catalog-index`
- [ ] Criar e executar suíte de testes unitários com JUnit 5 (`ProductControllerTest`)

---

## Passo 6 e 7: Frontend Angular (`fitoherb-frontend-v2`)
- [ ] Criar interfaces de tipos `src/app/types/chat/chat.interface.ts`
- [ ] Criar serviço `ChatService` com gerenciamento de estado via Signals e `sessionStorage`
- [ ] Criar componente `ChatFabComponent` (botão flutuante no canto inferior direito)
- [ ] Criar componente `ChatPanelComponent` com janela conversacional e 8 estados visuais
- [ ] Implementar lógica de auto-redirecionamento para a tela `/produtos` aplicando query params
- [ ] Ajustar `GalleryComponent` para ler o parâmetro `search` diretamente da URL
- [ ] Ancorar o chat flutuante no `AppComponent` sob a guarda do `@if (showLayout())`
- [ ] Criar e executar testes unitários com Jasmine (`chat.service.spec.ts`)

---

## Passo 8 a 12: Auditorias, Testes Integrados e Release
- [ ] Code Review de Clean Code e Auditoria de Código LGPD
- [ ] UX Review e Vibe Check da fidelidade visual e ausência de slop
- [ ] Teste integrado ao vivo com os 3 serviços em execução
- [ ] Auditoria de Segurança SAST e Red Teaming de Prompt Injection
- [ ] Abertura dos Pull Requests para a branch `develop`
