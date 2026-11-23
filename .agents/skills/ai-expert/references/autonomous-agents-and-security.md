# Agentes Autônomos com LLM, Arquitetura Transformer e Segurança Defensiva

## 1. Arquitetura Transformer (Encoder-Decoder vs Decoder-Only)
- **Encoder ($N\times$):** `Input Embedding + Positional Encoding -> Multi-Head Attention -> Add & Norm -> Feed Forward -> Add & Norm`. Ideal para compreensão bidirecional (BERT, classificação, NER).
- **Decoder-Only (GPT, LLaMA, Claude, Gemini):** `Input Tokens -> Token/Position Embedding -> N x (Masked Self-Attention -> Feed Forward) -> Output Tokens`. Pré-treinado na tarefa autorregressiva de previsão do próximo token em grandes corpora não rotulados.
- **Métodos de Alinhamento Pós-Pré-Treino:** `SFT` (Supervised Fine-Tuning), `RL` / `RLHF` (Reinforcement Learning) e `Ranking` (ex.: DPO).

---

## 2. Níveis de Inteligência de Agentes Pessoais (L1–L5)

| Nível | Descrição | Capacidades Associadas |
| :--- | :--- | :--- |
| **L1** | Passo simples seguindo | Execução direta de etapas |
| **L2** | Automação Determinística de Tarefas | Formulação e execução de etapas estruturadas |
| **L3** | Automação Estratégica de Tarefas | Planejamento, Reflexão e Descoberta de necessidades |
| **L4** | Memória e Consciência do Contexto | Decisão profissional contextualizada |
| **L5** | Personagem Digital | Criatividade e inteligência emocional |

---

## 3. Pilares Cognitivos de um Agente LLM

### 3.1 Planejamento e Raciocínio
- **Chain of Thought (CoT):** Decomposição passo a passo (crítico para lógica e matemática).
- **Tree of Thoughts (ToT):** Exploração de múltiplas ramificações com avaliação e backtracking.
- **LLM+P:** Delega planejamento formal para um planejador externo (ex.: PDDL).
- **ReAct (Reason + Act):** Alterna `Thought -> Action (Tool) -> Observation` até `Finish[answer]`.
- **Autorreflexão e Chain of Hindsight (CoH):** Melhora iterativa guiada por autocrítica e histórico de tentativas avaliadas.

### 3.2 Taxonomia de Memórias
- **Sensory Memory:** Sinais brutos multimodais (icônica/visual, ecoica/auditiva, háptica).
- **Short-term / Working Memory:** Janela de contexto ativa do modelo.
- **Long-term Memory:**
  - *Explícita / Declarativa:* **Episódica** (eventos passados) e **Semântica** (fatos/conceitos em Vector DB).
  - *Implícita / Procedural:* Habilidades, ferramentas e código reutilizável.
- **Recuperação em Agentes Generativos (Park et al., 2023):** Ciclo `Perceive -> Memory Stream -> Retrieve (Relevância + Recenticidade + Importância) -> Plan / Reflect -> Act`.

### 3.3 Padrões de Ferramentas, Prompt Chains e Routers
- **Sequential Prompt Chains:** Quebram uma instrução complexa (ex.: detectar PII → remover PII → substituir por dados sintéticos) em etapas menores confiáveis para modelos mais baratos.
- **Routers:** **Embedding Router** (roteamento por similaridade vetorial) ou **LLM Router** (classificação estruturada para escolher entre prompts especialistas).
- **Frameworks clássicos:** **MRKL** (raciocínio modular + especialistas), **TALM / Toolformer** (auto-aprendizado de chamadas de API) e **HuggingGPT** (4 etapas: *Task Planning → Model Selection → Task Execution → Response Generation*).
- **Lições de Estudos de Caso:**
  - *ChemCrow (Bran et al., 2023):* LLM + 13 ferramentas especializadas supera GPT-4 puro em síntese química, mas evidencia limites da autoavaliação de LLMs em domínios críticos.
  - *Descoberta Científica Autônoma (Boiko et al., 2023):* Demonstra risco real de uso indevido (armas químicas/biológicas) exigindo guardrails rígidos de segurança.
  - *AutoGPT:* Demonstrou o padrão de saída estruturada em JSON (`thoughts: {text, reasoning, plan, criticism, speak}` + `command: {name, args}`), mas também o risco de loops sem critério de parada.

---

## 4. Arquiteturas Defensivas e Compliance

### 4.1 Arquitetura Dual LLM (Mitigação de Prompt Injection)
- **Privileged LLM:** Interage com comandos confiáveis do usuário/sistema e controla **Agents** e **External Storage**.
- **Quarantined LLM:** Recebe conteúdo não-confiável (e-mails, web, PDFs externos) para sumarização/extração **sem acesso a ferramentas**.
- **Regra crítica em cadeias:** Nunca reinjete texto livre vindo do *Quarantined LLM* como instrução executável no *Privileged LLM*; passe apenas dados estruturados validados por schema.

### 4.2 Arquitetura SMART Bot (Guardrails de Entrada e Saída)
Insere uma camada de **Prompt & Output Check** entre o usuário e o agente para detectar viés, consultas impróprias, vazamento de dados e saídas inválidas antes de acionar a camada de APIs externas, sistema de arquivos local, Vector DB (longo prazo) e Cache (curto prazo).

### 4.3 Fluxo de Dados Corporativo (Referência Azure OpenAI)
- **Inference:** `App -> API -> Synchronous Content Filtering <-> Base/Finetuned Model`, com `Asynchronous Abuse Monitoring` (retenção padrão de 30 dias geo-específica, passível de isenção formal para compliance/LGPD).
- **Finetuning:** Dados isolados em storage dedicado com criptografia dupla (*Double encrypted*) exclusivo do recurso do cliente.
