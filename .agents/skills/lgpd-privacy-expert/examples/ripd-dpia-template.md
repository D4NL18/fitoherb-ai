# Relatório de Impacto à Proteção de Dados Pessoais (RIPD / DPIA)

> **Instruções de uso:** Salve uma cópia preenchida em `.agents/docs/privacy/RIPD_<feature>.md` (ou `.agents/docs/business_rules/RIPD_<feature>.md` conforme convenção do projeto) antes da implementação de qualquer funcionalidade que trate **dados sensíveis**, **decisões automatizadas por IA**, **perfilamento em larga escala** ou **Legítimo Interesse**.

---

## 1. Identificação do Projeto e Partes Envolvidas

| Campo | Preenchimento |
| :--- | :--- |
| **Nome do Sistema / Feature** | `<Ex.: Motor de Análise de Crédito v2>` |
| **Versão do RIPD** | `v1.0` |
| **Data de Elaboração** | `AAAA-MM-DD` |
| **Controlador** | `<Razão Social / Unidade de Negócio>` |
| **Operadores / Suboperadores** | `<Ex.: GCP Cloud Run, Supabase, Provedor de LLM>` |
| **Encarregado de Dados (DPO)** | `<Nome e canal de contato>` |
| **Responsável Técnico (Arquiteto/Tech Lead)** | `<Nome>` |
| **Gatilho do RIPD** | `[ ] Dados Sensíveis  [ ] Decisão Automatizada / IA  [ ] Legítimo Interesse  [ ] Larga Escala  [ ] Menores` |

---

## 2. Descrição do Tratamento (Natureza, Escopo, Contexto e Finalidade)

- **Finalidade específica e explícita:** `<Descrever exatamente por que os dados são coletados e qual objetivo de negócio atendem.>`
- **Fluxo de dados (Ciclo de Vida):**
  1. *Coleta:* `<Origem dos dados — formulário, API, integração externa>`
  2. *Armazenamento:* `<Banco de dados, região/país, criptografia em repouso>`
  3. *Processamento / Uso:* `<Serviços, pipelines, modelos de IA/ML envolvidos>`
  4. *Compartilhamento / Transferência Internacional:* `<Terceiros, país de destino e mecanismo legal — Art. 33>`
  5. *Retenção e Descarte:* `<Prazo exato de retenção, gatilho de exclusão e método de expurgo/anonimização>`

---

## 3. Inventário de Dados, Classificação e Bases Legais

| Campo / Dado | Classificação LGPD | Base Legal (Art. 7º ou Art. 11) | Justificativa de Necessidade (Minimização) | Prazo de Retenção |
| :--- | :--- | :--- | :--- | :--- |
| `cpf` | Dado Pessoal | Art. 7º, V (Execução de Contrato) | Identificação única para emissão contratual | 5 anos após encerramento |
| `email` | Dado Pessoal | Art. 7º, V (Execução de Contrato) | Comunicação transacional | Enquanto conta ativa |
| `biometria_facial` | Dado Pessoal Sensível | Art. 11, II, "g" (Prevenção à Fraude) | Prova de vida na abertura de conta | Vetor descartado após verificação / conforme política |
| `ip_acesso` | Dado Pessoal | Art. 7º, II (Obrigação Legal — MCI) | Guarda obrigatória de registros de acesso | 6 meses (Art. 15, Lei 12.965/14) |

---

## 4. Necessidade, Proporcionalidade e Privacy by Default

- **Princípio da Minimização:** `<Confirmar que nenhum campo extra é coletado "para uso futuro" e que APIs não fazem overfetching de PII.>`
- **Privacy by Default:** `<Confirmar que opções não essenciais vêm desmarcadas por padrão e que o acesso é restrito por menor privilégio (RBAC/RLS).>`
- **Direitos do Titular (Art. 18 e Art. 20):**
  - Canal de acesso/correção/eliminação: `<Endpoint ou portal>`
  - Revisão de decisão automatizada (se aplicável): `<Fluxo de revisão e explicabilidade>`
- **Teste de Balanceamento (LIA — preencher apenas se houver Legítimo Interesse):**
  - *Finalidade legítima:* `<...>`
  - *Necessidade (não há meio menos invasivo):* `<...>`
  - *Balanceamento e Opt-Out:* `<...>`

---

## 5. Matriz de Riscos à Privacidade e Medidas de Mitigação

> Escala sugerida: **Probabilidade (1-5)** × **Impacto (1-5)** = **Risco** (`1-5 Baixo`, `6-12 Médio`, `15-25 Alto/Crítico`).

| ID | Cenário de Risco | Prob. | Imp. | Risco Inerente | Controles / Medidas de Mitigação | Risco Residual | Responsável |
| :--- | :--- | :---: | :---: | :---: | :--- | :---: | :--- |
| R-01 | Vazamento de PII em logs de aplicação ou stacktraces | 3 | 4 | 12 (Médio) | Mascaramento estruturado de PII em logs; proibição de logar `req.body`/entidades completas | 3 (Baixo) | Dev / Reviewer |
| R-02 | Acesso não autorizado entre tenants (IDOR / BOLA) | 2 | 5 | 10 (Médio) | Isolamento multi-tenant via RLS / filtro obrigatório por `tenant_id` do token JWT (HttpOnly) | 2 (Baixo) | Arquiteto / SecOps |
| R-03 | Exposição de PII em prompts enviados a LLM externa | 3 | 5 | 15 (Alto) | Sanitização/anonimização prévia de PII antes da chamada; contrato DPA com Zero Data Retention | 3 (Baixo) | AI Specialist / DPO |
| R-04 | Retenção excessiva de dados após encerramento da conta | 3 | 3 | 9 (Médio) | Job automatizado de TTL/expurgo e anonimização em cascata | 2 (Baixo) | DBA / DevOps |

---

## 6. Parecer do Encarregado de Dados (DPO) e Aprovação

- **Decisão:** `[ ] Aprovado  [ ] Aprovado com Ressalvas  [ ] Vetado (Requer Redesenho)`
- **Condicionantes / Ressalvas:** `<Listar pendências obrigatórias antes do go-live, se houver.>`
- **Data da Próxima Revisão:** `<AAAA-MM-DD ou a cada mudança relevante de escopo>`
- **Assinatura / Registro:** `<DPO>` · `<Tech Lead / Arquiteto>`
