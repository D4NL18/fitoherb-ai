# Roadmap do Projeto 🗺️

> **Localização Mandatória:** `.agents/docs/ROADMAP.md`  
> **Responsável:** Product Owner (`product_owner.md`) / `agile-coach`

---

## 1. Visão do Produto
O ecossistema Fitoherb disponibiliza uma plataforma completa para distribuidores, equipe comercial e consumidores de produtos fitoterápicos, suplementos e cosméticos:
1. **Roteirização Comercial Inteligente (TDVRP + Inteligência Territorial e Leads):** Otimização de rotas de vendedores com Algoritmo Genético, previsão de tráfego por faixa horária/porte urbano, relatório demográfico e comercial das cidades visitadas e descoberta proativa de novas farmácias e lojas de produtos naturais no trajeto com curadoria em lote.
2. **Assistente Virtual Inteligente (Chatbot Gemini):** Ponto de atendimento automatizado em tempo real no website institucional e catálogo, sanando dúvidas institucionais com 0 tokens, divulgando canais digitais oficiais (WhatsApp e Instagram), localizando produtos no catálogo sem viés de marca e direcionando fluidamente a navegação do usuário.
3. **Governança de Catálogo & Integração ERP Atrio (`P-400+`):** Garantia de rastreabilidade integral entre o catálogo público/administrativo do site e o ERP Atrio (`FITOHERB`), com obrigatoriedade e validação de código `Id_Pro` por SKU (sabores × apresentações), busca/importação em lote no painel admin e saneamento/mapeamento zero-chutes do legado.

---

## 2. Épicos e User Stories (Backlog)

### Épico 1: Roteirização Comercial Inteligente (Evolução: Inteligência Demográfica por Cidade e Descoberta Proativa de Leads)

- [ ] **US-R1: Relatório de Inteligência Demográfica e Comercial por Cidade na Rota** `[PARALLEL]`
  - **Declaração INVEST:** Como vendedor comercial da Fitoherb, quero visualizar, ao prever uma rota, um relatório executivo das cidades que possuem pontos salvos/planejados na rota com informações demográficas e comerciais úteis (população estimada, porte urbano, PIB per capita / renda média estimada, potencial de consumo farma/natural, vocação econômica, total de paradas e tempo de permanência na cidade), para preparar melhor minha estratégia de vendas em cada município.
  - **Priorização RICE:** Reach: 100% das rotas previstas | Impact: Alto (2.5/3) | Confidence: 100% | Effort: Baixo (1 turno) ➔ **RICE Score: 250**.
  - **Critérios de Aceite (BDD):**
    - **Dado** que o vendedor prevê/otimiza (`POST /api/v1/routing/optimize`) ou recalcula (`POST /api/v1/routing/recalculate`) uma rota com paradas válidas, **Quando** a rota é processada, **Então** o payload de resposta retorna `city_insights` contendo o resumo estruturado de cada cidade distinta presente nas paradas de visita (na ordem cronológica de passagem da rota).
    - **Dado** cada cidade no relatório `city_insights`, **Quando** renderizada na aba de resultados da rota no Frontend, **Então** exibe: nome da cidade/UF, população estimada (IBGE), classificação de porte urbano (`METROPOLIS`, `REGIONAL_HUB`, `MEDIUM_CITY`, `SMALL_TOWN`), PIB per capita / renda média estimada, vocação econômica principal, índice de potencial comercial para fitoterápicos/suplementos, quantidade de paradas na cidade e tempo total de atendimento/permanência local.
    - **Dado** que uma cidade da rota não conste no catálogo demográfico primário, **Quando** o relatório é gerado, **Então** utiliza estimativa regional/fallback sem falhar ou bloquear o cálculo da rota.
  - **Tarefas Técnicas:** `.agents/docs/tasks/commercial_routing_city_and_suggestions.md` (Trilha Backend AI + Frontend)

