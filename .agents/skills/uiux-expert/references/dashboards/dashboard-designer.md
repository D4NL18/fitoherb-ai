# Dashboard Designer: Planejamento e Design de Painéis e Métricas 📊📈

> **Origem:** Baseado nas diretrizes de `nickcrew/claude-cortex/skills/dashboard-designer`  
> **Propósito:** Framework estruturado para concepção de dashboards acionáveis, hierarquia visual de KPIs, layouts em F/Z, codificação de cores de status e seleção de ferramentas de visualização.

---

## 1. Visão Geral e Princípio Central
Um dashboard bem desenhado apresenta a **informação certa para a pessoa certa no momento certo**, permitindo tomada de decisão imediata, não apenas exibição passiva de dados. O design combina princípios de visualização de dados (*Data Viz*) com design de experiência (*UX*) para impulsionar ações.

### Quando Usar
- Concepção de um novo dashboard ou painel de métricas analíticas.
- Reestruturação de dashboards sobrecarregados, ignorados ou confusos.
- Definição da hierarquia de KPIs antes da implementação técnica de frontend ou SQL.
- Escolha de ferramentas de BI ou bibliotecas de gráficos (ECharts, Chart.js, ApexCharts, Grafana, Tableau, Power BI).
- Apresentação de dados executivos com narrativa visual clara (*Data Storytelling*).

### Quando NÃO Usar
- Escrita de queries SQL analíticas (competência de engenharia de dados / DBA).
- Construção de código bruto de renderização de canvas (competência do Desenvolvedor).
- Relatórios estáticos ou lâminas de apresentação.
- Modelagem de Data Warehouse e pipelines ETL.

---

## 2. Guia de Referência Rápida (Quick Reference)

| Princípio de Design | Regra Inegociável |
| :--- | :--- |
| **Hierarquia Visual** | O KPI mais crítico fica no canto superior esquerdo (Top-Left); detalhes no canto inferior direito. |
| **Espaço em Branco (White Space)** | 15% a 20% da área do painel deve ser espaço negativo para evitar sobrecarga cognitiva. |
| **Codificação de Cores** | Máximo de 4 a 5 cores na interface; cores semáforo (verde/vermelho) apenas para status de metas. |
| **Densidade de Gráficos** | Máximo de 6 a 8 gráficos por tela; priorize gráficos maiores e legíveis a mosaicos densos. |
| **Quantidade de KPIs Headline** | Executivo: 3 a 5 KPIs. Operacional: 8 a 12 KPIs. Analítico/Explorer: sob demanda. |
| **Títulos dos Cards** | Títulos expressam *Insights* (ex: "Receita cresceu 12% vs meta"), NUNCA meros rótulos neutros ("Receita"). |
| **Frequência de Atualização** | Tempo real para operações/SRE; diário para gestão operacional; semanal/mensal para estratégia C-Level. |
| **Interatividade** | Filtros globais sempre no topo; drill-down por clique contextual; padrão na visão mais comum. |
| **Responsividade Móvel** | Gráficos empilhados verticalmente no mobile; exiba apenas os 3 KPIs primários no smartphone. |
| **Acessibilidade** | Paleta segura para daltônicos (Colorblind-safe); contraste mínimo de texto 4.5:1 (WCAG AA). |

---

## 3. As 7 Etapas do Processo de Design de Dashboard

### Etapa 1: Definição de Público-Alvo e Propósito
Responda a 4 perguntas antes de traçar qualquer wireframe:
1. **Quem é o usuário principal?** C-Level (Diretoria), Gestor Operacional, Engenheiro/SRE, Analista de Dados ou Cliente?
2. **Que decisão este painel orienta?** (Ex: *"Devemos realocar verba para a região Sul este mês?"*).
3. **Qual a frequência de consulta?** Tempo real (Live Ops), Diário, Semanal ou Mensal?
4. **Qual ação o usuário pode tomar ao ver os números?** Se nenhuma ação for viável ➔ reavalie se um dashboard é o formato adequado.

#### Arquétipos de Dashboard:
| Arquétipo | Público | Frequência | Qtd. KPIs | Exemplo |
| :--- | :--- | :--- | :---: | :--- |
| **Estratégico** | C-Level, VPs | Semanal / Mensal | 3–5 | Scorecard de Saúde da Empresa / DRE / EBITDA |
| **Operacional** | Gestores, Líderes de Squad | Diário | 8–15 | Pipeline de Vendas, Funil de Conversão, Sprint Burndown |
| **Analítico** | Cientistas e Analistas | Sob demanda | Ilimitado | Retenção de Coortes, Exploração Multidimensional |
| **Monitoramento Tempo Real** | DevOps, SRE, Suporte | Live / Segundos | 10–20 | Latência P95, Erros 5xx, Uptime, CPU e DORA Metrics |

---

### Etapa 2: Seleção e Nivelamento de KPIs
Um KPI legítimo DEVE ser:
- **Acionável:** O visualizador tem autoridade ou capacidade técnica para intervir baseado no que vê.
- **Oportuno (Timely):** Atualizado na mesma cadência em que o dashboard é consultado.
- **Comparável:** Possui obrigatoriamente um comparativo (vs meta, vs período anterior ou vs benchmark).
- **Sem Ambiguidade:** Possui fórmula matemática única compreendida por todas as áreas.

#### A Pirâmide de 3 Níveis de KPIs:
- **Nível 1 (Headline KPIs):** 3 a 5 números grandes em destaque no topo da tela (ex: ARR Total, MAU, Churn Rate). Tipografia em 24–32pt.
- **Nível 2 (Contexto / Gráficos Primários):** 6 a 10 gráficos demonstrando tendências temporais e distribuições (ex: evolução de vendas por mês, vendas por canal).
- **Nível 3 (Detalhamento / Investigação):** Tabelas analíticas com filtros e drill-downs contextuais.

