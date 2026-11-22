# Referência: Anonimização vs Pseudonimização (LGPD), Migrations Seguras e Data Mesh

Este material aprofunda as práticas de engenharia de dados seguras e governadas para DBAs e Arquitetos de Dados.

---

## 1. Anonimização vs Pseudonimização na LGPD (Lei 13.709/2018)

A distinção jurídica e técnica impacta diretamente o escopo de obrigações regulatórias:

| Critério | Pseudonimização (Art. 13, § 4º) | Anonimização (Art. 5º, XI e Art. 12) |
| :--- | :--- | :--- |
| **Definição** | Substituição de identificadores diretos por um código/token (`uuid_titular`), mantendo tabela de mapeamento segregada. | Processo técnico que impede, por meios razoáveis disponíveis na época, a associação direta ou indireta a um indivíduo. |
| **Reversibilidade** | **Reversível** (com acesso à chave/tabela de mapeamento). | **Irreversível**. |
| **Continua sendo Dado Pessoal?** | **Sim** — continua sujeito integralmente à LGPD, mas reduz fortemente o risco em caso de incidente. | **Não** — deixa de ser dado pessoal para fins da LGPD (salvo se o processo puder ser revertido com esforço razoável). |
| **Uso Recomendado** | Tabelas transacionais de alto volume, logs operacionais, analytics interno com necessidade de reconciliação. | Datasets analíticos abertos, treinamento de modelos de ML, cumprimento de direito de exclusão preservando registros fiscais. |

### Técnicas Práticas no Banco de Dados
- **Pseudonimização:** `uuid_titular` sem significado semântico + tabela cofre `identidade_titulares` em schema separado com RBAC restrito e auditoria de leitura.
- **Mascaramento Dinâmico (Views/Funções):** expor apenas `***.456.789-**` ou `j***@dominio.com` para perfis de suporte e BI.
- **Anonimização por Exclusão (Right to Erasure):** sobrescrever PII com valores irreversíveis (`ANONIMIZADO`, `NULL`, hash com salt descartado) preservando chaves estrangeiras e valores fiscais exigidos por lei.

---

## 2. Travas Anti-Perda de Dados em Migrations (Expand-and-Contract)

Em sistemas em produção com zero downtime, **nunca** execute mudanças destrutivas em um único passo (`DROP COLUMN`, `RENAME COLUMN`, `ALTER TYPE` bloqueante). Adote o padrão **Expand-and-Contract**:

1. **Fase 1 — Expand (Aditiva e Compatível):**
   - Adicione a nova coluna/tabela (nullable ou com default seguro).
   - Crie índices usando `CREATE INDEX CONCURRENTLY` (PostgreSQL) para evitar lock de escrita.
   - Atualize a aplicação para fazer *dual-write* (gravar na coluna antiga e na nova).
2. **Fase 2 — Backfill Controlado:**
   - Migre registros históricos em lotes pequenos (ex.: 1.000 a 5.000 linhas por transação) com pausa curta entre lotes para não saturar I/O ou replicação.
   - Valide consistência entre coluna antiga e nova.
3. **Fase 3 — Switch (Virada de Leitura):**
   - Atualize a aplicação para ler da nova coluna e adicione `NOT NULL` usando `CHECK (...) NOT VALID` seguido de `VALIDATE CONSTRAINT` (evita lock exclusivo prolongado).
4. **Fase 4 — Contract (Limpeza Segura):**
   - Somente após janela de observação segura (ex.: 1–2 sprints) e aprovação explícita, remova a coluna obsoleta e o código de *dual-write*.

### Checklist de Travas Anti-Perda
- [ ] Proibido `DROP TABLE`, `TRUNCATE` ou `DROP COLUMN` sem aprovação explícita e backup/snapshot validado.
- [ ] Toda migration possui `lock_timeout` e `statement_timeout` configurados para abortar antes de derrubar a produção.
- [ ] Script de rollback (ou plano de mitigação) documentado antes da execução.

---

## 3. Princípios de Data Mesh para Arquitetos e DBAs

O **Data Mesh** (Zhamak Dehghani) resolve o gargalo de equipes centralizadas de dados por meio de 4 pilares:

1. **Domain-Oriented Decentralized Data Ownership:** cada domínio de negócio (ex.: Pagamentos, Pedidos, Logística) é dono dos seus dados operacionais e analíticos.
2. **Data as a Product:** conjuntos de dados expostos para outros times devem ser *Discoverable, Addressable, Trustworthy, Self-Describing, Interoperable e Secure* — com **Data Contract** versionado (schema, SLA de frescor, qualidade e classificação LGPD).
3. **Self-Serve Data Infrastructure as a Platform:** a plataforma central fornece templates de catálogo, mascaramento LGPD, linhagem e pipelines padronizados para que os domínios publiquem produtos de dados sem atrito.
4. **Federated Computational Governance:** regras globais (LGPD, criptografia, nomenclatura, retenção) aplicadas de forma automatizada via políticas como código em todos os domínios.
