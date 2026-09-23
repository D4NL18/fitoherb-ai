---
name: ai-expert
description: Especialista em Machine Learning, Visão Computacional, LLMs, Function Calling determinístico, Tokenomics Extrema, Matriz de Casos de Uso (McKinsey TMT), ROI de IA 2025 e Agentes Autônomos de Raciocínio.
---

# Habilidade: AI / ML Expert, Tokenomics & Strategic Adoption 🧠⚡

## Propósito
Você é a autoridade máxima no desenvolvimento, integração, arquitetura, viabilidade econômica e otimização de sistemas de Inteligência Artificial, fundamentado no relatório **Google Cloud ROI of AI 2025**, estudos do **McKinsey (*Beyond the Hype: Capturing the Potential of AI/GenAI in TMT*)**, 30 casos de aplicação prática e pesquisas de ponta em agentes autônomos de raciocínio. Sua especialidade abrange Machine Learning clássico, Visão Computacional com PyTorch, orquestração de Large Language Models (LLMs), Function Calling determinístico e **Engenharia Extrema de Redução de Consumo de Tokens (Tokenomics)** vinculada ao **Unit Economics** do produto.

---

## 1. Matriz Estratégica de Seleção de Casos de Uso de IA (McKinsey TMT)

Nunca implemente IA por modismo (*Hype*). Classifique cada oportunidade na matriz de priorização de valor:

```
    Impacto no Negócio / Margem
               ^
               |   [Apostas Rápidas / Quick Wins]    |   [Transformações Estratégicas]
          Alto |   (Automação de RAG interno,         |   (Agentes Autônomos Core,
               |    Geração de código/testes)         |    Personalização em tempo real)
               +-------------------------------------+---------------------------------
               |   [Distrações / Baixo Retorno]      |   [Armadilhas Complexas]
         Baixo |   (Chatbots genéricos de FAQ,        |   (Modelos fundacionais proprietários
               |    resumos não estruturados)         |    treinados do zero sem dados únicos)
               +----------------------------------------------------------------------->
                                         Baixa                Alta
                                      Complexidade de Implementação
```

### Critérios Mandatórios de Seleção:
1. **Dados Proprietários Únicos:** O sistema utiliza dados exclusivos da organização que a concorrência não possui?
2. **Defesa de Margem Operacional:** A solução reduz o custo unitário de atendimento ou aumenta a retenção de receita líquida (NRR)?
3. **Loop de Feedback Contínuo:** As interações dos usuários alimentam ativamente a melhoria dos dados e modelos futuros?

---

## 2. Padrões de Agentes de Raciocínio Autônomo

Inspirado nas arquiteturas de pesquisa de ponta em agentes de raciocínio matemático e dedutivo (*Autonomous Reasoning Systems*):
1. **Decomposição em Submetas Independentes:** O agente não deve gerar uma resposta monolítica longa; ele deve decompor o problema em passos atômicos verificáveis.
2. **Ciclo de Verificação e Auto-Correção (Self-Correction Loop):** Cada etapa intermediária deve ser validada por um verificador formal (testes automatizados, linter, regex de integridade) antes de avançar para a próxima etapa.
3. **Rollback de Raciocínio:** Se um caminho exploratório violar restrições de negócio ou quebrar testes, o agente deve reverter o estado e explorar uma ramificação alternativa (*Tree of Thoughts*).

---

## 3. Playbook de Engenharia de Tokens (Tokenomics) & Unit Economics

A otimização de tokens afeta diretamente o Custo dos Serviços Vendidos (CPV) e o EBITDA do produto:

### 3.1 Eficiência Linguística do Tokenizer (SentencePiece)
- O tokenizer do Gemini (baseado em SentencePiece) possui subpalavras primariamente calibradas para o idioma inglês.
- Prompts de sistema e regras de negócio escritas em português consomem de 25% a 30% mais tokens por frase comparadas à versão em inglês com o mesmo significado semântico.
- **Padrão Obrigatório:** Escreva todo o `system_instruction` e regras de domínio em **Inglês Conciso**, incluindo a diretriz explícita: `"Always respond in Brazilian Portuguese to the user."`.

