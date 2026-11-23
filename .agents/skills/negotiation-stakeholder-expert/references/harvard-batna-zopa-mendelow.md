# Referência: Método de Harvard, BATNA/MAANA, ZOPA, Resolução de Conflitos e Matriz de Mendelow

Guia de referência aprofundado para negociações técnicas, contratuais, de prazo/escopo e alinhamento de stakeholders em ambientes de engenharia e produto.

---

## 1. Método de Negociação Baseada em Princípios (Harvard)

Desenvolvido por Roger Fisher, William Ury e Bruce Patton (*Getting to Yes*), substitui a barganha posicional ("cabo de guerra") por quatro pilares operacionais:

| Pilar | Pergunta-Chave na Preparação | Erro Comum em TI |
| :--- | :--- | :--- |
| **1. Pessoas** | Quais emoções, pressões políticas ou receios estão em jogo? | Tratar o pedido urgente de negócio como "falta de noção técnica" e reagir na defensiva. |
| **2. Interesses** | Por que a outra parte quer isso? Qual dor real precisa ser resolvida? | Discutir a solução/data ("sexta-feira") sem entender o evento que a motivou (ex.: demo de vendas). |
| **3. Opções** | Que alternativas criativas ampliam o valor antes de dividir concessões? | Responder "não dá" sem oferecer pacotes de trade-off (MVP, feature flag, faseamento). |
| **4. Critérios Objetivos** | Qual padrão independente legitima o acordo para ambos os lados? | Basear a estimativa em "achismo" em vez de throughput histórico, SLA, OWASP ou DORA. |

### Técnica dos 5 Porquês para Descobrir Interesses
Quando um stakeholder apresentar uma **posição rígida**, investigue sem confronto:
- *"O que torna essa data específica crítica para o negócio?"*
- *"Se entregarmos 100% do fluxo principal até lá e deixarmos os relatórios para a semana seguinte, isso resolve o objetivo?"*
- *"Qual métrica de sucesso você precisará apresentar após o lançamento?"*

---

## 2. BATNA (MAANA), Ponto de Reserva e ZOPA

### Conceitos Essenciais
- **BATNA / MAANA (*Best Alternative to a Negotiated Agreement*):** Seu plano B concreto caso não haja acordo. **Não é um desejo**, é uma alternativa executável e mensurada.
- **Ponto de Reserva (*Walkaway Point*):** O limite mínimo (para quem oferta) ou máximo (para quem compra/concede) abaixo/acima do qual é melhor acionar o BATNA.
- **ZOPA (*Zone of Possible Agreement*):** A interseção entre o Ponto de Reserva da Parte A e o Ponto de Reserva da Parte B.
  - **ZOPA Positiva:** Há sobreposição; um acordo racional beneficia ambos.
  - **ZOPA Negativa:** Não há sobreposição; ou se reestrutura o escopo (novas variáveis como prazo, pagamento, SLA, risco) ou se aciona o BATNA.

### Como Fortalecer seu BATNA em Tecnologia
1. **Fornecedores/Cloud:** Tenha cotação real de um concorrente ou prova de conceito de alternativa open-source antes de renovar contrato.
2. **Prazo/Escopo Interno:** Tenha pronto um plano de entrega fatiada (MVP) validado tecnicamente com métricas históricas da squad.
3. **Alocação de Time:** Quantifique explicitamente o *custo de oportunidade* (o que sai do roadmap se a nova demanda entrar).

---

## 3. Resolução Construtiva de Conflitos (Thomas-Kilmann / TKI)

Escolha o estilo de manejo de conflito conforme a importância do **Relacionamento** e do **Resultado Técnico**:

| Estilo | Assertividade | Cooperação | Quando usar em TI |
| :--- | :---: | :---: | :--- |
| **Colaboração (Ganha-Ganha)** | Alta | Alta | Decisões arquiteturais críticas, roadmap trimestral, contratos estratégicos. |
| **Compromisso (Meio-Termo)** | Média | Média | Prazos apertados com duas opções igualmente aceitáveis e baixo risco. |
| **Competição (Firmeza)** | Alta | Baixa | Questões inegociáveis: segurança (OWASP), privacidade (LGPD), compliance legal. |
| **Acomodação (Ceder)** | Baixa | Alta | O tema é pouco relevante tecnicamente, mas muito importante para o stakeholder (gera capital político). |
| **Evitação (Adiar)** | Baixa | Baixa | Emoções acirradas (esfriar antes de decidir) ou falta de dados objetivos no momento. |

---

## 4. Matriz de Gestão de Stakeholders (Mendelow — Poder x Interesse)

Mapeie cada stakeholder no início de projetos, migrações ou negociações críticas:

| Quadrante | Poder | Interesse | Estratégia de Engajamento | Cadência & Artefatos |
| :--- | :---: | :---: | :--- | :--- |
| **Gerenciar de Perto** (*Manage Closely*) | Alto | Alto | Envolver nas decisões, co-criar trade-offs, zero surpresas. | Semanal / 1:1, RFCs, demos antecipadas. |
| **Manter Satisfeito** (*Keep Satisfied*) | Alto | Baixo | Garantir conformidade, orçamento e risco sob controle sem ruído operacional. | Mensal / Sumário executivo, KPIs, alertas de risco. |
| **Manter Informado** (*Keep Informed*) | Baixo | Alto | Dar visibilidade, ouvir feedbacks e transformar em aliados/embaixadores. | Quinzenal / Release notes, canais públicos, demos. |
| **Monitorar** (*Monitor*) | Baixo | Baixo | Esforço mínimo; observar mudanças de papel ou interesse. | Trimestral / Newsletter ou status geral. |

> **Atenção dinâmica:** Stakeholders mudam de quadrante durante o projeto (ex.: Jurídico/DPO pode subir de *Manter Satisfeito* para *Gerenciar de Perto* quando uma feature passa a coletar dados sensíveis). Reavalie a matriz a cada marco.
