# Referência: Três Horizontes, Ambidestria, Lean Startup, Design Thinking e Plataformas

Guia consolidado para estratégia de inovação tecnológica, experimentação disciplinada e modelos de plataforma.

---

## 1. Os Três Horizontes de McKinsey (Governança e Métricas)

Cada horizonte exige **governança, métricas e perfil de engenharia diferentes**. Aplicar métricas de H1 (ROI imediato, SLA rígido) em projetos de H3 mata a inovação antes da validação.

| Dimensão | Horizonte 1 (H1 — Core) | Horizonte 2 (H2 — Emergente) | Horizonte 3 (H3 — Disrupção) |
| :--- | :--- | :--- | :--- |
| **Objetivo** | Defender e otimizar o negócio atual | Escalar oportunidades validadas | Explorar futuros modelos e tecnologias |
| **Alocação Típica** | ~70% | ~20% | ~10% |
| **Métricas Principais** | EBITDA, SLA, CAC/LTV, redução de custos | Crescimento de receita, retenção, PMF | Aprendizado validado, taxa de experimentos |
| **Postura de Engenharia** | Alta estabilidade, compliance, automação | Escala rápida, arquitetura evolutiva | Prototipação, spikes, descarte rápido |

---

## 2. Ambidestria Organizacional e Canibalização Estratégica

A **ambidestria organizacional** é a capacidade de executar simultaneamente **Exploitation** (extrair eficiência máxima do core atual) e **Exploration** (buscar novos negócios que podem inclusive substituir o core).

### A Lição da Canibalização Estratégica (Caso Netflix)
- **Contexto:** A Netflix construiu um negócio altamente lucrativo de aluguel de DVDs pelo correio (H1).
- **Decisão Corajosa:** Em vez de proteger o negócio de DVDs até ser destruída por concorrentes (como ocorreu com a Blockbuster), a Netflix **canibalizou o próprio core** investindo pesadamente em streaming (H2/H3) e, posteriormente, em produção original de conteúdo (estúdio próprio).
- **Regra para Líderes de Tecnologia:** *"Se uma nova tecnologia vai tornar seu produto atual obsoleto, é melhor que você mesmo o canibalize do que esperar um entrante fazê-lo."*
- **Padrão Arquitetural Habilitador:** Use *Strangler Fig*, APIs desacopladas e eventos para construir o novo modelo em paralelo, migrando clientes gradualmente sem derrubar a receita do H1.

---

## 3. Design Thinking (Duplo Diamante) + Lean Startup

Combine **Design Thinking** (garantir que estamos resolvendo o problema certo) com **Lean Startup** (validar rapidamente a solução com menor desperdício) e **Ágil** (entregar de forma incremental).

1. **Empatia & Descoberta:** entrevistas em profundidade, observação de usuários reais, mapeamento de dores (*Jobs to Be Done*).
2. **Definição:** sintetizar o problema central em uma declaração clara (*How Might We...*).
3. **Ideação:** divergir em múltiplas hipóteses antes de escolher uma arquitetura ou solução.
4. **Prototipação & MVP (Lean Startup):** construir o artefato mínimo para testar a hipótese mais arriscada (ex.: *Fake Door*, *Concierge MVP*, *Wizard of Oz*, protótipo navegável).
5. **Teste, Medição e Aprendizado Validado:**
   - **Métricas Acionáveis:** taxa de ativação, retenção D7/D30, conversão real, disposição a pagar.
   - **Evitar Métricas de Vaidade:** total acumulado de cadastros, pageviews brutos, downloads sem uso.
6. **Decisão Formal:** **Perseverar** (escalar), **Pivotar** (mudar segmento, canal, monetização ou Zoom-In/Zoom-Out) ou **Encerrar** (matar o experimento e registrar o aprendizado).

---

## 4. Modelos de Plataforma e Efeitos de Rede

Diferente de negócios lineares (*pipelines* que produzem e vendem em sentido único), **plataformas** criam valor conectando produtores e consumidores e reduzindo atrito de transação.

### Tipos de Efeitos de Rede
- **Direto (Mesmo Lado):** mais usuários aumentam diretamente o valor para os demais usuários (ex.: mensageiros, redes colaborativas).
- **Indireto / Bilateral (Lados Cruzados):** mais oferta (vendedores, desenvolvedores, criadores) atrai mais demanda (compradores, usuários finais), gerando um ciclo virtuoso (*flywheel*).
- **Efeito de Rede de Dados:** quanto mais usuários interagem, melhores ficam os modelos de recomendação/IA, atraindo ainda mais usuários.

### Desafios Críticos de Engenharia em Plataformas
1. **Problema do Ovo e da Galinha (*Cold Start*):** começar por um nicho denso ou oferecer utilidade *single-player* antes de depender da rede.
2. **Curadoria e Confiança:** reputação, moderação, antifraude e SLAs para evitar degradação da qualidade com o crescimento.
3. **API First & Ecossistema:** expor capacidades do core via APIs documentadas, webhooks e SDKs para que parceiros criem extensões e ampliem o fosso competitivo.
