# Roadmap do Projeto 🗺️

> **Localização Mandatória:** `.agents/docs/ROADMAP.md`  
> **Responsável:** Product Owner (`product_owner.md`) / `agile-coach`

---

## 1. Visão do Produto
O ecossistema Fitoherb disponibiliza uma plataforma completa para distribuidores, equipe comercial e consumidores de produtos fitoterápicos, suplementos e cosméticos:
1. **Roteirização Comercial Inteligente (TDVRP + Inteligência Territorial e Leads):** Otimização de rotas de vendedores com Algoritmo Genético, previsão de tráfego por faixa horária/porte urbano, relatório demográfico e comercial das cidades visitadas e descoberta proativa de novas farmácias e lojas de produtos naturais no trajeto com curadoria em lote.
2. **Assistente Virtual Inteligente (Chatbot Gemini):** Ponto de atendimento automatizado em tempo real no website institucional e catálogo, sanando dúvidas institucionais com 0 tokens, divulgando canais digitais oficiais (WhatsApp e Instagram), localizando produtos no catálogo sem viés de marca e direcionando fluidamente a navegação do usuário.

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

## 3. Histórico de Entregas
- [x] **Épico 1 (Fase 1):** Roteirização Comercial Inteligente (Algoritmo Genético TDVRP com Trava de Ordem, Tráfego Preditivo, Calendário de Rotas e Exportação PDF).
- [x] **Épico 2:** Assistente Virtual Inteligente Fitoherb (Chat Gemini com Redirecionamento, Tokenomics e Treinamento de Redes Sociais `P-312`).
