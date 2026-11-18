# Contrato de API: Fitoherb AI Roteirização Comercial e Inteligência de Cidades

Este documento descreve detalhadamente como a API de Roteirização Comercial (`fitoherb-ai`) está desenvolvida, incluindo o Algoritmo Genético com Trava de Ordem (`P-103`, `P-104`), Horário Marcado (`P-106`), Relatório de Inteligência Demográfica por Cidade (`P-107`), Descoberta Proativa de Farmácias e Lojas de Produtos Naturais (`P-108`) e suporte ao Manejo em Lote com Recálculo Diferido (`P-109`).

## 1. Visão Geral
- **Serviço:** `fitoherb-ai` (FastAPI / Python 3.11+)
- **Porta Padrão:** `8000`
- **Prefixo Base:** `/api/v1/routing`
- **Propósito:** Resolver o Problema de Roteamento de Veículo Único Dependente do Tempo (TDVRP), enriquecer o roteiro com indicadores demográficos e comerciais das cidades visitadas (IBGE + Base Curada), sugerir proativamente novos leads (farmácias e lojas naturais) não listados na rota e gerar o manifesto oficial em PDF sem exposição de coordenadas brutas (`P-105`).

---

## 2. Endpoints

### 2.1. `POST /api/v1/routing/optimize`
**Objetivo:** Executa o Algoritmo Genético de Vendedor Único (Locked-Order GA + 2-Opt) sobre a matriz viária OSRM, descobre novos estabelecimentos sugeridos no corredor da rota (quando `discover_suggestions = true`) e gera o relatório demográfico e comercial por cidade (`city_insights`).

**Requisição (Request):**
- **Autenticação:** Comunicação CORS / Gateway autenticada no ecossistema Fitoherb.
- **Headers:** `Content-Type: application/json`

**Request Body (`OptimizeRouteRequest`):**
```json
{
  "depot": {
    "id": "base-vendedor",
    "name": "Minha Residência (Base)",
    "lat": -12.8992,
    "lon": -38.3242,
    "address": {
      "street": "Rua Itaeté",
      "number": "434",
      "neighborhood": "Pitangueiras",
      "city": "Lauro de Freitas",
      "state": "BA",
      "postal_code": "42701-360",
      "full_address": "Rua Itaeté, 434, Pitangueiras, Lauro de Freitas - BA"
    }
  },
  "stops": [
    {
      "id": "stop-1",
      "name": "Drogaria São Paulo - Pituba",
      "lat": -12.9984,
      "lon": -38.4908,
      "priority": "HIGH",
      "fixed_order": 1,
      "service_duration_minutes": 25,
      "target_arrival_time": "09:00",
      "is_suggestion": false,
      "suggestion_category": null,
      "detour_distance_km": null,
      "detour_time_minutes": null,
      "address": {
        "street": "Av. Manoel Dias da Silva",
        "number": "1500",
        "neighborhood": "Pituba",
        "city": "Salvador",
        "state": "BA",
        "postal_code": "41830-000",
        "full_address": "Av. Manoel Dias da Silva, 1500, Pituba, Salvador - BA"
      }
    }
  ],
  "return_to_depot": true,
  "departure_time": "08:00",
  "default_service_minutes": 20,
  "discover_suggestions": true,
  "max_suggestions": 5,
  "excluded_locations": [
    {
      "id": "fav-99",
      "name": "Farmácia Pague Menos - Pituba",
      "lat": -12.9991,
      "lon": -38.4895
    }
  ]
}
```

