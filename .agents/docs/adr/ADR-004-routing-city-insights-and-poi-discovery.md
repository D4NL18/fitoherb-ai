# ADR-004: Motor Híbrido de Inteligência de Cidades, Descoberta de POIs Comerciais e Manejo em Lote (Batch Staging)

> **Status:** Aceito  
> **Data:** 2026-11-05  
> **Autor:** Arquiteto (`architect.md`)  
> **Localização Mandatória:** `.agents/docs/adr/ADR-004-routing-city-insights-and-poi-discovery.md`

---

## 1. Contexto do Problema
Os representantes comerciais (perfil `SELLER`) da Fitoherb precisam de três novas capacidades estratégicas durante o planejamento de rotas (`P-107`, `P-108` e `P-109`):
1. **Inteligência Demográfica e Comercial por Cidade (`P-107`):** Visualizar indicadores das cidades visitadas (população IBGE, porte, densidade, PIB per capita estimado, polo regional, nº de paradas e tempo na cidade) sem sofrer lentidão ou falhas caso a API do IBGE esteja indisponível.
2. **Descoberta Proativa de Leads no Trajeto (`P-108`):** Descobrir automaticamente farmácias/drogarias e lojas de produtos naturais situadas ao longo das paradas/cidades da rota que **não estejam** entre os pontos já listados ou salvos pelo vendedor.
3. **Manejo de Lista sem Recálculo Bloqueante (`P-109`):** Quando várias sugestões são adicionadas à lista da rota, o vendedor precisa remover as sugestões indesejadas (ou ajustar paradas) de forma fluida; se cada clique disparasse uma requisição de recálculo OSRM + Algoritmo Genético, a interface travaria a cada remoção.

---

## 2. Decisão Arquitetural

### 2.1. Arquitetura Híbrida de 4 Camadas para Inteligência de Cidades (`CityInsightsService`)
Implementar `app/domains/routing/services/city_insights_service.py` no `fitoherb-ai` combinando:
1. **Catálogo Curado L1 (`CURATED_MUNICIPALITIES_DB`):** Base embarcada em memória com indicadores oficiais IBGE (Censo 2022 / Estimativas 2024 e PIB per capita) dos principais municípios da Bahia, Nordeste e capitais brasileiras, além de normalização de distritos/bairros (ex.: Abrantes ➔ Camaçari, Praia do Forte ➔ Mata de São João).
2. **Cache SQLite L2 (`city_insights_cache` em `osrm_cache.db`):** TTL de 30 dias para evitar chamadas repetidas de rede.
3. **Integração IBGE REST API L3 (`servicodados.ibge.gov.br`):** Consulta HTTP com timeout estrito (`2.5s`) para municípios não catalogados.
4. **Fallback Heurístico L4 por `CityTier`:** Caso o município não conste no catálogo e a rede esteja offline, infere indicadores demográficos e recomendação comercial com base no `CityTier` (`TrafficPredictor`), garantindo 100% de disponibilidade e **0 tokens de LLM**.

### 2.2. Descoberta Espacial de POIs e Deduplicação Geodésica/Fonética (`PoiDiscoveryService`)
Implementar `app/domains/routing/services/poi_discovery_service.py` no `fitoherb-ai`:
1. **Fontes Espaciais:** Consulta Overpass API (`amenity=pharmacy`, `shop=chemist`, `shop=health_food`, `shop=herbalist`, `shop=nutrition_supplements`, `shop=vitamins`) e Photon Komoot no corredor das paradas da rota, com cache SQLite de 7 dias (`poi_discovery_cache`) e catálogo curado de contingência por município/bairro.
2. **Filtro de Deduplicação Duplo (`P-108.3`):** Um POI candidato é descartado se:
   - Sua distância Haversine até qualquer ponto em `[depot] + stops + excluded_locations` for **<= 80 metros (`0.08 km`)**; **OU**
   - Sua similaridade textual/fonética normalizada (token/SequenceMatcher PT-BR) com o nome de qualquer ponto existente na mesma cidade/raio for **>= 0.82**.
3. **Injeção Controlada na Previsão:** Quando `discover_suggestions=True`, as melhores oportunidades (ordenadas pelo menor desvio `detour_distance_km` e score comercial em relação aos trechos da rota, limitadas a `max_suggestions`) são incluídas na resposta (`suggested_stops` e integradas em `ordered_stops` com `is_suggestion=True`), permitindo avaliação imediata na lista e no mapa.

### 2.3. Máquina de Estado de Manejo em Lote (Batch Staging) com Angular Signals (`P-109`)
No `SellerRoutesComponent` (`fitoherb-frontend-v2`):
- Introduzir os signals `hasPendingBatchChanges`, `pendingBatchChangesCount`, `preStagingSnapshot` e `dismissedSuggestions`.
- Operações de manejo de lista (`removeStop`, `removeSuggestionFromRoute`, `confirmSuggestionInRoute`, `removeAllSuggestions`) mutam **apenas os signals locais** em memória e atualizam os pinos do Leaflet sem emitir chamadas HTTP ao `fitoherb-ai`.
- Somente a ação explícita **"Concluir Manejo e Recalcular Rota"** (`commitBatchChangesAndRecalculate()`) envia o payload consolidado com `discover_suggestions: false` ao backend, recalculando a geometria OSRM, horários e `city_insights` em uma única transação de rede.

---

## 3. Alternativas Consideradas
1. **Opção A: Consultar exclusivamente a API do IBGE e Overpass em tempo real sem cache ou catálogo local.**
   - *Motivo de descarte:* A Overpass API possui rate-limiting severo em IPs compartilhados e a API do IBGE pode apresentar latência > 3s, o que degradaria o tempo de resposta da otimização de rota.
2. **Opção B: Recalcular a rota automaticamente com `debounceTime(500)` a cada remoção de sugestão.**
   - *Motivo de descarte:* Viola diretamente a regra de negócio `P-109` e a experiência do vendedor, que analisa a lista com calma e pode levar vários segundos entre uma remoção e outra, gerando múltiplos recálculos intermediários indesejados.

---

## 4. Consequências e Trade-offs
- **Pontos Positivos:**
  - Zero latência (`0 ms`) durante a curadoria/remoção de sugestões e paradas na lista pelo vendedor.
  - Resiliência total contra quedas ou timeouts de APIs externas (Overpass, Photon, IBGE) graças ao SQLite `GeoCache` e ao catálogo curado.
  - Nenhuma migração de banco de dados necessária no `fitoherb-backend-v2` (persistência JSON transparente em `scheduled_routes`).
- **Pontos Negativos / Débito Técnico Aceito:**
  - Enquanto o vendedor estiver com alterações pendentes no modo de manejo (`hasPendingBatchChanges() === true`), a polilinha e os horários exibidos pertencem à última previsão até que ele clique em **"Concluir Manejo e Recalcular Rota"** (mitigado por banner visual claro e pulsante de alterações pendentes).
