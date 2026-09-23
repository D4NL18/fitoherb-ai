# Regras de Negócio: [Nome da Funcionalidade/Módulo]

> **Localização Mandatória:** `.agents/docs/business_rules/<nome-da-feature>.md`  
> **Responsável:** Analista (`business-rules-expert`)  
> **Referências de Regras:** `.agents/rules/architecture/BUSINESS_LOGIC_ISOLATION_RULES.md`

---

## 1. Contexto e Objetivo
- **User Story Relacionada:** [Ex: US-01 - Cadastro de Usuários]
- **Objetivo da Feature:** [Descrição clara e enxuta do que a funcionalidade deve entregar ao usuário final.]
- **Atores Envolvidos:** [Ex: Administrador, Cliente Autenticado, Sistema Externo]

---

## 2. Catálogo de Regras de Negócio (P-XXX)

> [!IMPORTANT]
> Toda regra individual DEVE receber um identificador sequencial `P-XXX`. Esse identificador será referenciado nos testes de unidade (TDD), nas mensagens de commit do Desenvolvedor e no PR.

### `P-001`: [Título Curto da Regra]
- **Declaração Mandatória:** O sistema DEVE / NÃO DEVE [descreva o comportamento imperativo exato].
- **Condições de Ativação:** Quando [condição ou evento de disparo].
- **Resultado Esperado:** [O que o sistema faz quando a condição é atendida].
- **Exceção / Mensagem de Erro:** Caso não atendida, lançar erro HTTP [400/422] com mensagem: `"[Mensagem de erro amigável ao usuário]"`.

### `P-002`: [Título Curto da Regra]
- **Declaração Mandatória:** O sistema DEVE validar [regrando formato, limites numéricos ou restrições].
- **Condições de Ativação:** [Condição de disparo].
- **Resultado Esperado:** [Comportamento do sistema].
- **Exceção / Mensagem de Erro:** Código HTTP [400/422] com mensagem: `"[Mensagem de erro amigável ao usuário]"`.

---

## 3. Enquadramento LGPD & Privacidade (Art. 7º e 11 da LGPD)

> [!NOTE]
> Obrigatório sempre que a funcionalidade coletar, consultar, processar ou armazenar dados de pessoas físicas.

| Dado / Atributo | Classificação LGPD | Base Legal Aplicada | Finalidade Específica e Proporcional |
| :--- | :--- | :--- | :--- |
| `[Ex: email]` | Dado Pessoal | Execução de Contrato (Art. 7º, V) | Comunicação de status de pedido e autenticação. |
| `[Ex: cpf]` | Dado Pessoal | Obrigação Legal (Art. 7º, II) | Emissão de Nota Fiscal perante a Receita Federal. |
| `[Ex: biometria/saúde]`| Dado Pessoal Sensível | Consentimento Específico (Art. 11, I) | Validação de segurança reforçada e histórico clínico. |

---

## 4. Matriz de Cenários e Edge Cases

| ID | Cenário / Entrada | Comportamento Esperado | Código HTTP |
| :--- | :--- | :--- | :--- |
| **C-01** | Dados válidos e completos | Registra com sucesso e retorna status `ACTIVE` | `201 Created` |
| **C-02** | Campo obrigatório ausente | Retorna lista de campos inválidos | `400 Bad Request` |
| **C-03** | Registro já existente (duplicidade) | Bloqueia operação informando conflito | `409 Conflict` |
| **C-04** | Violação de regra de negócio (`P-001`) | Bloqueia operação com detalhamento | `422 Unprocessable` |

---

## 5. Critérios de Aceitação (DoD - Definition of Done)
- [ ] Todas as regras `P-XXX` mapeadas possuem testes unitários automatizados com cobertura >= 80%.
- [ ] Dicionário de termos está 100% alinhado a `.agents/skills/domain-expert/GLOSSARY.md`.
- [ ] Enquadramento LGPD e bases legais formalizados para dados pessoais manipulados.
- [ ] Não há vazamento de lógica de negócio para a camada de controllers/routers.