---

### Etapa 3: Arquitetura de Informação e Padrões de Layout

#### Padrão em F (F-Pattern Layout - Padrão Universal Mais Eficaz)
O olho humano escaneia: topo-esquerda ➔ topo-direita ➔ desce pela esquerda.
```
┌─────────────────────────────────────────────────────────────────┐
│ [Filtro Data ▼]  [Filtro Segmento ▼]          Atualizado às 18h │
├───────────────┬───────────────┬────────────────┬────────────────┤
│ KPI 1 (Hero)  │ KPI 2         │ KPI 3          │ KPI 4          │
│ R$ 1.2M       │ 3.4x meta     │ 28% conv.      │ 12 em risco    │
│ ▲ +15% vs LM  │ ✅ Na meta    │ ▲ +3pp vs LM   │ 🔴 R$ 340k     │
├───────────────┴───────────────┴────────────────┴────────────────┤
│ Gráfico Primário (Tendência Temporal - 60% largura)             │
├───────────────────────────────┬─────────────────────────────────┤
│ Gráfico Secundário (Segmento) │ Gráfico de Funil / Distribuição │
├───────────────────────────────┴─────────────────────────────────┤
│ Tabela Analítica de Detalhes com Paginação                      │
└─────────────────────────────────────────────────────────────────┘
```

#### Padrão em Z (Z-Pattern Layout - Dashboards Executivos)
Poucos elementos, foco em narrativa fluida: Topo (KPIs) ➔ Diagonal (Gráfico macro de saúde) ➔ Base (Próximos passos e alertas).

---

### Etapa 4: Hierarquia Visual e Escala Tipográfica
1. **Posição:** O canto superior esquerdo é a área mais nobre da tela. Posicione ali o KPI herói.
2. **Tamanho:** Elementos mais importantes devem ser visivelmente maiores.
3. **Escala Tipográfica:**
   - Valores numéricos de KPI: `24px` a `32px` (peso `700` ou `800`).
   - Títulos de cards e gráficos: `14px` a `16px` (peso `600`).
   - Rótulos contextuais e legendas: `11px` a `12px` (peso `400`).
4. **Respiro:** 15% a 20% de espaço livre entre cards impede a sensação de "painel de controle de usina".

---

### Etapa 5: Sistema de Cores e Acessibilidade (Color Coding)
- 🟢 **Verde:** Bom, dentro da meta, acima do esperado (`#009988` ou `#22c55e`).
- 🔴 **Vermelho:** Ruim, alerta crítico, abaixo do esperado (`#CC3311` ou `#ef4444`).
- 🟡 **Amarelo / Laranja:** Atenção, aproximando-se do limiar (`#EE7733` ou `#f59e0b`).
- 🔵 **Azul:** Dados primários neutros, linhas de tendência histórica (`#0077BB` ou `#3b82f6`).
- ⬜ **Cinza:** Contexto, períodos passados, linhas de grade e eixos (`#64748b` ou `#94a3b8`).

> [!IMPORTANT]
> **Paleta Acessível a Daltônicos (Colorblind-Safe):**
> Nunca use verde e vermelho sozinhos como único sinalizador. Adicione sempre um ícone indicador (ex: `▲ +15%`, `▼ -4%`, `✅`, `🔴`) e respeite contraste mínimo de 4.5:1.

---

### Etapa 6: Guia de Seleção de Ferramentas e Bibliotecas

| Necessidade | Tecnologia / Ferramenta Recomendada | Justificativa |
| :--- | :--- | :--- |
| **Frontend Customizado (Angular / React)** | **Apache ECharts** ou **ApexCharts** | Alto desempenho, suporte a temas dark/light, gráficos SVG/Canvas responsivos. |
| **Monitoramento de Engenharia / SRE** | **Grafana** | Conexão nativa com Prometheus/CloudWatch, alertas em tempo real. |
| **BI Corporativo em Grande Escala** | **Tableau** ou **Looker** | Camada semântica governada (LookML), modelagem robusta de métricas. |
| **Ecossistema Microsoft / Azure** | **Power BI** | Integração com Active Directory, DAX e suite Office. |
| **Dashboards Operacionais com Ações (CRUD)** | **Retool** | Permite disparar mutações e rotas diretamente dos cards do painel. |
| **Analytics Rápido / Startups** | **Metabase** ou **Looker Studio** | Gratuito/open-source, conexão direta SQL e fácil compartilhamento. |

---

### Etapa 7: Checklist de Qualidade de Dashboards (Quality Gate)
Antes de aprovar o layout de qualquer dashboard:
- [ ] Todo gráfico tem título formulado como **Insight** (ex: *"Receita cresceu 12% no trimestre"*, não apenas *"Receita"*).
- [ ] Todo card de KPI possui valor de comparação (vs meta, vs período anterior ou vs baseline).
- [ ] Codificação de cores é consistente em toda a página.
- [ ] O seletor de intervalo de datas está evidente no topo e com valor padrão intuitivo.
- [ ] Os números estão formatados com precisão adequada (ex: `R$ 1.2M`, não `R$ 1.234.567,89`).
- [ ] Máximo de 6 a 8 blocos visuais por tela para evitar sobrecarga.
- [ ] O layout mobile empilha os cards e exibe prioritariamente os 3 KPIs heróis.
- [ ] O rodapé informa a fonte dos dados e o timestamp de atualização (*"Atualizado há 10 min"*).