**Resposta de Sucesso (200 OK - `OptimizeRouteResponse`):**
```json
{
  "total_time_minutes": 68.4,
  "total_distance_km": 31.5,
  "stops_count": 2,
  "ordered_stops": [
    {
      "step": 0,
      "id": "base-vendedor",
      "name": "Minha Residência (Base)",
      "action": "DEPARTURE",
      "is_fixed": true,
      "fixed_order": null,
      "priority": "BASE",
      "arrival_time_minutes": 0.0,
      "lat": -12.8992,
      "lon": -38.3242,
      "estimated_arrival_clock": "08:00",
      "estimated_departure_clock": "08:00",
      "service_duration_minutes": 0,
      "traffic_factor": 1.0,
      "traffic_condition": "LIVRE",
      "target_arrival_time": null,
      "has_time_conflict": false,
      "time_conflict_message": null,
      "is_suggestion": false,
      "suggestion_category": null,
      "detour_distance_km": null,
      "detour_time_minutes": null,
      "address": {
        "street": "Rua Itaeté",
        "number": "434",
        "neighborhood": "Pitangueiras",
        "city": "Lauro de Freitas",
        "state": "BA",
        "postal_code": "42701-360",
        "full_address": "Rua Itaeté, 434, Pitangueiras, Lauro de Freitas - BA"
      }
    },
    {
      "step": 1,
      "id": "stop-1",
      "name": "Drogaria São Paulo - Pituba",
      "action": "VISIT",
      "is_fixed": true,
      "fixed_order": 1,
      "priority": "HIGH",
      "arrival_time_minutes": 28.0,
      "lat": -12.9984,
      "lon": -38.4908,
      "estimated_arrival_clock": "08:28",
      "estimated_departure_clock": "09:25",
      "service_duration_minutes": 25,
      "traffic_factor": 1.45,
      "traffic_condition": "PICO_MANHA",
      "target_arrival_time": "09:00",
      "has_time_conflict": false,
      "time_conflict_message": null,
      "is_suggestion": false,
      "suggestion_category": null,
      "detour_distance_km": null,
      "detour_time_minutes": null,
      "address": {
        "street": "Av. Manoel Dias da Silva",
        "number": "1500",
        "neighborhood": "Pituba",
        "city": "Salvador",
        "state": "BA",
        "postal_code": "41830-000",
        "full_address": "Av. Manoel Dias da Silva, 1500, Pituba, Salvador - BA"
      }
    },
    {
      "step": 2,
      "id": "sug-8f3a1c",
      "name": "Mundo Verde - Pituba",
      "action": "VISIT",
      "is_fixed": false,
      "fixed_order": null,
      "priority": "REGULAR",
      "arrival_time_minutes": 33.5,
      "lat": -13.0012,
      "lon": -38.4865,
      "estimated_arrival_clock": "09:30",
      "estimated_departure_clock": "09:45",
      "service_duration_minutes": 15,
      "traffic_factor": 1.15,
      "traffic_condition": "MODERADO",
      "target_arrival_time": null,
      "has_time_conflict": false,
      "time_conflict_message": null,
      "is_suggestion": true,
      "suggestion_category": "PRODUTOS_NATURAIS",
      "detour_distance_km": 0.9,
      "detour_time_minutes": 3.2,
      "address": {
        "street": "Av. Paulo VI",
        "number": "1820",
        "neighborhood": "Pituba",
        "city": "Salvador",
        "state": "BA",
        "postal_code": "41810-001",
        "full_address": "Av. Paulo VI, 1820, Pituba, Salvador - BA"
      }
    },
    {
      "step": 3,
      "id": "base-vendedor",
      "name": "Minha Residência (Base)",
      "action": "RETURN",
      "is_fixed": true,
      "fixed_order": null,
      "priority": "BASE",
      "arrival_time_minutes": 68.4,
      "lat": -12.8992,
      "lon": -38.3242,
      "estimated_arrival_clock": "10:20",
      "estimated_departure_clock": "10:20",
      "service_duration_minutes": 0,
      "traffic_factor": 1.05,
      "traffic_condition": "LIVRE",
      "target_arrival_time": null,
      "has_time_conflict": false,
      "time_conflict_message": null,
      "is_suggestion": false,
      "suggestion_category": null,
      "detour_distance_km": null,
      "detour_time_minutes": null,
      "address": {
        "street": "Rua Itaeté",
        "number": "434",
        "neighborhood": "Pitangueiras",
        "city": "Lauro de Freitas",
        "state": "BA",
        "postal_code": "42701-360",
        "full_address": "Rua Itaeté, 434, Pitangueiras, Lauro de Freitas - BA"
      }
    }
  ],
  "geojson_geometry": {
    "type": "FeatureCollection",
    "features": [],
    "coordinates": []
  },
  "fitness_history": [120.4, 98.2, 85.1, 74.3],
  "departure_clock": "08:00",
  "estimated_finish_clock": "10:20",
  "total_transit_minutes": 68.4,
  "total_service_minutes": 40.0,
  "peak_hours_encountered": 1,
  "has_any_time_conflict": false,
  "time_conflict_count": 0,
  "city_insights": [
    {
      "city": "Salvador",
      "state": "BA",
      "ibge_code": "2927408",
      "population": 2417678,
      "city_tier": "METROPOLIS",
      "city_tier_label": "Metrópole (> 1M hab)",
      "demographic_density_hab_km2": 3486.5,
      "gdp_per_capita_brl": 27540.0,
      "regional_hub_name": "Capital / Região Metropolitana (RMS)",
      "commercial_potential_summary": "Metrópole de Alta Densidade: Priorizar grandes redes de drogarias, farmácias de manipulação premium e empórios de suplementação esportiva/longevidade nos corredores comerciais.",
      "confirmed_stops_count": 1,
      "suggested_leads_count": 1,
      "estimated_dwell_minutes": 40
    },
    {
      "city": "Lauro de Freitas",
      "state": "BA",
      "ibge_code": "2919207",
      "population": 203331,
      "city_tier": "REGIONAL_HUB",
      "city_tier_label": "Polo Regional / Metropolitano",
      "demographic_density_hab_km2": 3526.3,
      "gdp_per_capita_brl": 35820.0,
      "regional_hub_name": "Sede Fitoherb / Eixo Metropolitano Norte",
      "commercial_potential_summary": "Polo de Alto Poder Aquisitivo (Sede Fitoherb): Forte consumo per capita em saudabilidade, dermocosméticos naturais, fitoterápicos padronizados e lojas especializadas em vida saudável.",
      "confirmed_stops_count": 0,
      "suggested_leads_count": 0,
      "estimated_dwell_minutes": 0
    }
  ],
  "suggested_stops": [
    {
      "id": "sug-8f3a1c",
      "name": "Mundo Verde - Pituba",
      "lat": -13.0012,
      "lon": -38.4865,
      "suggestion_category": "PRODUTOS_NATURAIS",
      "category_label": "Produtos Naturais / Fitoterápicos",
      "detour_distance_km": 0.9,
      "detour_time_minutes": 3.2,
      "nearest_stop_id": "stop-1",
      "nearest_stop_name": "Drogaria São Paulo - Pituba",
      "is_suggestion": true,
      "address": {
        "street": "Av. Paulo VI",
        "number": "1820",
        "neighborhood": "Pituba",
        "city": "Salvador",
        "state": "BA",
        "postal_code": "41810-001",
        "full_address": "Av. Paulo VI, 1820, Pituba, Salvador - BA"
      }
    }
  ]
}
```