- [ ] **US-R2: Descoberta Proativa de Leads — Sugestão de Farmácias e Lojas de Produtos Naturais no Trajeto** `[PARALLEL]`
  - **Declaração INVEST:** Como vendedor comercial da Fitoherb, quero que o sistema sugira novas farmácias, drogarias, farmácias de manipulação e lojas de produtos naturais/suplementos situadas nas proximidades das paradas ou do corredor da rota que ainda não estão na minha lista de pontos, para descobrir novos clientes potenciais e visitá-los aproveitando a viagem.
  - **Priorização RICE:** Reach: 100% das rotas planejadas | Impact: Muito Alto (3.0/3) | Confidence: 90% | Effort: Médio (1.5 turnos) ➔ **RICE Score: 180**.
  - **Critérios de Aceite (BDD):**
    - **Dado** uma rota prevista com coordenadas de paradas e cidades definidas, **Quando** o serviço de sugestões de pontos de interesse (`suggested_pois` / endpoint de descoberta no corredor da rota) é executado, **Então** retorna estabelecimentos das categorias **Farmácia/Drogaria** e **Loja de Produtos Naturais/Suplementos** próximos às paradas/trajeto.
    - **Dado** a lista bruta de estabelecimentos encontrados na região da rota, **Quando** o filtro de deduplicação é aplicado, **Então** nenhum ponto já presente nas paradas atuais da rota (`stops`) ou nos locais salvos (`savedLocations`) é sugerido novamente (deduplicação por raio geodésico $\le 80\text{m}$ ou nome normalizado + endereço).
    - **Dado** cada estabelecimento sugerido, **Quando** apresentado ao vendedor na UI e no mapa, **Então** exibe Nome, Categoria (*Farmácia* ou *Produtos Naturais*), Endereço legível, distância/desvio estimado em relação à parada mais próxima (`detour_km`) e botões rápidos de **"Adicionar à Lista"** ou **"Descartar Sugestão"**.
  - **Tarefas Técnicas:** `.agents/docs/tasks/commercial_routing_city_and_suggestions.md` (Trilha Backend AI + Frontend)

- [ ] **US-R3: Curadoria em Lote da Lista de Sugestões e Paradas com Recálculo Diferido ao Final**
  - **Declaração INVEST:** Como vendedor comercial da Fitoherb, quero adicionar sugestões de novas lojas à minha lista de paradas e remover pontos da lista livremente, sem que a rota seja recalculada a cada alteração individual, disparando o recálculo/otimização somente após terminar de manejar a lista, para garantir agilidade e fluidez na montagem do roteiro.
  - **Priorização RICE:** Reach: 100% dos usuários da tela de rotas | Impact: Muito Alto (3.0/3) | Confidence: 100% | Effort: Baixo (1 turno) ➔ **RICE Score: 300**.
  - **Critérios de Aceite (BDD):**
    - **Dado** que o vendedor está visualizando as sugestões de novas farmácias/lojas naturais e a lista de paradas da rota, **Quando** ele adiciona uma sugestão à rota ou remove uma parada existente da lista, **Então** a alteração é aplicada imediatamente na lista em memória (`stops` / `suggestedPois`), marcando o estado como pendente de recálculo (`hasPendingChanges = true`), **sem** chamar `/optimize` ou `/recalculate` automaticamente.
    - **Dado** que uma sugestão foi adicionada à lista de paradas, **Quando** a lista é atualizada na tela, **Então** o item deixa a lista de sugestões ativas e passa a figurar na lista de paradas com badge indicativo de *"Novo / Sugerido"* (ou é descartado se o usuário clicar em remover da lista de sugestões).
    - **Dado** que existem alterações pendentes na lista de paradas (adições de sugestões e/ou remoções de pontos), **Quando** o vendedor finaliza o manejo e clica explicitamente em **"Recalcular Rota"** (ou **"Aplicar Alterações e Recalcular"**), **Então** o sistema realiza uma única chamada de otimização/recálculo contemplando todas as inclusões e exclusões, atualizando mapa, horários, métricas e relatório de cidades.
  - **Tarefas Técnicas:** `.agents/docs/tasks/commercial_routing_city_and_suggestions.md` (Trilha Frontend)

---

### Épico 2: Assistente Virtual Inteligente (Chat Gemini)
- [x] **US-C1: Acesso ao Chat Flutuante e Interface Responsiva** `[PARALLEL]`
  - **Critérios de Aceite:**
    - Botão flutuante (FAB) visível no canto inferior direito das páginas públicas (oculto em `/login` e `/admin`).
    - Janela/modal de chat abre e fecha mantendo a conversa sem perda de contexto visual.
    - Suporte a acessibilidade (fechamento com `Esc`, foco adequado, `aria-label`).
    - Campo de entrada com trava dura de 255 caracteres e contador visível.
  - **Tarefas Técnicas:** `.agents/docs/tasks/chatbot_assistant.md` (Trilha Front-end)

