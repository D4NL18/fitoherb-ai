# Knowledge Graph — Memória Comprimida do Projeto 🧠

> **Mantido por:** Orquestrador (`context-compressor`)

## 1. Épico 1: Roteirização Comercial Inteligente (`app/domains/routing/`)
- **Objetivo:** Otimização de rotas comerciais multi-parada (TDVRP) com Algoritmo Genético, modelo preditivo de tráfego por faixas horárias/corredores rodoviários, trava de ordem manual (`recalculate`) e geração de manifesto PDF.
- **Novas Capacidades Ativas (`P-107`, `P-108`, `P-109`):**
  - **`P-107` (Relatório de Inteligência das Cidades):** `CityInsightsService` enriquece cada município visitado na rota com população oficial IBGE, porte demográfico (`METROPOLIS`, `REGIONAL_HUB`, `MEDIUM_CITY`, `SMALL_TOWN`), densidade demográfica (`hab/km²`), PIB per capita, polo regional, recomendações de mix comercial Fitoherb e métricas agregadas da rota (paradas confirmadas, sugestões no caminho e tempo de permanência estimado `estimated_dwell_minutes`). Renderizado no painel retrátil da UI e no manifesto PDF com total conformidade com `P-105` (zero coordenadas brutas de GPS no relatório).
  - **`P-108` (Descoberta Proativa de Leads):** `PoiDiscoveryService` descobre farmácias e lojas naturais no corredor viário com cálculo prévio de desvio (`+X.X km`, `+Y min`), categorização visual no Leaflet (`💊` e `🌿`), balanceamento de mix comercial e deduplicação rígida (`<= 80m` ou similaridade fonética `>= 0.82`) contra paradas, base e favoritos, além de sanitização de PII em nomes do OSM.
  - **`P-109` (Manejo em Lote com Recálculo Diferido):** Estado de *Batch Staging* no Frontend (`SellerRoutesComponent`). O vendedor gerencia e remove sugestões e paradas com latência de rede de 0 ms, sem requisições HTTP por clique. Uma única chamada consolidada a `POST /recalculate` (com `discover_suggestions=false`) é emitida ao clicar em "Concluir Manejo e Recalcular Rota", com suporte a reversão via "Desfazer Alterações" (*Snapshot Undo*).
  - **FinOps & Performance (Score 4.94 / 5.00):** Zero consumo de tokens de LLM para insights municipais e POIs (resolvidos via base curada, API gratuita do IBGE e Overpass OSM com cache SQLite L1 `GeoCache`). Scale-to-Zero preservado no Cloud Run.

## 2. Épico 2: Assistente Virtual Inteligente Fitoherb (`app/domains/chat/`)
- **Objetivo:** Chatbot flutuante (`POST /api/v1/chat/messages`) com guardrails determinísticos, roteamento semântico 0 tokens (`IntentRouter`), cache L1 SHA-256 (`ConversationCacheService`), busca neutra no catálogo (`CatalogIndex`) com redirecionamento automático (`NAVIGATE_CATALOG`) e integração enxuta com `gemini-2.5-flash` (`google-genai`).
- **Regras Centrais Ativas (`P-300` a `P-312`):**
  - `P-301` & `P-312`: Base institucional em `app/domains/chat/knowledge/company_profile.yaml` contendo telefone fixo `(71) 3379-7717`, WhatsApp oficial `(71) 99241-9709` (`https://wa.me/5571992419709`), Instagram oficial `@fitoherb` (`https://www.instagram.com/fitoherb`) e e-mail `comercial@fitoherb.com.br`.
  - `P-302` & `P-303`: Bloqueio determinístico de preços/estoque/tabela nutricional (`COMMERCIAL_RESTRICTED`) e de aconselhamento médico/ANVISA (`MEDICAL_RESTRICTED`) com 0 tokens.
  - `P-304` & `P-305`: Neutralidade absoluta entre marcas parceiras e redirecionamento automático (`NAVIGATE_CATALOG`) para `/produtos`.
  - `P-306` & `P-307`: Limite de entrada de 255 caracteres, proibição de travessões no meio de frases explicativas e compactação de histórico a partir de 5 mensagens.
  - `P-308` & `P-312`: `IntentRouter` responde com 0 tokens (`STATIC_KB`) para saudações (`GREETING`), endereço (`COMPANY_LOCATION`), redes sociais/Instagram (`COMPANY_SOCIAL`), telefone/WhatsApp/e-mail (`COMPANY_CONTACT`), história (`COMPANY_ABOUT`) e cobertura (`COMPANY_COVERAGE`), fazendo bypass para o `ChatOrchestrator` quando há menção composta a produtos.