**Respostas de Erro Mapeadas:**
- **400 Bad Request:** Lista `stops` vazia (`"É necessário fornecer ao menos uma parada de visita."`).
- **422 Unprocessable Entity:** Payload inválido ou tipos de coordenadas incorretos.

---

### 2.2. `POST /api/v1/routing/recalculate`
**Objetivo:** Recalcula as métricas viárias OSRM, horários projetados, conflitos de janela temporal (`P-106`) e relatório de inteligência das cidades (`P-107`) mantendo **rigorosamente** a sequência de paradas enviada na requisição (após reordenação manual Drag & Drop ou após conclusão do Manejo em Lote `P-109` sem reinjetar novas sugestões).

- **Request Body:** `OptimizeRouteRequest` (força internamente `discover_suggestions = False` para preservar exatamente a lista filtrada/ordenada pelo vendedor).
- **Response 200 OK:** `OptimizeRouteResponse` (com `city_insights` recalculado para as paradas mantidas).

---

### 2.3. `POST /api/v1/routing/export-pdf`
**Objetivo:** Gera o relatório oficial em PDF (`application/pdf`) contendo cabeçalho Fitoherb, resumo de KPIs, quadro de Inteligência das Cidades da Rota (`P-107`), imagem do mapa (se aplicável) e tabela sequencial de paradas sem expor coordenadas (`P-105`).

**Request Body (`ExportPdfRequest`):**
```json
{
  "seller_name": "Vendedor Fitoherb",
  "date": "05/11/2026",
  "total_time_minutes": 68.4,
  "total_distance_km": 31.5,
  "ordered_stops": [],
  "city_insights": [],
  "map_image_base64": "data:image/png;base64,..."
}
```

---

### 2.4. `GET /api/v1/routing/search-address` e `GET /api/v1/routing/reverse-geocode`
**Objetivo:** Proxies de geocodificação direta (com expansão fonética PT-BR e priorização por distância Haversine à base) e geocodificação reversa via Photon/Nominatim.

---

## 3. Implementação no Frontend (`fitoherb-frontend-v2`)

- **Serviço:** `CommercialRoutingService` (`src/app/services/commercial-routing/commercial-routing.service.ts`).
- **Componente:** `SellerRoutesComponent` (`src/app/views/admin/components/seller-routes/seller-routes.component.ts`).
- **Fluxo de Manejo em Lote (`P-109`):**
  1. Na previsão inicial (`optimizeRoute()`), o frontend envia `discover_suggestions: true` e `excluded_locations` (contendo os favoritos salvos do vendedor e quaisquer sugestões previamente descartadas).
  2. As sugestões descobertas são mescladas na lista de paradas com `is_suggestion: true` e renderizadas na lista e no mapa com badge **`SUGESTÃO`** (`Farmácia` ou `Loja Natural`).
  3. Qualquer remoção de sugestão, confirmação de sugestão ou exclusão de parada aciona o estado local `hasPendingBatchChanges = true` (`pendingBatchChangesCount > 0`), atualizando a UI instantaneamente **sem chamar `/optimize` ou `/recalculate`**.
  4. Ao clicar em **"Concluir Manejo e Recalcular Rota"**, o frontend executa uma única chamada ao backend com `discover_suggestions: false` contendo apenas os pontos mantidos pelo vendedor.