- [x] **US-C2: Dúvidas Institucionais sem Consumo de Tokens** `[PARALLEL]`
  - **Critérios de Aceite:**
    - Perguntas sobre localização, telefone, WhatsApp, Instagram, redes sociais, e-mail e quem somos são respondidas instantaneamente via templates da base de conhecimento com 0 tokens de LLM.
    - Se a informação solicitada não existir na base de conhecimento, o assistente responde honestamente que não possui a informação e convida a falar com o comercial.
  - **Tarefas Técnicas:** `.agents/docs/tasks/chatbot_assistant.md` (Trilha AI)

- [x] **US-C3: Busca e Consulta Neutra de Produtos do Catálogo** `[PARALLEL]`
  - **Critérios de Aceite:**
    - Consulta de produtos indexa todo o catálogo (nome, categoria, fornecedor, sabores, apresentação, descrição).
    - Tratamento estritamente equânime entre fornecedores e marcas, sem preferência, publicidade ou ranking patrocinado.
    - Recusa expressa de responder sobre preços, estoque em tempo real ou tabela nutricional detalhada, orientando contato com o setor comercial.
    - Recusa imediata de aconselhamento médico, posologia ou prescrição terapêutica.
  - **Tarefas Técnicas:** `.agents/docs/tasks/chatbot_assistant.md` (Trilha AI + Backend)

- [x] **US-C4: Redirecionamento Automático com Filtros no Catálogo** `[PARALLEL]`
  - **Critérios de Aceite:**
    - Ao identificar a busca/listagem por produtos (ex: "quais as opções de whey 100%"), o sistema redireciona automaticamente o usuário para a tela `/produtos` aplicando os filtros (`category`, `supplier` e `search`) na URL.
    - O chat permanece aberto durante a navegação, exibindo a resposta explicativa concisa.
    - A tela de galeria consome os parâmetros da URL sem requisições redundantes.
  - **Tarefas Técnicas:** `.agents/docs/tasks/chatbot_assistant.md` (Trilha Front-end + AI)

- [x] **US-C5: Otimização de Tokens, Prompt Caching e Compactação** `[PARALLEL]`
  - **Critérios de Aceite:**
    - Roteador semântico de intenções com bypass de LLM para saudações e dados institucionais.
    - Resolução dinâmica da versão mais recente estável do modelo Gemini Flash (`gemini-2.5-flash` / alias estável).
    - Compactação de histórico automática a partir de 5 mensagens.
    - Limite estrito de tokens de saída para gerar respostas curtas, diretas e simples (sem vocabulário rebuscado ou travessões no meio de orações).
    - Cache L1 em memória com SHA-256 e TTL.
  - **Tarefas Técnicas:** `.agents/docs/tasks/chatbot_assistant.md` (Trilha AI)

- [x] **US-C6: Atendimento de Redes Sociais e Canais Digitais (WhatsApp e Instagram)** `[PARALLEL]`
  - **Declaração INVEST:** Como visitante ou cliente da Fitoherb, quero perguntar ao chatbot sobre as redes sociais, Instagram ou WhatsApp da empresa para obter rapidamente os links e contatos oficiais de atendimento e acompanhamento digital.
  - **Priorização RICE:** Reach: 100% dos usuários do chat | Impact: Alto (conversão direta para WhatsApp/Instagram) | Confidence: 100% | Effort: Baixo (1 turno).
  - **Critérios de Aceite (BDD):**
    - **Dado** que o usuário pergunta sobre redes sociais, Instagram ou WhatsApp (ex.: *"qual o instagram?"*, *"tem zap?"*, *"quais as redes sociais da fitoherb?"*), **Quando** a mensagem é processada pelo `IntentRouter`, **Então** o sistema responde instantaneamente com **0 tokens de LLM**, informando o WhatsApp oficial `(71) 99241-9709` (`https://wa.me/5571992419709`) e o Instagram oficial `@fitoherb` (`https://www.instagram.com/fitoherb`).
    - **Dado** o arquivo `company_profile.yaml`, **Quando** carregado na inicialização do microsserviço de IA, **Então** deve conter os campos estruturados de WhatsApp (`(71) 99241-9709` / `https://wa.me/5571992419709`) e Instagram (`@fitoherb` / `https://www.instagram.com/fitoherb`) sincronizados com o rodapé institucional (`footer.component.html`).
    - **Dado** que o usuário envia uma pergunta composta sobre produtos combinada com pedido de contato ou rede social que seja encaminhada ao Gemini, **Quando** o prompt de sistema do `ChatOrchestrator` é montado, **Então** o modelo inclui o conhecimento do WhatsApp e Instagram oficiais e utiliza esses canais também nos convites de contato comercial.
  - **Tarefas Técnicas:** `.agents/docs/tasks/chatbot_assistant.md` (Trilha AI)

