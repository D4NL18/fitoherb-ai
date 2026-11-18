# Entidade / Feature: Inteligência Demográfica por Cidade e Descoberta Proativa de Leads com Manejo em Lote (`commercial_routing_city_and_suggestions`)

Este documento centraliza todo o planejamento, as especificações e as etapas de execução para as tarefas relacionadas ao Relatório de Cidades (`P-107`), Sugestão de Farmácias e Lojas de Produtos Naturais (`P-108`) e Manejo em Lote com Recálculo Diferido (`P-109`).

## 1. Dúvidas Resolvidas (Especificação)
- **Dúvida:** Quais informações das cidades visitadas na rota são mais úteis para o vendedor no relatório previsto em `P-107`?
  - **Decisão:** O relatório por cidade deve exibir: População Estimada (IBGE), Porte do Município (Metrópole, Polo Regional, Cidade Média, Pequeno Porte), Densidade Demográfica (`hab/km²`), PIB per capita / Potencial Econômico, Polo/Região Geográfica, Foco Comercial Recomendado Fitoherb, Total de Paradas Confirmadas na Cidade, Total de Novas Sugestões Descobertas na Cidade e Tempo Total Estimado de Atendimento no Município.
- **Dúvida:** Como o sistema descobre novas farmácias e lojas de produtos naturais que não estão nos pontos listados (`P-108`)?
  - **Decisão:** Durante a previsão da rota, o `fitoherb-ai` busca POIs dos segmentos de Farmácias/Drogarias/Manipulação e Lojas de Produtos Naturais/Suplementos/Fitoterápicos no corredor das paradas/cidades da rota (via Overpass API / Photon OSM + cache SQLite + catálogo de contingência), filtrando qualquer ponto com distância <= 80m ou similaridade de nome >= 0.82 em relação aos pontos já listados ou salvos pelo vendedor.
- **Dúvida:** Como deve funcionar a adição de sugestões e a remoção na lista sem recalcular a cada clique (`P-109`)?
  - **Decisão:** As sugestões descobertas entram na lista da rota com badge `SUGESTÃO` (podendo ser mantidas ou removidas pelo vendedor). Qualquer remoção ou ajuste na lista ativa o estado de **Manejo da Lista (Staging)** sem chamar o backend a cada clique. O recálculo da rota ocorre **apenas uma única vez** quando o vendedor clica em **"Concluir Manejo e Recalcular Rota"**.

---

## 2. Tarefas e Etapas de Desenvolvimento

### Tarefa 1: Motor de Inteligência de Cidades (`P-107`) e Descoberta de Leads no Trajeto (`P-108`) no `fitoherb-ai` `[PARALLEL]`

**Descritivo Detalhado:**
Implementar no microserviço `fitoherb-ai` os serviços de enriquecimento demográfico/econômico por município (`city_insights_service.py`) e de descoberta de estabelecimentos comerciais do segmento farmacêutico e de produtos naturais ao longo da rota (`poi_discovery_service.py`), integrando-os aos schemas (`routing_dto.py`), aos endpoints `/routing/optimize` e `/routing/recalculate`, e à geração de manifesto PDF (`pdf_service.py`).

**Critérios de Aceite:**
- [x] **[P-107]** Ao chamar `POST /api/v1/routing/optimize` ou `/recalculate`, a resposta `OptimizeRouteResponse` deve incluir a lista `city_insights` contendo todas as cidades únicas com paradas na rota e seus respectivos dados: `city`, `state`, `ibge_code`, `population`, `city_tier`, `city_tier_label`, `demographic_density_hab_km2`, `gdp_per_capita_brl`, `regional_hub_name`, `commercial_potential_summary`, `confirmed_stops_count`, `suggested_leads_count` e `estimated_dwell_minutes`.
- [x] **[P-108]** Ao chamar `POST /api/v1/routing/optimize` (quando `discover_suggestions=True`), o sistema deve buscar farmácias e lojas de produtos naturais próximas ao corredor da rota, excluindo rigorosamente pontos já presentes em `stops`, `depot` ou `excluded_locations` (raio <= 80m ou similaridade textual/fonética >= 0.82).
- [x] **[P-108]** Cada sugestão descoberta deve retornar categoria (`FARMACIA` ou `PRODUTOS_NATURAIS`), endereço legível, distância de desvio estimado (`detour_distance_km`) e tempo adicional estimado (`detour_time_minutes`), além de `is_suggestion = True`.
- [x] **[P-105 / P-107]** O gerador de PDF (`pdf_service.py` e exportação frontend) deve incluir o resumo de Inteligência das Cidades da Rota sem expor coordenadas geográficas (`lat`/`lon`).

