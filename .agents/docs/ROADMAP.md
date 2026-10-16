# Roadmap do Projeto 🗺️

> **Localização Mandatória:** `.agents/docs/ROADMAP.md`  
> **Responsável:** Product Owner (`product_owner.md`) / `agile-coach`

---

## 1. Visão do Produto
O ecossistema Fitoherb disponibiliza uma plataforma completa para distribuidores e consumidores de produtos fitoterápicos, suplementos e cosméticos. O Assistente Virtual Inteligente (Chatbot Gemini) atua como o ponto de atendimento automatizado em tempo real no website institucional e catálogo, sanando dúvidas institucionais, divulgando canais digitais oficiais (WhatsApp e Instagram), localizando produtos no catálogo sem viés de marca e direcionando fluidamente a navegação do usuário.

---

## 2. Épicos e User Stories (Backlog)

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
- [x] **Épico 1:** Roteirização Comercial Inteligente (Algoritmo Genético TDVRP com Trava de Ordem e Tráfego Preditivo).
- [x] **Épico 2:** Assistente Virtual Inteligente Fitoherb (Chat Gemini com Redirecionamento, Tokenomics e Treinamento de Redes Sociais `P-312`).