---

### Épico 3: Governança de Catálogo — Códigos ERP por SKU (Sabores/Apresentações), Saneamento Prod → Local e Sincronização Diária (`P-400+`)
- **Objetivo de Valor:** Eliminar produtos órfãos sem código do ERP Atrio, estruturar o vínculo 1:1 de códigos `Id_Pro` para cada sabor/apresentação (SKU), acelerar o cadastro administrativo via importação em lote do ERP, construir uma base local fiel a partir do clone de produção sem suposições ("zero chutes") e manter a vitrine pública e o Chatbot sincronizados diariamente com o status ativo/inativo do ERP — incluindo publicação imediata de recém-ativados (mesmo sem foto) e alerta de curadoria rápida ao entrar no painel administrativo.
- **Abordagem de Execução:** Híbrida (PMBOK 7) — preditiva na curadoria do legado, preservação do catálogo público, controle de baseline e estratégia de rollout; ágil adaptativa nas fatias verticais por valor (`US-P1` a `US-P8`).
- **Outcome Roadmap:** *Now (Onda 1):* `US-P1`, `US-P2` · *Now (Onda 2):* `US-P3`, `US-P4`, `US-P5` · *Next (Onda 3):* `US-P6` · *Next (Onda 4 — Automação Contínua Pós-Baseline):* `US-P7`, `US-P8`.
- **Matriz de Riscos Principais:**
  - *Conectividade Cloud Run → SQL Server 2008 R2 on-premise:* Prob. Alta / Impacto Alto -> Estratégia Mitigar: consulta somente-leitura via `ErpCatalogGateway` (`jtds:1.3.1` `ssl=off`) + cache RAM, sem espelho permanente no PostgreSQL (`A1`).
  - *Trava rígida antes do backfill dos legados (`1.032` produtos no clone prod):* Prob. Média / Impacto Alto -> Estratégia Mitigar: backfill e curadoria local (`US-P1`) + script idempotente (`US-P6`) antes de constraint `NOT NULL` em produção.
  - *Mapeamento ambíguo ou vínculo com SKU inativo (`inativo_pro = 1`):* Prob. Média / Impacto Alto -> Estratégia Mitigar: política zero-chutes com pesquisa web, lista `INACTIVE_MATCH_ALERTS` e fila de confirmação humana.
  - *Regressão no `CatalogIndex` (`fitoherb-ai`) ou vitrine pública:* Prob. Média / Impacto Alto -> Estratégia Mitigar: manutenção de listas distintas saneadas em `ProductRes`, filtro `active = true` e validação dedicada (`US-P5`, `US-P7`).
  - *Cloud Run Scale-to-Zero impedindo disparo do `@Scheduled` diário:* Prob. Alta / Impacto Alto -> Estratégia Evitar/Mitigar: suportar disparo dual — `@Scheduled` interno (já habilitado) + endpoint/gatilho externo idempotente autenticado (Cloud Scheduler / GitHub Actions cron diário) mantendo FinOps Scale-to-Zero.
  - *Flood de itens históricos do ERP não vendidos no site vs. Baseline (`1.653` ativos no ERP vs. `1.032` no site):* Prob. Alta / Impacto Alto -> Estratégia Evitar: exigir política explícita de baseline na virada pós-`US-P1` e critérios de elegibilidade antes de ativar criação automática em `US-P7`.
  - *`category_id` (6 categorias) e `supplier_id` (44 fornecedores) obrigatórios para produto novo nascido no ERP antes da curadoria:* Prob. Alta / Impacto Médio -> Estratégia Mitigar: definir mapeamento determinístico / fallback padrão na Etapa 2 e destacar revisão de categoria/fornecedor junto com a foto no modal pré-preenchido (`US-P8`).
  - *Conflito semântico com regra anterior `P-406` (`A2`) e inativação parcial Multi-SKU:* Prob. Média / Impacto Alto -> Estratégia Mitigar: conciliar `P-406` na Etapa 1 distinguindo exclusão lógica (`active = false`, sem apagar vínculo/foto) de deleção física, e definir regra explícita para produtos Multi-SKU com variação parcialmente inativa.
  - *Dessincronização do `CatalogIndex` em RAM (`fitoherb-ai`) e colisão de `slug` / nomes abreviados do ERP:* Prob. Média / Impacto Médio -> Estratégia Mitigar: recarga/invalidação do `CatalogIndex` pós-sync diário, geração de `slug` único sem colisão (`P-009`) e revisão rápida em `US-P8`.