**Etapas de Execução (Checklist Técnico):**
- [x] **1.1. Estender Modelos de Domínio ([`app/domains/routing/models/point.py`](file:///c:/Users/danie/Documents/Github/fitoherb-ai/app/domains/routing/models/point.py)):**
  - Adicionar em `DeliveryStop`:
    - `is_suggestion: bool = Field(False, description="Indica se o ponto é uma sugestão proativa da IA (P-108)")`
    - `suggestion_category: Optional[str] = Field(None, description="FARMACIA ou PRODUTOS_NATURAIS")`
    - `detour_distance_km: Optional[float] = Field(None, description="Desvio viário estimado em km")`
    - `detour_time_minutes: Optional[float] = Field(None, description="Tempo adicional estimado do desvio em minutos")`
- [x] **1.2. Estender Schemas e DTOs ([`app/domains/routing/schemas/routing_dto.py`](file:///c:/Users/danie/Documents/Github/fitoherb-ai/app/domains/routing/schemas/routing_dto.py)):**
  - Criar `CityInsightDto(BaseModel)` com: `city`, `state`, `ibge_code`, `population`, `city_tier`, `city_tier_label`, `demographic_density_hab_km2`, `gdp_per_capita_brl`, `regional_hub_name`, `commercial_potential_summary`, `confirmed_stops_count`, `suggested_leads_count`, `estimated_dwell_minutes`.
  - Criar `SuggestedStopDto(BaseModel)` com: `id`, `name`, `lat`, `lon`, `address`, `suggestion_category`, `category_label`, `detour_distance_km`, `detour_time_minutes`, `nearest_stop_id`, `nearest_stop_name`, `is_suggestion: bool = True`.
  - Atualizar `OptimizeRouteRequest` adicionando `discover_suggestions: bool = True`, `max_suggestions: int = Field(5, ge=1, le=12)` e `excluded_locations: List[LocationPoint] = Field(default_factory=list)`.
  - Atualizar `OrderedStopDto` adicionando `is_suggestion: bool = False`, `suggestion_category: Optional[str] = None`, `detour_distance_km: Optional[float] = None`, `detour_time_minutes: Optional[float] = None`.
  - Atualizar `OptimizeRouteResponse` adicionando `city_insights: List[CityInsightDto] = Field(default_factory=list)` e `suggested_stops: List[SuggestedStopDto] = Field(default_factory=list)`.
  - Atualizar `ExportPdfRequest` adicionando `city_insights: List[CityInsightDto] = Field(default_factory=list)`.
- [x] **1.3. Expandir Cache SQLite ([`app/domains/routing/infrastructure/osrm_provider.py`](file:///c:/Users/danie/Documents/Github/fitoherb-ai/app/domains/routing/infrastructure/osrm_provider.py)):**
  - Em `GeoCache._init_db()`, criar tabelas `city_insights_cache (city_key TEXT PRIMARY KEY, payload TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)` e `poi_discovery_cache (corridor_key TEXT PRIMARY KEY, payload TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)`.
  - Adicionar métodos `get_city_insight(city_key: str)`, `set_city_insight(city_key: str, data: dict)`, `get_poi_candidates(corridor_key: str)` e `set_poi_candidates(corridor_key: str, data: list)`.
- [x] **1.4. Criar Serviço de Inteligência Demográfica por Cidade (`app/domains/routing/services/city_insights_service.py`):**
  - Implementar `CityInsightsService` com método `build_city_insights(depot: LocationPoint, ordered_stops: List[OrderedStopDto], suggested_stops: List[SuggestedStopDto], default_service_minutes: int = 20) -> List[CityInsightDto]`.
  - Incluir normalização de distritos (`DISTRICT_TO_MUNICIPALITY_MAP`), base curada de municípios da Bahia/Nordeste e capitais brasileiras (`CURATED_MUNICIPALITIES_DB`: código IBGE, população Censo/Estimativa IBGE, densidade `hab/km²`, PIB per capita BRL, polo econômico regional e recomendação comercial Fitoherb) + consulta com timeout `2.5s` à API oficial do IBGE e cache via `geo_cache`.
- [x] **1.5. Criar Serviço de Descoberta Proativa de Leads (`app/domains/routing/services/poi_discovery_service.py`):**
  - Implementar `PoiDiscoveryService` com método `discover_along_route(depot: LocationPoint, stops: List[DeliveryStop], excluded_locations: List[LocationPoint], max_suggestions: int = 5) -> List[SuggestedStopDto]`.
  - Implementar clusterização de pivôs da rota, consulta Overpass API / Photon para `FARMACIA` e `PRODUTOS_NATURAIS` + cache SQLite + catálogo de contingência realista geolocalizado próximo aos pontos da rota (respeitando sanitização LGPD sem PII de pessoas físicas e sem enviar identidade do vendedor).
  - Implementar `is_duplicate_poi(candidate_name, candidate_lat, candidate_lon, candidate_city, existing_points)` descartando qualquer ponto com distância Haversine `<= 0.08 km` (80m) ou similaridade normalizada/fonética `>= 0.82`.
  - Implementar cálculo de custo de inserção mínima (`detour_distance_km` e `detour_time_minutes`) e ranqueamento com balanceamento de mix (`FARMACIA` + `PRODUTOS_NATURAIS`).
- [x] **1.6. Integrar nos Endpoints de Roteirização ([`app/api/v1/routers/routing_router.py`](file:///c:/Users/danie/Documents/Github/fitoherb-ai/app/api/v1/routers/routing_router.py)):**
  - Em `optimize_route(payload)`:
    - Se `payload.discover_suggestions` for `True`, acionar `poi_discovery_service.discover_along_route(...)`, converter as sugestões descobertas em `DeliveryStop(is_suggestion=True, ...)` e mesclá-las às paradas antes da matriz OSRM e do `RoutingGeneticSolver`, para que já entrem posicionadas de forma inteligente na lista e no traçado inicial.
    - Propagar `is_suggestion`, `suggestion_category`, `detour_distance_km` e `detour_time_minutes` em `_evaluate_ordered_route(...)`.
    - Acionar `city_insights_service.build_city_insights(...)` tanto em `/optimize` quanto em `/recalculate` (em `/recalculate`, não descobrir novas sugestões, apenas recalcular métricas e `city_insights` para as paradas enviadas).
- [x] **1.7. Atualizar Manifesto PDF Backend ([`app/domains/routing/services/pdf_service.py`](file:///c:/Users/danie/Documents/Github/fitoherb-ai/app/domains/routing/services/pdf_service.py)):**
  - Em `PdfReportService.generate_route_manifest`, renderizar a seção **"Inteligência Demográfica e Comercial das Cidades da Rota"** (tabela com Município/UF, População IBGE, Porte, PIB per capita, Paradas e Foco Comercial) e identificar na tabela de visitas se um ponto era uma oportunidade sugerida, mantendo zero exposição de latitude/longitude (`P-105`).

**Audit (Testes e Validação):**
- [x] **Cenário 1:** Otimizar rota com paradas em Salvador e Lauro de Freitas; deve retornar `city_insights` para ambos os municípios com população IBGE, PIB per capita, porte e contagem correta de paradas.
- [x] **Cenário 2:** Otimizar rota passando ponto existente "Drogaria São Paulo - Pituba"; a lista de sugestões não deve conter esse mesmo estabelecimento (deduplicação <= 80m e nome similar).
- [x] **Cenário 3:** Simular falha/timeout na API externa (Overpass/IBGE); o endpoint `/optimize` deve responder HTTP 200 utilizando cache SQLite / fallback determinístico sem quebrar a otimização.

---

### Tarefa 2: Painel de Inteligência de Cidades, Sugestões no Mapa/Lista e Manejo em Lote com Recálculo Diferido (`P-107`, `P-108`, `P-109`) no `fitoherb-frontend-v2` `[PARALLEL]`

**Descritivo Detalhado:**
Atualizar o componente `SellerRoutesComponent` (`seller-routes.component.ts`, `.html`, `.scss`) e `routing.interface.ts` para exibir o Relatório de Inteligência das Cidades da Rota, injetar as sugestões de novas farmácias e lojas de produtos naturais na lista da rota com marcadores visuais distintos, e implementar o **Modo de Manejo de Lista em Lote (Staging)** onde o vendedor remove/gerencia múltiplas sugestões ou paradas sem disparar recálculo a cada remoção, recalculando a rota apenas ao clicar no botão de conclusão do manejo.

**Critérios de Aceite:**
- [x] **[P-107]** Exibir na aba *Roteiro da IA* a seção **"Inteligência das Cidades na Rota"** com cards ricos por cidade (População, Porte, PIB per capita, Região, Nº de Paradas, Tempo na Cidade, Oportunidades Descobertas e Dica Comercial).
- [x] **[P-108 / P-109]** Ao prever a rota, incluir as sugestões descobertas na lista de manejo com badge visual **`SUGESTÃO`** (`Farmácia` ou `Produtos Naturais`), indicando o desvio estimado (`+X.X km`) e exibindo pinos diferenciados no mapa Leaflet.
- [x] **[P-109]** Ao clicar em remover uma sugestão (ou remover/alternar múltiplas paradas/sugestões na lista), o sistema **NÃO** deve chamar o endpoint de otimização/recálculo imediatamente; deve atualizar a lista local instantaneamente e exibir a barra de manejo pendente (*"Modo de Manejo: X alteração(ões) pendente(s)"*) com os botões **"Concluir Manejo e Recalcular Rota"** e **"Desfazer Alterações"**.
- [x] **[P-109]** Ao clicar em **"Concluir Manejo e Recalcular Rota"**, o sistema executa uma única chamada de recálculo/otimização com os pontos finais mantidos pelo vendedor, atualizando o mapa, os horários, os KPIs, o relatório de cidades e salvando a rota agendada.
- [x] **[P-108]** Permitir ao vendedor favoritar (`Salvar nos Favoritos`) uma sugestão descoberta caso queira transformá-la em cliente recorrente.

**Etapas de Execução (Checklist Técnico):**
- [x] **2.1. Atualizar Interfaces TypeScript ([`src/app/types/routing/routing.interface.ts`](file:///c:/Users/danie/Documents/Github/fitoherb-frontend-v2/src/app/types/routing/routing.interface.ts)):**
  - Adicionar `CityInsightDto` e `SuggestedStopDto`.
  - Estender `DeliveryStopDto` e `OrderedStopDto` com `is_suggestion?: boolean`, `suggestion_category?: 'FARMACIA' | 'PRODUTOS_NATURAIS' | null`, `detour_distance_km?: number | null`, `detour_time_minutes?: number | null`.
  - Estender `OptimizeRouteRequest` com `discover_suggestions?: boolean`, `max_suggestions?: number`, `excluded_locations?: LocationPointDto[]`.
  - Estender `OptimizeRouteResponse` com `city_insights?: CityInsightDto[]` e `suggested_stops?: SuggestedStopDto[]`.
- [x] **2.2. Implementar Estado de Manejo em Lote (Batch Staging) e Sugestões em `SellerRoutesComponent` ([`seller-routes.component.ts`](file:///c:/Users/danie/Documents/Github/fitoherb-frontend-v2/src/app/views/admin/components/seller-routes/seller-routes.component.ts)):**
  - Adicionar signals:
    - `readonly discoverSuggestionsEnabled = signal<boolean>(true);`
    - `readonly hasPendingBatchChanges = signal<boolean>(false);`
    - `readonly pendingBatchChangesCount = signal<number>(0);`
    - `readonly isCityInsightsExpanded = signal<boolean>(true);`
    - `readonly dismissedSuggestions = signal<LocationPointDto[]>([]);`
    - `private preStagingSnapshot: { stops: DeliveryStopDto[]; optResult: OptimizeRouteResponse | null } | null = null;`
  - Em `optimizeRoute(discoverNewSuggestions: boolean = true)`:
    - Enviar `discover_suggestions: discoverNewSuggestions` e `excluded_locations: [...this.savedLocations().map(...), ...this.dismissedSuggestions()]`.
    - Ao receber a resposta `res`, sincronizar `this.stops` a partir das visitas de `res.ordered_stops` (incluindo as sugestões descobertas com `is_suggestion: true`), limpando `hasPendingBatchChanges` e `pendingBatchChangesCount`.
  - Implementar métodos de **Manejo em Lote sem Recálculo Imediato (`P-109`)**:
    - `enterBatchStagingIfNeeded()`: salva `preStagingSnapshot` na 1ª alteração.
    - `removeStopFromList(index: number)` e `removeStopFromTimeline(stopId: string, event?: Event)`: remove a parada/sugestão localmente de `stops` e `optimizationResult().ordered_stops`, adiciona em `dismissedSuggestions` se `is_suggestion`, incrementa `pendingBatchChangesCount`, atualiza os marcadores do mapa (`renderMarkers()`), **sem chamar o backend**.
    - `confirmSuggestionInRoute(stopId: string, event?: Event)`: converte `is_suggestion = false` localmente (mantendo na rota como visita confirmada) e incrementa `pendingBatchChangesCount`.
    - `removeAllSuggestions()`: remove de uma só vez todos os itens com `is_suggestion === true` da lista local e ativa a barra de manejo em lote.
    - `saveSuggestionAsFavorite(stop: OrderedStopDto | DeliveryStopDto, event?: Event)`: salva a sugestão em `SavedLocationsService` como `FAVORITE` e marca como confirmada.
    - `undoBatchChanges()`: restaura `stops` e `optimizationResult` a partir de `preStagingSnapshot`, zerando `hasPendingBatchChanges` e `pendingBatchChangesCount`.
    - `commitBatchChangesAndRecalculate()`: executa **uma única chamada** ao backend (`recalculateRoute` ou `optimizeRoute` com `discover_suggestions: false` com os `stops` restantes), atualiza polilinha, horários e `city_insights`, limpa o modo de manejo e salva via `autoSaveRoute(res)`.
- [x] **2.3. Atualizar Marcadores no Mapa e Exportação PDF Frontend ([`seller-routes.component.ts`](file:///c:/Users/danie/Documents/Github/fitoherb-frontend-v2/src/app/views/admin/components/seller-routes/seller-routes.component.ts)):**
  - Em `renderOptimizedMarkers()` e `renderPlanningMarkers()`: diferenciar os pinos com `is_suggestion === true` usando classes `.pin--suggestion-pharma` e `.pin--suggestion-natural` + badge `+X.Xkm`.
  - Em `exportPdf()`: incluir quadro resumo **"Inteligência Demográfica das Cidades da Rota"** antes da tabela sequencial de visitas, respeitando `P-105` (zero coordenadas).
- [x] **2.4. Atualizar Template e Estilos ([`seller-routes.component.html`](file:///c:/Users/danie/Documents/Github/fitoherb-frontend-v2/src/app/views/admin/components/seller-routes/seller-routes.component.html) e [`seller-routes.component.scss`](file:///c:/Users/danie/Documents/Github/fitoherb-frontend-v2/src/app/views/admin/components/seller-routes/seller-routes.component.scss)):**
  - Seguir rigorosamente o Design Plan (`.agents/docs/design/plans/commercial_routing_city_and_suggestions.md`).
  - Adicionar barra sticky de **Modo de Manejo da Lista (`.batch-staging-bar`)** nas abas *Paradas* e *Roteiro da IA* com contador de alterações pendentes, botão **"Desfazer"** e botão de destaque **"Concluir Manejo e Recalcular Rota"**.
  - Adicionar seção expansível **"Inteligência das Cidades na Rota (`city_insights`)"** na aba *Roteiro da IA*.
  - Adicionar badges **`SUGESTÃO · FARMÁCIA`** / **`SUGESTÃO · LOJA NATURAL`**, pílula de desvio (`+X.X km`) e botões rápidos (`Manter na Rota`, `Favoritar`, `Remover`) nos cards de parada e na timeline.

**Audit (Testes e Validação):**
- [x] **Cenário 1:** Prever rota e receber sugestões; remover 3 sugestões seguidas na lista e verificar que nenhuma requisição HTTP de recálculo foi disparada durante os cliques individuais.
- [x] **Cenário 2:** Clicar em "Concluir Manejo e Recalcular Rota" após remover as sugestões indesejadas; verificar que apenas 1 requisição foi enviada e a rota final foi recalculada com sucesso contendo apenas as paradas e sugestões mantidas.
- [x] **Cenário 3:** Exportar PDF da rota otimizada e validar a presença do quadro de Inteligência das Cidades e a ausência total de latitude/longitude.
