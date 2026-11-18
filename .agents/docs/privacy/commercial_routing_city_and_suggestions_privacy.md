# Parecer Oficial de Privacy by Design & Conformidade LGPD 🛡️📜

**Feature / Módulo:** Inteligência Demográfica por Cidade e Descoberta Proativa de Leads com Manejo em Lote (`commercial_routing_city_and_suggestions`)  
**Regras Auditadas:** `P-105`, `P-107`, `P-108` e `P-109` ([`commercial_routing.md`](file:///c:/Users/danie/Documents/Github/fitoherb-ai/.agents/docs/business_rules/commercial_routing.md))  
**Etapa da Esteira:** Etapa 2 — Revisão de Privacy by Design & Bases Legais  
**Autoridade Responsável:** Encarregado de Proteção de Dados / DPO (`privacy_officer`)  
**Skill Aplicada:** `lgpd-privacy-expert` (Lei nº 13.709/2018 - LGPD & 7 Princípios de Ann Cavoukian)  
**Status do Parecer:** **APROVADO COM SALVAGUARDAS ARQUITETURAIS OBRIGATÓRIAS** ✅

---

## 1. Matriz de Classificação Jurídico-Técnica de Dados (LGPD)

Conforme o Art. 5º e Art. 12 da LGPD, todos os insumos e artefatos de dados manipulados pelas novas funcionalidades (`P-107`, `P-108`, `P-109`) foram auditados e classificados:

| Domínio / Funcionalidade | Campos / Atributos no Payload | Classificação LGPD | Escopo de Incidência e Fundamentação Legal |
| :--- | :--- | :--- | :--- |
| **Relatório de Inteligência das Cidades (`P-107`)** | `city`, `state`, `ibge_code`, `population`, `city_tier`, `demographic_density_hab_km2`, `gdp_per_capita_brl`, `regional_hub_name`, `commercial_potential_summary` | **Dado Público / Estatístico Agregado (Não Pessoal)** | **Fora do escopo de dados pessoais (Art. 1º e Art. 12 da LGPD).** Trata-se exclusivamente de indicadores macroeconômicos e demográficos agregados em nível municipal (IBGE), sem qualquer possibilidade de identificação ou inferência sobre pessoas naturais. |
| **Métricas Operacionais da Cidade (`P-107`)** | `confirmed_stops_count`, `suggested_leads_count`, `estimated_dwell_minutes` | **Dado Operacional Corporativo (Vinculado ao Vendedor no Backend)** | **Execução de Contrato / Procedimentos Preliminares (Art. 7º, V)** e **Legítimo Interesse do Controlador (Art. 7º, IX)** para planejamento logístico e apoio à força de vendas B2B. |
| **Sugestão Proativa de Leads Comerciais (`P-108`)** | `id` (`sug-...`), `name` (Razão Social / Nome Fantasia), `category` (`FARMACIA` / `PRODUTOS_NATURAIS`), `address`, `street`, `number`, `neighborhood`, `city`, `state`, `detour_distance_km`, `detour_time_minutes`, `is_suggestion` | **Dado de Pessoa Jurídica / Ponto de Interesse Comercial Público (Não Pessoal)** | **Não sujeito à LGPD (Art. 1º — proteção restrita a pessoa natural).** Dados extraídos de diretórios geográficos abertos (OpenStreetMap / Overpass / Photon) referentes exclusivamente a estabelecimentos comerciais B2B (farmácias, drogarias e lojas de produtos naturais). |
| **Ponto de Partida / Base do Vendedor (`P-101` / `P-105` / `P-108`)** | `depot` (`lat`, `lon`, `name`, `address`), `excluded_locations` | **Dado Pessoal (quando `BASE` = residência do vendedor)** | **Execução de Contrato (Art. 7º, V) / Legítimo Interesse (Art. 7º, IX).** Coordenadas utilizadas estritamente em memória para cálculo viário e deduplicação espacial (`<= 80m`), sendo **proibida sua exibição em UI/PDF (`P-105`)** e vedado o envio de identificadores do titular para APIs externas. |
| **Estado de Manejo em Lote (`P-109`)** | `pendingStopsChanges`, `stagedStops`, remoção/confirmação de sugestões em memória no cliente | **Estado Efêmero de Sessão (UI Local)** | **Privacy by Default & Minimização.** O processamento em lote ocorre localmente no navegador do usuário autenticado, evitando tráfego de rede desnecessário e persistindo apenas a rota consolidada mediante ação explícita (*Opt-In* operacional). |

---

## 2. Auditoria de Privacy by Design e by Default por Regra de Negócio

### 2.1. Relatório de Inteligência das Cidades (`P-107`)
- **Validação de Dados Agregados:** Os indicadores exibidos (`population`, `demographic_density_hab_km2`, `gdp_per_capita_brl`, `city_tier` e `commercial_potential_summary`) provêm de estatísticas oficiais municipais (IBGE / catálogo municipal curado). Não há coleta, cruzamento ou inferência de perfilhamento individual (*profiling* de pessoa natural nos termos do Art. 20 da LGPD).
- **Trava de Conformidade:** O serviço `city_insights_service.py` DEVE operar estritamente sobre o nome do município e UF (`city`, `state`), sem armazenar ou vincular qualquer identificador pessoal (`userId`, `email`, `cpf` ou nome do vendedor) na tabela de cache SQLite (`city_insights_cache`).

### 2.2. Sugestão de Farmácias e Lojas de Produtos Naturais (`P-108`) e Proteção de Coordenadas (`P-105`)
- **Restrição Estrita a Pessoas Jurídicas (B2B):** A descoberta de oportunidades filtra exclusivamente tags comerciais de estabelecimentos de varejo farmacêutico e natural (`amenity=pharmacy`, `shop=chemist`, `shop=health_food`, `shop=herbalist`, `shop=nutrition_supplements`, `shop=vitamins`).
- **Veto à Coleta de PII de Proprietários ou Terceiros:** Caso metadados brutos retornados pelo OpenStreetMap (tags OSM livres como `operator`, `contact:person`, `owner`, `phone`, `email` pessoal) contenham nomes de pessoas físicas, CPFs ou contatos privados, o parser de `poi_discovery_service.py` **DEVE descartá-los imediatamente (Data Sanitization / Anti-Overfetching)**. Apenas o nome comercial do estabelecimento, a categoria comercial e o endereço logístico estruturado podem compor o DTO `StopInput` / `RouteStopDTO`.
- **Proteção da Residência do Vendedor (`P-105`):**
  1. As coordenadas geográficas (`lat`/`lon`) das sugestões e especialmente da `BASE` (residência do vendedor) são utilizadas unicamente pelo motor matemático (OSRM / Haversine / Algoritmo Genético) e pela renderização vetorial de pinos no mapa Leaflet.
  2. É **terminantemente proibido** renderizar valores numéricos de latitude e longitude nos cards de sugestões, nos cards de cidades, em tooltips textuais ou no manifesto PDF exportado (`P-105`).
  3. O filtro de deduplicação espacial (`<= 80m` de `depot`, `stops` e `excluded_locations`) impede que o endereço residencial da `BASE` do vendedor ou clientes já salvos reapareçam indevidamente como sugestões públicas.

### 2.3. Minimização e Desidentificação em Consultas a APIs Externas (Overpass / Photon / IBGE)
- **Risco Auditado:** Ao consultar APIs públicas externas (Overpass API, Photon Komoot, IBGE servicodados), o envio acidental de cabeçalhos de autenticação internos, IDs de usuário, nomes de vendedores ou rótulos como `"Minha Casa - João Silva"` configuraria vazamento de dados pessoais a terceiros internacionais.
- **Diretrizes Mandatórias de Engenharia (Desidentificação na Borda):**
  1. **Consultas Overpass / Photon:** Devem receber **exclusivamente** caixas delimitadoras ou raios numéricos desidentificados (`bounding box` / `around` com coordenadas arredondadas ao nível de corredor/bairro) ou nomes de municípios, utilizando um `User-Agent` institucional genérico da aplicação (`FitoherbRoutingService/1.0`), **jamais** repassando `Authorization` headers, cookies de sessão, `userId`, nome do vendedor ou o título (`name`) do ponto `BASE`.
  2. **Consultas IBGE:** Devem trafegar exclusivamente códigos de UF/município ou nomes de cidades públicas.
  3. **Cache Local Compartilhado e Anônimo (`osrm_cache.db`):** As tabelas SQLite de cache (`city_insights_cache` e `poi_discovery_cache`) devem utilizar chaves puramente geográficas (ex.: `city_state_key` ou `geohash/grid_cell_key`), sem qualquer coluna ou metadado de `user_id` ou titular.

### 2.4. Privacy by Default e Controle do Usuário no Manejo em Lote (`P-109`)
- **Ausência de Persistência Forçada (Opt-In Explícito):** As sugestões descobertas (`is_suggestion = true`) não são convertidas automaticamente em locais favoritos permanentes (`saved_locations`) do vendedor. Elas ingressam em estado de manejo (*staging*), permitindo ao vendedor descartar individualmente, limpar todas as sugestões em um clique ou confirmar apenas as desejadas antes de acionar **"Concluir Manejo e Recalcular Rota"**.
- **Favoritamento Deliberado:** A gravação de uma sugestão na base persistente `saved_locations` do usuário exige ação explícita e individual do vendedor (*"Salvar nos Favoritos"*), respeitando integralmente o princípio de *Privacy by Default* (2º Princípio de Cavoukian).

---

## 3. Avaliação de Gatilho de RIPD / DPIA

Conforme diretriz da Governança de Privacidade:
1. **Há tratamento de dados pessoais sensíveis (Art. 5º, II - saúde, biometria, religião, etc.)?** **NÃO.** Embora o domínio comercial envolva farmácias e lojas de produtos naturais, os dados referem-se exclusivamente a estabelecimentos comerciais (CNPJs/POIs públicos) e estatísticas demográficas do IBGE, sem dados clínicos ou de saúde de pessoas físicas.
2. **Há decisão automatizada por IA que afete direitos individuais de titulares (Art. 20 LGPD)?** **NÃO.** O algoritmo genético e o motor de descoberta de POIs geram apenas recomendações logísticas B2B submetidas à revisão e aprovação humana em lote pelo vendedor (`P-109`).

> **Conclusão sobre RIPD:** Não há necessidade de abertura de RIPD/DPIA de alto risco para esta feature, bastando o cumprimento integral das salvaguardas técnicas estabelecidas neste parecer.

---

## 4. Checklist Obrigatório para a Etapa 3 (Desenvolvimento) e Etapa 4 (Code Review LGPD)

Para aprovação no Quality Gate 360 (Etapa 4), os desenvolvedores e revisores devem assegurar:

- [ ] **Sanitização de POIs (`fitoherb-ai`):** O serviço `poi_discovery_service.py` extrai apenas nome comercial, categoria (`FARMACIA` / `PRODUTOS_NATURAIS`), endereço público estruturado e coordenadas para roteamento, ignorando quaisquer tags OSM que possam conter nomes de pessoas físicas, telefones pessoais ou e-mails privados.
- [ ] **Isolamento de Identidade em Chamadas Externas (`fitoherb-ai`):** Nenhuma chamada HTTP para IBGE, Overpass ou Photon inclui dados do vendedor (`userId`, `email`, `name` da `BASE` ou tokens JWT).
- [ ] **Ocultação Absoluta de Coordenadas (`fitoherb-ai` + `fitoherb-frontend-v2`):** Nem os cards de cidades (`P-107`), nem os itens de sugestão (`P-108`), nem o relatório PDF (`P-105`) exibem valores de `lat` ou `lon` em texto para o usuário.
- [ ] **Zero PII em Logs (`fitoherb-ai` + `fitoherb-backend-v2`):** Logs de descoberta de POIs e enriquecimento de cidades registram apenas contagens agregadas e nomes de municípios (ex.: `logger.info("Descobertos %d POIs em %s/%s", count, city, state)`), sem logar o endereço residencial da `BASE` do vendedor.
- [ ] **Isolamento Multi-Tenant (`fitoherb-backend-v2`):** Ao salvar uma sugestão como favorito (`saved_locations`) ou persistir a rota após o manejo em lote (`scheduled_routes`), o vínculo permanece estritamente escopado ao `userId` extraído do token JWT autenticado.