- **Histórias de Usuário (INVEST):**

- [ ] **US-P1: Clonagem Prod → Local, Saneamento de Variações Legadas e Mapeamento Assistido Site × ERP (Zero Chutes)** `[PARALLEL]`
  - **Declaração INVEST:** Como administrador de catálogo da Fitoherb, quero clonar o banco de produção (via `backup.yml`) para o banco local `fitoherb-v2`, limpar variações concatenadas (`" e "` e ponto final `.`) e mapear os 1.040 produtos existentes contra o ERP Atrio com pesquisa web e confirmação humana em qualquer dúvida, para ter uma base local fidedigna sem códigos inventados.
  - **Priorização RICE:** Reach: 100% dos 1.040 produtos legados | Impact: Muito Alto (3.0/3) | Confidence: 90% | Effort: Alto (2.5 turnos) ➔ **RICE Score: 108** *(Pré-requisito de dados; fase de clone/saneamento/matching inicial paralelizável).*
  - **Critérios de Aceite (BDD):**
    - **Dado** o dump de produção gerado por `backup.yml`, **Quando** restaurado no PostgreSQL local `fitoherb-v2`, **Então** os 1.040 produtos, 6 categorias e 44 fornecedores ficam disponíveis localmente sem alterar produção.
    - **Dado** registros legados com concatenações (ex.: `{"Baunilha","Chocolate e Morango."}`, `{"25ml e 60ml."}`), **Quando** o saneamento é aplicado, **Então** os valores são desmembrados em variações atômicas limpas.
    - **Dado** os produtos do site comparados a `[dbo].[Produtos]` e `[Externo01].[Produto]` do ERP Atrio, **Quando** houver match inequívoco, **Então** o `Id_Pro` é pré-vinculado; **Quando** persistir dúvida após pesquisa externa na web, **Então** nenhum código é chutado e o item entra em fila de decisão com o usuário.
  - **Tarefas Técnicas:** `.agents/docs/tasks/product_code_mapping_flavors.md` (Trilha Dados / Backend)

- [ ] **US-P2: Obrigatoriedade, Validação contra o ERP Atrio e Exibição Admin do Código ERP (Produto Simples — MVP Core)** `[PARALLEL]`
  - **Declaração INVEST:** Como operador administrativo, quero que o cadastro e a edição de produtos simples exijam um código `Id_Pro` válido no ERP Atrio e que esse código seja visível e pesquisável na listagem administrativa, para garantir rastreabilidade desde a entrada do produto.
  - **Priorização RICE:** Reach: 100% dos cadastros/edições e 83% do catálogo (865 simples) | Impact: Muito Alto (3.0/3) | Confidence: 95% | Effort: Médio (1.5 turnos) ➔ **RICE Score: 190**.
  - **Critérios de Aceite (BDD):**
    - **Dado** o formulário administrativo de criação/edição (`ModalEntityComponent`) de um produto sem variações, **Quando** submetido sem código ERP ou com código inexistente no ERP Atrio, **Então** a operação é bloqueada com feedback claro no backend e na UI.
    - **Dado** um código `Id_Pro` válido no ERP Atrio, **Quando** salvo, **Então** o vínculo é persistido no banco e exibido/filtrável na tabela `Produtos` (`adminProducts`).
  - **Tarefas Técnicas:** `.agents/docs/tasks/product_code_mapping_flavors.md` (Trilha Backend + Frontend)