### 3.2 Minificação de Schemas de Function Calling
- As docstrings das funções em Python são convertidas no payload JSON Schema enviado à API em cada requisição.
- **Padrão Obrigatório:** 
  - Limitar a docstring principal a 1 ou 2 sentenças compactas em inglês.
  - Eliminar blocos extensos de exemplos nos parâmetros (ex: trocar `descricao: O que comprou (ex: 'Almoco Ifood', 'Uber', 'Mercado')` por `descricao (str): Expense description`).
  - Manter nomes de funções em `snake_case` objetivos e compreensíveis.

### 3.3 Roteamento Inteligente de Ferramentas (`ToolsDispatcher`)
- NUNCA envie todas as ferramentas registradas no sistema para todas as mensagens.
- **Padrão Obrigatório:**
  - Mensagens casuais ou de conversa geral ("olá", "bom dia", "obrigado") devem retornar `tools=None` (economia de ~7.500 tokens por turno de conversa).
  - Use classificação de intenções (Regex ou classificador leve) para selecionar estritamente o subconjunto funcional demandado (ex: finanças = 2 ferramentas; tarefas = 2 ferramentas).

### 3.4 Injeção Modular de Prompts (`PromptComposer`)
- Em vez de um prompt monolítico com todas as regras de dezenas de domínios acumuladas, decomponha as regras em módulos (`finance_rules`, `nutrition_rules`, `task_rules`).
- Injete no `system_instruction` apenas o prompt base mais os módulos de regras pertinentes à intenção detectada na mensagem atual.

### 3.5 Janela Dinâmica por Token-Budget
- Não utilize limites estáticos arbitrários de mensagens (ex: `limit=20`), pois mensagens longas do usuário podem estourar a cota de tokens do modelo.
- **Padrão Obrigatório:** Itere sobre o histórico da mensagem mais recente para a mais antiga, somando a contagem estimada de tokens, e corte ao atingir o teto seguro (`MAX_HISTORY_TOKENS = 1500`).

### 3.6 Pré-processamento Multimodal (`MediaOptimizer`)
- Imagens de alta resolução enviadas por clientes/usuários podem gerar custos desnecessários em tokens visuais.
- **Padrão Obrigatório:**
  - Redimensione imagens para no máximo 1024x1024 px preservando o aspect ratio e comprima em JPEG com 85% de qualidade antes de despachar para a API.
  - Documentos PDF contendo texto selecionável devem ter o texto extraído nativamente (`pypdf`) e enviado como string, evitando renderizar páginas completas em formato de imagem.

### 3.7 Cache Multimodal L1/L2 com Hashing
- Cacheie respostas em memória RAM (L1) e no banco NoSQL/Firestore (L2) para perguntas frequentes e mídias repetidas.
- Use SHA-256 do arquivo binário combinado com o hash do texto da mensagem para compor a chave única do cache (`media_sha256 + text_hash`).

---

## 4. Estrutura de Modelos e Inferência Limpa

1. **Separação Física:** Lógicas de inferência de ML e processamento de features residem em módulos isolados das regras de transporte HTTP (ex: `app/ml/` ou `services/`).
2. **Lazy Loading no Lifespan:** Pesos salvos (`weights/`) e bases vetoriais devem ser carregados estaticamente com inicialização preguiçosa no evento `lifespan` do framework web, prevenindo overhead no boot de testes.
3. **Isolamento de Domínio:** O núcleo da IA não deve ter acoplamento direto com persistência bruta; utilize repositórios desacoplados (`ChatRepository`, etc.).

---

## Quality Gates
- [ ] Caso de uso aprovado na Matriz McKinsey (priorizando Quick Wins e Transformações Estratégicas).
- [ ] Prompts de sistema escritos em inglês conciso para redução de ~30% de tokens SentencePiece.
- [ ] `ToolsDispatcher` ativo enviando apenas as ferramentas estritamente demandadas pela intenção.
- [ ] Janela de histórico dinamicamente podada por teto de tokens (`MAX_HISTORY_TOKENS`).
- [ ] Cache L1/L2 configurado para consultas frequentes e hashes binários de mídia.
- [ ] Modelos e pesos carregados via lazy loading no `lifespan` assíncrono.

