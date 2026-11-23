# Referência: SAM, 5 Forças de Porter, Cadeia de Valor, ExO & MTP

Guia de consulta aprofundada para diagnóstico e posicionamento estratégico de TI.

---

## 1. Strategic Alignment Model (SAM — Henderson & Venkatraman)

O SAM propõe que o valor da TI nasce do **ajuste estratégico** (alinhamento externo entre estratégia de negócio e estratégia de TI) e da **integração funcional** (alinhamento interno entre processos organizacionais e infraestrutura/processos de TI).

### Os 4 Domínios e seus Componentes
| Domínio | Escopo Externo / Interno | Decisões-Chave |
| :--- | :--- | :--- |
| **Estratégia de Negócio** | Externo (Mercado) | Escopo de negócio, competências distintivas, governança (parcerias, M&A). |
| **Estratégia de TI** | Externo (Tecnologia) | Escopo tecnológico, competências sistêmicas (cloud, IA, dados), governança de TI (build vs buy, alianças). |
| **Infraestrutura Organizacional** | Interno (Empresa) | Estrutura administrativa, processos críticos, habilidades das pessoas. |
| **Infraestrutura e Processos de TI** | Interno (Engenharia) | Arquitetura de sistemas, processos de engenharia (CI/CD, SRE), competências técnicas. |

### Como Escolher a Perspectiva de Alinhamento
1. **Execução da Estratégia:** Negócio define a estratégia → reorganiza processos → TI implementa. *Risco:* TI vista apenas como centro de custo reativo.
2. **Potencial Tecnológico:** Negócio define ambição → TI desenha arquitetura habilitadora → transforma infraestrutura de TI. *Uso ideal:* modernização de plataforma e escala.
3. **Vantagem Competitiva:** TI identifica nova tecnologia (ex.: IA generativa, APIs abertas) → redesenha o modelo de negócio → adapta a organização. *Uso ideal:* disrupção de mercado.
4. **Nível de Serviço:** TI foca em excelência operacional → constrói plataforma de alta confiabilidade → eleva produtividade das áreas internas. *Uso ideal:* plataformas internas (IDP) e SLAs críticos.

---

## 2. As 5 Forças de Porter Aplicadas à Tecnologia

| Força Competitiva | Pergunta Estratégica para o Líder de TI | Alavanca Tecnológica |
| :--- | :--- | :--- |
| **Rivalidade entre Concorrentes** | Conseguimos iterar e lançar mais rápido que os rivais? | DORA elite (Lead Time curto), CI/CD, arquitetura modular. |
| **Poder dos Fornecedores** | Um provedor de nuvem ou SaaS pode inviabilizar nossa margem? | Padrões abertos (OCI/Containers, SQL padrão, OpenTelemetry), abstração de provedores críticos. |
| **Poder dos Clientes** | O que torna nossa experiência difícil de substituir? | Ecossistema integrado, APIs, personalização orientada a dados, confiabilidade superior. |
| **Ameaça de Novos Entrantes** | Quais barreiras defensivas (*moats*) nossa tecnologia cria? | Dados proprietários, modelos de IA treinados no domínio, efeitos de rede. |
| **Ameaça de Substitutos** | Nossa arquitetura suporta pivotar o produto sem reescrita total? | Domínios desacoplados (DDD), eventos, contratos versionados. |

---

## 3. Cadeia de Valor de Michael Porter (Build vs Buy)

Separar onde a empresa **diferencia** de onde apenas **opera**:

- **Atividades Primárias** *(Logística Interna, Operações, Logística Externa, Marketing & Vendas, Pós-Venda)*:
  - Onde mora a margem e o diferencial competitivo.
  - **Diretriz:** investir em **engenharia proprietária (Build)**, arquitetura sob medida e dados exclusivos.
- **Atividades de Apoio** *(Infraestrutura Administrativa, RH, Finanças, Jurídico, Suprimentos)*:
  - Essenciais para operar, raramente diferenciam no mercado.
  - **Diretriz:** priorizar **SaaS / soluções de prateleira (Buy)** com integração limpa, reservando o tempo dos engenheiros para o core.

---

## 4. Organizações Exponenciais (ExO) e MTP

Baseado em Salim Ismail (*Exponential Organizations*), uma ExO entrega impacto desproporcionalmente maior (10x) combinando um **MTP** claro com atributos externos (**SCALE**) e internos (**IDEAS**).

### MTP — Massive Transformative Purpose
Propósito ambicioso, aspiracional e focado em transformação externa (não em lucro interno).
- *Exemplos:* "Organizar a informação do mundo" (Google), "Acelerar a transição do mundo para energia sustentável" (Tesla).
- **Na Engenharia:** serve de norte para priorização arquitetural e atração de talentos — toda grande iniciativa técnica deve explicar qual parte do MTP ela acelera.

### Atributos ExO Relevantes para Arquitetura de TI
- **SCALE (Externos — Abundância):**
  - **S**taff on Demand (talentos especializados sob demanda).
  - **C**ommunity & Crowd (comunidades open-source, ecossistemas de desenvolvedores).
  - **A**lgorithms (automação, ML/IA para escalar decisões sem escalar headcount linearmente).
  - **L**everaged Assets (cloud elástica, serverless, infraestrutura sob demanda em vez de datacenters ociosos).
  - **E**ngagement (loops de engajamento, gamificação, transparência digital).
- **IDEAS (Internos — Controle e Ordem):**
  - **I**nterfaces (APIs padronizadas que conectam a abundância externa ao core interno).
  - **D**ashboards (observabilidade em tempo real, OKRs e métricas DORA visíveis).
  - **E**xperimentation (feature flags, testes A/B, Lean Startup em produção).
  - **A**utonomy (squads multidisciplinares alinhadas a Value Streams — Lei de Conway Inversa).
  - **S**ocial Technologies (colaboração assíncrona, documentação viva, ADRs).
