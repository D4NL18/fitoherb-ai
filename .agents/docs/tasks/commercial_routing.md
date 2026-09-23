# Checklist de Implementação: Roteirização Comercial Inteligente

## Passo 1 a 5: Governança, Especificação e Modelagem
- [x] Especificação de regras de negócio P-100 a P-105 (`.agents/docs/business_rules/commercial_routing.md`)
- [x] Contratos de API REST (`.agents/docs/api_contracts/saved_locations.md` e `routing_ai.md`)
- [x] Modelagem segura da tabela `saved_locations` (`.agents/docs/db/saved_locations.md`)
- [x] Atualização do `STATE.md` e `ROADMAP.md`

## Passo 6 e 7: Backend Spring Boot (`fitoherb-backend-v2`)
- [ ] Atualizar enum `UserRole` para incluir `SELLER`
- [ ] Atualizar autorizações de `User` e `AuthorizationService` (`ROLE_SELLER`, `isSeller`, `isAdminOrSeller`)
- [ ] Criar enum `SavedLocationType` (`BASE`, `FAVORITE`)
- [ ] Criar entidade `SavedLocation` com auditoria JPA e relacionamentos
- [ ] Criar repositório `SavedLocationRepository`
- [ ] Criar DTOs `SavedLocationReq`, `SavedLocationRes` e mapper `SavedLocationMapper`
- [ ] Criar serviço `SavedLocationService` com regras de base única e fallback Fitoherb
- [ ] Criar controller `SavedLocationController` com Swagger e segurança
- [ ] Criar cliente HTTP `FitoherbAiClient`
- [ ] Desenvolver e executar suíte de testes unitários do backend (`./gradlew test`)

## Passo 6 e 7: Microserviço FastAPI (`fitoherb-ai`)
- [ ] Inicializar projeto FastAPI com arquitetura DDD
- [ ] Criar `app/core/config.py` e `app/main.py` com CORS e handlers
- [ ] Criar domínio `routing`: modelos (`point.py`, `chromosome.py`)
- [ ] Implementar operadores genéticos com trava de ordem (`routing_operators.py`)
- [ ] Implementar avaliador de fitness para vendedor único (`routing_fitness.py`)
- [ ] Implementar solver com hiperparâmetros fixos otimizados (`routing_solver.py`)
- [ ] Implementar infraestrutura viária OSRM com cache e fallback Haversine (`osrm_provider.py`)
- [ ] Implementar gerador de PDF (`pdf_service.py`)
- [ ] Implementar endpoints REST (`routing_router.py`, `health_router.py`)
- [ ] Criar e executar suíte de testes unitários com pytest (`tests/test_routing_solver.py`)

## Passo 7, 8 e 9: Frontend Angular (`fitoherb-frontend-v2`)
- [ ] Integrar Leaflet, `jspdf`, `jspdf-autotable` e `html2canvas`
- [ ] Atualizar tipos de usuário para suportar `SELLER` (`UserRes`, `UserReq`, `modal-entity`)
- [ ] Filtrar abas no `admin-nav`: Vendedor visualiza exclusivamente 'Rotas' e 'Alterar Senha'
- [ ] Criar serviço `SavedLocationsService` para consumir `/saved-locations`
- [ ] Criar serviço `CommercialRoutingService` para consumir `fitoherb-ai`
- [ ] Criar componente `SellerRoutesComponent` com mapa Leaflet, geocodificação reversa transparente, trava de ordem e exportação de PDF
- [ ] Integrar aba de Rotas no `admin.component.html`
- [ ] Validar compilação (`npm run build`)

## Passo 10 a 12: Validação Integrada, Segurança e Execução
- [ ] Executar testes de integração entre os 3 serviços
- [ ] Verificar conformidade LGPD (ausência de PII e coordenadas em logs e PDFs)
- [ ] Subir os serviços e validar o sistema funcionando