- [ ] **US-P3: Gestão de Códigos ERP por Sabor e Apresentação (Matriz SKU × Variações)**
  - **Declaração INVEST:** Como operador administrativo, quero gerenciar sabores e/ou apresentações de forma estruturada onde cada variação ativa possua seu código `Id_Pro` validado no ERP, para representar corretamente produtos multi-SKU (ex.: `100% Pure Whey 900g`, `B.O.P.E` 150g/300g × 3 sabores, `Stevita Líquido` 25ml/60ml).
  - **Priorização RICE:** Reach: 70 (175 legados multi-SKU + lançamentos com variações) | Impact: Muito Alto (3.0/3) | Confidence: 90% | Effort: Médio-Alto (2.0 turnos) ➔ **RICE Score: 95**.
  - **Critérios de Aceite (BDD):**
    - **Dado** um produto com apenas sabores, apenas apresentações ou matriz sabor × apresentação, **Quando** configurado no modal administrativo, **Então** cada SKU ativo exige seu código `Id_Pro` válido e único no catálogo.
    - **Dado** um produto multi-SKU salvo com combinações repetidas por eixo (ex.: 2 apresentações × 3 sabores), **Quando** retornado para consumo público (`ProductRes`), **Então** `flavours` e `presentation` permanecem sem duplicatas.
  - **Tarefas Técnicas:** `.agents/docs/tasks/product_code_mapping_flavors.md` (Trilha Backend + Frontend)

- [ ] **US-P4: Busca Direta e Importação em Lote de Variações do ERP Atrio no Painel Admin**
  - **Declaração INVEST:** Como operador administrativo, quero pesquisar produtos do ERP Atrio dentro do modal do site e importar múltiplos SKUs selecionados em lote, para preencher automaticamente códigos `Id_Pro`, sabores e apresentações com agilidade e segurança.
  - **Priorização RICE:** Reach: 80% das operações de catálogo no admin | Impact: Muito Alto (2.8/3) | Confidence: 90% | Effort: Médio (1.5 turnos) ➔ **RICE Score: 134**.
  - **Critérios de Aceite (BDD):**
    - **Dado** o modal administrativo de produto, **Quando** o operador busca por nome, código `Id_Pro`, EAN ou marca no ERP, **Então** são exibidos os SKUs encontrados com código, descrição, fornecedor e indicador de ativo/inativo.
    - **Dado** múltiplos SKUs selecionados na busca ERP, **Quando** o operador confirma a importação em lote, **Então** a grade de variações é populada automaticamente com os respectivos códigos `Id_Pro`, sabores e apresentações sugeridos para revisão antes de salvar.
  - **Tarefas Técnicas:** `.agents/docs/tasks/product_code_mapping_flavors.md` (Trilha Backend + Frontend)

- [ ] **US-P5: Compatibilidade e Saneamento na Vitrine Pública e no `CatalogIndex` (`fitoherb-ai`)** `[PARALLEL]`
  - **Declaração INVEST:** Como cliente ou usuário do Chatbot da Fitoherb, quero visualizar sabores e apresentações limpos na vitrine pública e obter recomendações neutras e precisas no assistente virtual após a adoção de SKUs e códigos ERP, para evitar regressões na experiência de consulta.
  - **Priorização RICE:** Reach: 100% dos visitantes públicos e usuários do chat | Impact: Alto (2.0/3) | Confidence: 95% | Effort: Baixo (1.0 turno) ➔ **RICE Score: 190**.
  - **Critérios de Aceite (BDD):**
    - **Dado** o catálogo atualizado no PostgreSQL `fitoherb-v2`, **Quando** o `CatalogIndex` do `fitoherb-ai` recarrega os produtos, **Então** indexa corretamente nome, categoria, fornecedor, `flavours` e `presentation` saneados mantendo as regras `P-302`, `P-304` e `P-305`.
    - **Dado** a vitrine pública (`ItemCardGalleryComponent` e `ModalGalleryComponent`), **Quando** o usuário abre o catálogo e os detalhes do produto, **Então** os chips de sabor e apresentação são exibidos sem duplicatas nem pontuações legadas.
  - **Tarefas Técnicas:** `.agents/docs/tasks/product_code_mapping_flavors.md` (Trilha AI + Frontend)

