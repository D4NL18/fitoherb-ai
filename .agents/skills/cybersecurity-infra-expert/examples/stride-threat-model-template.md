# Exemplo: Template de Modelagem de Ameaças STRIDE

> **Sistema / Feature:** [Ex.: API de Pagamentos Pix & Webhooks]  
> **Versão / Data:** v1.0 — [AAAA-MM-DD]  
> **Responsáveis:** [Arquiteto + SecOps + Tech Lead]  
> **Classificação dos Dados:** [Público / Interno / Confidencial / Restrito (PII/Financeiro)]

---

## 1. Escopo e Fronteiras de Confiança (Trust Boundaries)

```text
[Cliente Web/Mobile]
        |  (TLS 1.3 + Cookie HttpOnly / OAuth2)
=== Trust Boundary 1: Internet -> Borda ===
        v
[WAF / API Gateway] (Rate Limit + Validação JWT)
        |  (mTLS interno)
=== Trust Boundary 2: Borda -> Rede Privada ===
        v
[Serviço de Pagamentos] ---> [Banco PostgreSQL (AES-256)]
        |
        +---> [Webhook Parceiro Externo] (HMAC-SHA256)
```

---

## 2. Matriz de Ameaças STRIDE

| ID | Componente / Fluxo | Categoria STRIDE | Cenário de Ameaça | Severidade | Mitigação Técnica Obrigatória | Status |
| :--- | :--- | :---: | :--- | :---: | :--- | :---: |
| **TM-01** | API Gateway -> Serviço | **S** (Spoofing) | Chamada interna forjada se um pod vizinho for comprometido. | Alta | Exigir mTLS com Workload Identity e validação de audiência (`aud`) no token. | 🟢 Mitigado |
| **TM-02** | Webhook Parceiro -> API | **T** (Tampering) | Adulteração do valor/status do pagamento em trânsito ou replay attack. | Crítica | Validar assinatura `HMAC-SHA256` no header + timestamp (janela <= 5 min) + chave de idempotência. | 🟡 Em progresso |
| **TM-03** | Aprovação de Transação | **R** (Repudiation) | Usuário ou operador contesta autorização de transferência de alto valor. | Alta | Gravar audit log estruturado imutável (WORM) com `actor_id`, `correlation_id`, IP e timestamp UTC. | 🟢 Mitigado |
| **TM-04** | Logs da Aplicação | **I** (Info Disclosure) | Vazamento de CPF, chave Pix ou token em logs de erro ou stacktrace HTTP. | Crítica | Mascaramento automático de PII no logger; handler global retorna apenas código semântico sem stacktrace. | 🟢 Mitigado |
| **TM-05** | Endpoint `POST /pagamentos` | **D** (DoS) | Flood de requisições simultâneas esgotando pool de conexões do banco. | Alta | Rate limit por IP e por `tenant_id` no WAF/Gateway + fila assíncrona + circuit breaker. | 🟡 Em progresso |
| **TM-06** | Endpoint `GET /pagamentos/{id}` | **E** (Elevation) | Usuário autenticado consulta comprovante de outro cliente alterando `{id}` (BOLA/IDOR). | Crítica | Filtrar query obrigatoriamente por `id = :id AND tenant_id = :token_tenant_id`; teste automatizado de BOLA no CI. | 🟢 Mitigado |

---

## 3. Metas de Resiliência e Continuidade

- **RTO Alvo:** `< 15 minutos` (failover automatizado via IaC/DNS).
- **RPO Alvo:** `< 5 minutos` (replicação semissíncrona + PITR habilitado).
- **Último Teste de DR / Restore:** `[AAAA-MM-DD]` — Resultado: `[Aprovado / Pendente]`.

---

## 4. Critérios de Aprovação (Sign-off)

- [ ] Todas as ameaças de severidade **Crítica** e **Alta** possuem mitigação implementada ou plano com prazo aprovado.
- [ ] Testes automatizados de segurança (SAST, SCA, BOLA e validação de assinatura) adicionados ao pipeline CI.
- [ ] Nenhum segredo hardcoded; chaves gerenciadas via Secret Manager / KMS.
