# Checklist de Implementação: Roteirização Comercial Inteligente

## Passo 1 a 5: Governança, Especificação e Modelagem
- [x] Especificação de regras de negócio P-100 a P-105 (`.agents/docs/business_rules/commercial_routing.md`)
- [x] Contratos de API REST (`.agents/docs/api_contracts/saved_locations.md` e `routing_ai.md`)
- [x] Modelagem segura da tabela `saved_locations` (`.agents/docs/db/saved_locations.md`)
- [x] Atualização do `STATE.md` e `ROADMAP.md`

## Passo 6 e 7: Backend Spring Boot (`fitoherb-backend-v2`)
- [x] Atualizar enum `UserRole` para incluir `SELLER`
- [x] Atualizar autorizações de `User` e `AuthorizationService` (`ROLE_SELLER`, `isSeller`, `isAdminOrSeller`)
- [x] Criar enum `SavedLocationType` (`BASE`, `FAVORITE`)
- [x] Criar entidade `SavedLocation` com auditoria JPA e relacionamentos
- [x] Criar repositório `SavedLocationRepository`
- [x] Criar DTOs `SavedLocationReq`, `SavedLocationRes` e mapper `SavedLocationMapper`
- [x] Criar serviço `SavedLocationService` com regras de base única e fallback Fitoherb
- [x] Criar controller `SavedLocationController` com Swagger e segurança
- [x] Criar cliente HTTP `FitoherbAiClient`
- [x] Desenvolver e executar suíte de testes unitários do backend (`./gradlew test`)

## Passo 6 e 7: Microserviço FastAPI (`fitoherb-ai`)
- [x] Inicializar projeto FastAPI com arquitetura DDD
- [x] Criar `app/core/config.py` e `app/main.py` com CORS e handlers
- [x] Criar domínio `routing`: modelos (`point.py`, `chromosome.py`)
- [x] Implementar operadores genéticos com trava de ordem (`routing_operators.py`)
- [x] Implementar avaliador de fitness para vendedor único (`routing_fitness.py`)
- [x] Implementar solver com hiperparâmetros fixos otimizados (`routing_solver.py`)
- [x] Implementar prioridade urgente (CRITICAL scheduled strictly first, fitness penalty + hotstart)
- [x] Implementar proxy de busca com viés de proximidade geográfica por lat/lon
- [x] Implementar infraestrutura viária OSRM com cache e fallback Haversine (`osrm_provider.py`)
- [x] Implementar gerador de PDF (`pdf_service.py`)
- [x] Implementar endpoints REST (`routing_router.py`, `health_router.py`)
- [x] Criar e executar suíte de testes unitários com pytest (`tests/test_routing_solver.py`) - 5/5 passaram

## Passo 7, 8 e 9: Frontend Angular (`fitoherb-frontend-v2`)
- [x] Integrar Leaflet, `jspdf`, `jspdf-autotable` e `html2canvas`
- [x] Atualizar tipos de usuário para suportar `SELLER` (`UserRes`, `UserReq`, `modal-entity`)
- [x] Filtrar abas no `admin-nav`: Vendedor visualiza exclusivamente 'Rotas' e 'Alterar Senha'
- [x] Criar serviço `SavedLocationsService` para consumir `/saved-locations`
- [x] Criar serviço `CommercialRoutingService` para consumir `fitoherb-ai` (com viés de proximidade e fallback direto)
- [x] Criar componente `SellerRoutesComponent` com mapa Leaflet, geocodificação reversa transparente, trava de ordem e exportação de PDF
- [x] Implementar edição de paradas do itinerário comercial (título, prioridade, ordem fixa, endereço)
- [x] Implementar barra rápida de favoritos (chips rápidos sob o searchbar e foco automático)
- [x] Ajustar overlay modal neutro escuro (`rgba(15, 23, 42, 0.65)`) sem tom esverdeado
- [x] Limpar placeholder da barra de busca removendo exemplos `(ex: ...)`
- [x] Integrar aba de Rotas no `admin.component.html`
- [x] Validar compilação (`npm run build`) - 100% sem erros

## Passo 10 a 12: Validação Integrada, Segurança e Execução
- [x] Executar testes de integração entre os 3 serviços
- [x] Verificar conformidade LGPD (ausência de PII e coordenadas em logs e PDFs)
- [x] Subir os serviços e validar o sistema funcionando (portas 8000, 8080 e 4200 ativas)