- [ ] **US-P6: Filtro Admin de Pendências ERP e Governança de Rollout Seguro para Produção** `[PARALLEL]`
  - **Declaração INVEST:** Como administrador responsável pela operação, quero filtrar na tabela administrativa os produtos sem código ERP ou com alerta de inatividade na tabela e dispor de um pacote idempotente de migração pós-curadoria, para promover a mudança em produção sem paralisar edições do catálogo.
  - **Priorização RICE:** Reach: 100% da transição operacional em produção | Impact: Alto (2.5/3) | Confidence: 90% | Effort: Médio (1.5 turnos) ➔ **RICE Score: 150**.
  - **Critérios de Aceite (BDD):**
    - **Dado** a listagem administrativa `Produtos`, **Quando** aplicado filtro de status ERP (*Sem Código*, *Completo*, *Com Alerta Inativo no ERP*), **Então** apenas os produtos compatíveis são exibidos com badge indicativa.
    - **Dado** o mapeamento curado e validado localmente (`US-P1`), **Quando** o artefato de migração idempotente é gerado, **Então** pode ser aplicado no banco alvo sem sobrescrever vínculos já confirmados nem quebrar integridade referencial.
  - **Tarefas Técnicas:** `.agents/docs/tasks/product_code_mapping_flavors.md` (Trilha Backend + Frontend + Dados)

- [ ] **US-P7: Sincronização Diária Agendada de Status Ativo/Inativo ERP ↔ Site, Publicação Imediata (Inclusive Sem Foto) e Ocultação na Vitrine/IA** `[PARALLEL]`
  - **Declaração INVEST:** Como administrador e equipe comercial da Fitoherb, quero que um agendamento diário sincronize automaticamente os produtos ativos e inativos do ERP Atrio com o banco do sistema, ocultando da vitrine pública e do Chatbot produtos inativados e publicando imediatamente produtos que se tornaram ativos (mesmo sem foto), para manter o catálogo público fiel à operação diária sem intervenção manual.
  - **Priorização RICE:** Reach: 100% do catálogo sincronizado, vitrine pública (`/produtos`) e Chatbot (`fitoherb-ai`) | Impact: Muito Alto (3.0/3) | Confidence: 85% | Effort: Médio-Alto (2.0 turnos) ➔ **RICE Score: 128** *(`[PARALLEL]` no serviço agendado + recarregamento/filtros vitrine e `CatalogIndex`; depende de baseline e regras fechadas na Etapa 1/2).*
  - **Critérios de Aceite (BDD):**
    - **Dado** o agendamento diário configurado no backend (suportando tanto `@Scheduled` interno quanto gatilho externo autenticado para Cloud Run Scale-to-Zero), **Quando** a sincronização diária executa contra o SQL Server somente-leitura do ERP Atrio (`Empresa_Pro = 1`, sem espelho completo permanente no PostgreSQL `A1` e sem extrair PII, Estoque ou Preços), **Então** avalia `inativo_pro` (`0` = ativo, `1` = inativo) respeitando o controle de baseline para evitar inundar o catálogo com itens históricos nunca vendidos no site.
    - **Dado** um produto mapeado no site cujo código ERP (ou todos os seus SKUs vinculados) passa a `inativo_pro = 1` no ERP Atrio, **Quando** a sincronização diária é concluída, **Então** o produto é marcado com exclusão lógica (`active = false`, preservando cadastro, imagem e vínculo `product_skus` para eventual reativação futura) e deixa imediatamente de ser exibido em `GET /products/gallery` e no `CatalogIndex` do `fitoherb-ai`.
    - **Dado** um produto previamente inativado no site ou um item elegível que se torna ativo (`inativo_pro = 0`) no ERP, **Quando** a sincronização diária é processada, **Então** o produto passa a `active = true` e é publicado imediatamente na vitrine pública e no `CatalogIndex` **mesmo que `imageUrl` seja `null`** (usando o fallback visual `assets/images/fitoherb-leaf-icon.png` no `ItemCardGalleryComponent`), sem expor `Id_Pro`, `inativo_pro` ou `Estoque` ao público (`P-408`) e registrando pendência de curadoria para `US-P8` se estiver sem imagem/revisão.
    - **Dado** alterações de visibilidade/novos produtos aplicadas pela sincronização diária, **Quando** o ciclo diário finaliza, **Então** o `CatalogIndex` (`fitoherb-ai`) recarrega/filtra apenas produtos `active = true` e a execução fica registrada de forma idempotente sem duplicar registros em reexecuções no mesmo dia.
  - **Tarefas Técnicas:** `.agents/docs/tasks/product_code_mapping_flavors.md` (Trilha Backend Agendador/Sync + Trilha Vitrine/AI `[PARALLEL]`)