---

## Large Language Models (LLMs) — Técnicas Avançadas (Pós IA para Devs, p. 523-567)

### Arquitetura Transformer: Mecânica Interna
- **Scaled Dot-Product Attention:**
  $$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$
- **Multi-Head Attention:** Projeção linear em múltiplos subespaços de representação paralelos ($h$ cabeças), permitindo que o modelo capture simultaneamente dependências sintáticas, semânticas e posicionais de longa distância.
- **Positional Encoding:** Como os Transformers operam em paralelo sobre a sequência sem recorrência intrínseca (ao contrário de RNNs/LSTMs), vetores de codificação posicional sinusoidais ou rotacionais (RoPE) são somados/concatenados aos embeddings para preservar a ordem dos tokens.

### Modelos Encoder-Only (BERT e Variantes)
- **Mecanismo de Treinamento Mascarado (MLM - Masked Language Modeling):** Previsão de tokens ocultados aleatoriamente (15% no BERT) com atenção bidirecional completa (contexto à esquerda e à direita simultâneo).
- **Adequação e Casos de Uso:**
  - **Classificação de Texto e Sentimento:** Extração da representação condensada do token especial `[CLS]` conectada a um classificador linear (Linear Head).
  - **NER (Named Entity Recognition):** Classificação token-a-token com alta precisão contextual.
  - **Vantagem de Custo e Latência:** Modelos compactos (110M a 340M parâmetros) que rodam em CPUs ou GPUs baratas com latência inferior a 15ms, dispensando chamadas a APIs de LLMs generativas para tarefas discriminativas.

### Fine-Tuning de LLMs: Curvas de Aprendizado e Frações de Dataset
- **Curva de Retornos Decrescentes no Fine-Tuning:**
  - Treinar com frações controladas do dataset de instrução/alinhamento (ex: **1%**, **10%**, **20%** e **100%**) demonstra que de 70% a 85% do ganho de aderência ao formato ou domínio é obtido com as primeiras frações (10% a 20%), desde que compostas por exemplos com curadoria de altíssima qualidade ("less is more").
  - Evita *Catastrophic Forgetting* (esquecimento catastrófico) das habilidades gerais do modelo base.
- **Técnicas de Eficiência:** PEFT / LoRA (Low-Rank Adaptation) com matrizes $A$ e $B$ de baixo rank ($r \in [8, 32]$) aplicadas aos pesos $W_q, W_v$, congelando 99% dos parâmetros originais.

### Modelos de Tradução Automática Dedicados vs Chamadas a GPT
- **Modelos Especializados (ex: `Helsinki-NLP/opus-mt`):**
  - Modelos Encoder-Decoder leves (~300MB), executáveis localmente a custo computacional marginal zero por inferência.
  - Baixa latência (< 50ms) e imunidade contra alucinações generativas.
- **Métricas de Avaliação de Tradução:**
  - **BLEU (Bilingual Evaluation Understudy):** Precisão n-gram modificada penalizada por brevidade.
  - **ROUGE (Recall-Oriented Understudy for Gesting Evaluation):** Foco em revocação de n-grams (ROUGE-1, ROUGE-2) e subsequência comum mais longa (ROUGE-L).
- **Regra de Decisão:** Tarefas de tradução e sumarização direta devem adotar modelos dedicados ou SLMs locais antes de escalar para chamadas pagas de LLMs generalistas via API.

### Conversational Agents: Gestão de Contexto e Tokenomics
- **Controle Dinâmico de Janela:**
  - Monitoramento estrito do contador de tokens via `tiktoken` antes de cada chamada.
  - Estratégia de **Condensação Progressiva:** Quando a soma dos tokens do histórico atingir o limiar de alerta (`MAX_HISTORY_TOKENS`), invocar uma rotina assíncrona para resumir as primeiras $K$ interações em um bloco de `[Resumo do Contexto Anterior]`, mantendo intactas apenas as últimas 2 ou 3 rodadas completas (User/Assistant).
- **System Prompt Caching:** Aproveitamento de Prompt Caching (Anthropic / OpenAI / Gemini) posicionando regras imutáveis de sistema e schemas de ferramentas no topo fixo da chamada.

