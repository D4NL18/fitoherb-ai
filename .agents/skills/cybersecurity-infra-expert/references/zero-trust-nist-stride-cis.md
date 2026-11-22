# Referência: Zero Trust, NIST CSF 2.0, STRIDE, Controles CIS e Resiliência (RTO/RPO)

Este guia de referência consolida os frameworks de cibersegurança corporativa e defesa de infraestrutura para revisões arquiteturais, auditorias de segurança e planos de continuidade de negócios.

---

## 1. Arquitetura Zero Trust (NIST SP 800-207)

O modelo **Zero Trust Architecture (ZTA)** elimina a confiança implícita baseada em localização de rede (VPN ou intranet).

### Pilares Operacionais
1. **Identidade Forte (Humanos e Workloads):**
   - Humanos: SSO + MFA resistente a phishing (FIDO2/WebAuthn), acesso condicional por postura do dispositivo.
   - Workloads/Serviços: identidades criptográficas de curta duração (Workload Identity Federation, SPIFFE/SPIRE, mTLS), eliminando chaves estáticas de longa duração.
2. **Menor Privilégio Dinâmico (PoLP + JIT/JEA):**
   - Permissões concedidas *Just-in-Time* (expiram automaticamente) e *Just-Enough-Access* (escopo mínimo por recurso).
3. **Microsegmentação e Assume Breach:**
   - Políticas de rede *default-deny* entre namespaces/VPCs.
   - Criptografia obrigatória em trânsito (TLS 1.3 / mTLS) e em repouso (AES-256 com chaves gerenciadas em KMS/HSM com rotação automática).

---

## 2. NIST Cybersecurity Framework (CSF) 2.0

A versão 2.0 elevou **Govern (GV)** a função central que permeia todas as demais:

| Função | Objetivo Central | Controles e Artefatos Chave |
| :--- | :--- | :--- |
| **1. Govern (GV)** | Estabelecer contexto organizacional, apetite a risco, papéis e gestão de risco na cadeia de suprimentos (SCRM). | Política de Segurança, Matriz RACI, avaliação de terceiros/SaaS, métricas para o Board. |
| **2. Identify (ID)** | Conhecer ativos, dados, fluxos e vulnerabilidades. | Inventário automatizado (CMDB/CSPM), classificação de dados, SBOM, modelagem de ameaças. |
| **3. Protect (PR)** | Reduzir probabilidade e impacto de eventos adversos. | IAM/MFA, criptografia, hardening, SAST/SCA no CI/CD, WAF, treinamento seguro. |
| **4. Detect (DE)** | Descobrir ataques e anomalias rapidamente. | SIEM centralizado, EDR/CWPP, alertas de anomalia de IAM, logs estruturados imutáveis. |
| **5. Respond (RS)** | Conter, erradicar e comunicar incidentes de forma coordenada. | Playbooks SOAR, plano de comunicação (incl. ANPD/reguladores), war room e forense. |
| **6. Recover (RC)** | Restaurar operações com segurança e incorporar lições aprendidas. | Backups imutáveis (air-gapped/WORM), testes periódicos de DR, validação de integridade pós-restore. |

---

## 3. Modelagem de Ameaças STRIDE

Aplique STRIDE sobre cada componente e fluxo de dados (DFD — *Data Flow Diagram*) que cruza uma **fronteira de confiança (Trust Boundary)**:

- **S — Spoofing (Falsificação de Identidade):** um atacante se passa por usuário ou serviço legítimo.
  - *Controles:* OIDC/OAuth2 com PKCE, MFA, JWT com `RS256`/`EdDSA` + validação de `iss`/`aud`/`exp`, mTLS.
- **T — Tampering (Adulteração de Dados):** modificação indevida de payload, banco ou artefato de build.
  - *Controles:* TLS 1.3, assinatura HMAC em webhooks, validação estrita de schema (DTO/Pydantic), artefatos assinados (Cosign/SLSA).
- **R — Repudiation (Repúdio):** negação de uma ação executada no sistema.
  - *Controles:* Audit trail imutável (append-only/WORM), correlation ID, carimbo de tempo sincronizado (NTP), logs assinados.
- **I — Information Disclosure (Vazamento de Informação):** exposição de PII, segredos ou detalhes internos.
  - *Controles:* Criptografia em repouso/trânsito, mascaramento em logs, remoção de stacktraces em produção, headers de segurança (`HSTS`, `CSP`).
- **D — Denial of Service (Negação de Serviço):** indisponibilização de API, banco ou fila.
  - *Controles:* Rate limiting por IP/tenant, WAF/Cloud Armor, timeouts, circuit breakers, limites de payload e paginação obrigatória.
- **E — Elevation of Privilege (Elevação de Privilégio):** usuário comum executa ação administrativa ou acessa recurso de outro tenant (BOLA/IDOR).
  - *Controles:* Checagem de autorização no servidor por recurso (`tenant_id` / `owner_id` extraído do token, nunca do body), RBAC/ABAC.

---

## 4. Controles CIS (v8) Prioritários para Engenharia

1. **CIS 1 e 2 (Inventário de Ativos e Software):** rastrear todos os containers, APIs e dependências (SBOM).
2. **CIS 3 (Proteção de Dados):** classificação, retenção, criptografia e DLP.
3. **CIS 5 e 6 (Contas e Controle de Acesso):** MFA universal, revisão periódica de privilégios, zero contas compartilhadas.
4. **CIS 7 (Gestão Contínua de Vulnerabilidades):** SLA de correção por severidade (Crítica: 24–72h; Alta: 7–15 dias).
5. **CIS 8 (Audit Log Management):** retenção centralizada sem PII sensível, sincronizada e protegida contra alteração.
6. **CIS 11 (Data Recovery):** regra **3-2-1-1-0** (3 cópias, 2 mídias, 1 offsite, 1 imutável/offline, 0 erros em testes de restauração).

---

## 5. Resiliência Operacional: RTO, RPO e Estratégias de DR

| Estratégia de DR | RTO Típico | RPO Típico | Custo Relativo | Quando Usar |
| :--- | :--- | :--- | :---: | :--- |
| **Backup & Restore** | Horas a dias | Horas | $ | Sistemas não críticos / ambientes internos |
| **Pilot Light** | Dezenas de minutos | Minutos | $$ | Serviços importantes com orçamento controlado |
| **Warm Standby** | Minutos (< 15 min) | Segundos a minutos | $$$ | Aplicações core de negócio (Tier-1) |
| **Multi-Site Active-Active** | Próximo de zero | Próximo de zero | $$$$ | Missão crítica global / pagamentos em tempo real |

> [!CAUTION]
> Um plano de Disaster Recovery que **nunca foi testado** não é um plano — é uma hipótese. Execute simulações de failover e restauração de backup periodicamente e registre o RTO/RPO real medido.