- [ ] **US-P8: Painel de Curadoria Rápida ao Entrar no Admin (`USER` e `ADMIN`) — Lista de Novos Produtos Pendentes de Imagem com Modal Pré-Preenchido** `[PARALLEL]`
  - **Declaração INVEST:** Como usuário administrativo (`ROLE_USER` ou `ROLE_ADMIN`) da Fitoherb, quero que o painel `/admin` sinalize logo ao entrar uma lista dos novos produtos ativos vindos da sincronização que ainda aguardam foto/revisão e que, ao clicar em um item, abra o modal de produto já pré-preenchido com suas informações e código ERP, para concluir o cadastro rapidamente apenas enviando a imagem e conferindo categoria/nome.
  - **Priorização RICE:** Reach: 100% dos operadores `ROLE_USER` e `ROLE_ADMIN` no `/admin` | Impact: Alto (2.5/3) | Confidence: 90% | Effort: Médio (1.5 turnos) ➔ **RICE Score: 150** *(`[PARALLEL]` entre endpoint Backend de pendências e UI Frontend no `/admin` + `ModalEntityComponent`).*
  - **Critérios de Aceite (BDD):**
    - **Dado** que um usuário autenticado com perfil `ROLE_USER` ou `ROLE_ADMIN` acessa o painel `/admin` (ou aba `Produtos`) e há novos produtos ativos pendentes de imagem/revisão gerados pela sincronização, **Quando** o painel carrega, **Então** exibe um sinalizador/lista de curadoria rápida com os itens pendentes (nome, código `Id_Pro`, fornecedor/marca e badge `"Sem foto"` / `"Novo do ERP"`); caso não haja pendências, o aviso não polui a tela; usuários `ROLE_SELLER` ou não autenticados não veem o aviso e recebem `403`/`401` nos endpoints.
    - **Dado** a lista de novos produtos pendentes exibida no `/admin`, **Quando** o usuário `ROLE_USER` ou `ROLE_ADMIN` clica em um produto da lista, **Então** o modal administrativo (`ModalEntityComponent`) abre imediatamente pré-preenchido com nome, descrição sugerida, categoria, fornecedor e grade `skus[]` contendo o `Id_Pro` vinculado, destacando a área de upload de imagem (`"Selecionar / Alterar Imagem"`) para preenchimento rápido.
    - **Dado** o modal pré-preenchido aberto a partir da lista de pendências, **Quando** o operador adiciona a imagem (podendo ajustar nome, categoria, fornecedor ou variações) e salva com sucesso, **Então** a imagem é persistida e passa a aparecer na vitrine pública, e o produto sai automaticamente da lista de novos produtos pendentes atualizando o contador no `/admin`.
    - **Dado** que o operador avalie um item recém-sincronizado que não deva permanecer no site ou já tenha sido revisado conforme regra definida na Etapa 1/2, **Quando** aciona a conclusão/descarte na interface de curadoria rápida, **Então** o item deixa a lista de avisos de forma auditável sem reaparecer indevidamente no próximo ciclo diário.
  - **Tarefas Técnicas:** `.agents/docs/tasks/product_code_mapping_flavors.md` (Trilha Backend Endpoint + Trilha Frontend UI `[PARALLEL]`)

---

## 3. Histórico de Entregas
- [x] **Épico 1 (Fase 1):** Roteirização Comercial Inteligente (Algoritmo Genético TDVRP com Trava de Ordem, Tráfego Preditivo, Calendário de Rotas e Exportação PDF).
- [x] **Épico 2:** Assistente Virtual Inteligente Fitoherb (Chat Gemini com Redirecionamento, Tokenomics e Treinamento de Redes Sociais `P-312`).
