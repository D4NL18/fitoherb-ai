---
description: "Use quando implementar, refatorar ou revisar arquitetura backend, Clean Code, tratamento de excecoes, contratos REST (envelope data/meta) e performance de banco de dados."
trigger: model_decision
---

# Regras de Arquitetura Backend, Clean Code & Performance 🏛️⚡

**ATENÇÃO ARQUITETOS, DESENVOLVEDORES, DBAs E REVIEWERS:**
A aplicação deve ser desenhada para escalabilidade, manutenibilidade e baixo acoplamento.

---

## 1. Isolamento Rígido de Regras de Negócio (Clean Architecture)
- ❌ **Controllers com Lógica de Negócio:** É PROIBIDO injetar regras de negócio ("se valor > X calcule Y e salve") diretamente em Controllers ou Route Handlers.
- ✅ **A Solução:** Controllers apenas recebem o input, invocam Use Cases/Services e devolvem o output transformado. O "Se, E, Ou" reside exclusivamente na camada de domínio.
- ❌ **Acoplamento ORM no Domínio:** A regra de negócio principal não deve depender de métodos diretos de persistência ou drivers nativos. O acesso a dados deve ser desacoplado via *Repository Pattern*.

---

## 2. Padrões de Clean Code & Baixa Complexidade Cognitiva
- ❌ **Código Hadouken (Deep Nesting):** Proibido criar código com mais de 2 níveis de aninhamento de `if/else`.
- ✅ **Early Return (Fail Fast):** Toda função DEVE adotar *Early Return*. Inverta as condições e encerre antecipadamente caminhos de exceção/validação logo nas primeiras linhas.
- ❌ **God Functions (> 35-40 linhas):** Funções longas que fazem validação, cálculo e persistência violam o *Single Responsibility Principle*. Divida em sub-funções semânticas e autoexplicativas.
- ❌ **Magic Numbers & Nomes Enigmáticos:** Proibido usar números literais (`status === 2`) ou abreviações obscuras (`let a`, `usr`). Extraia constantes/enums declarativos e use booleanos com prefixos claros (`isActive`, `hasPermission`, `canExecute`).
- ❌ **Mais de 3 Parâmetros:** Funções com 4 ou mais argumentos devem agrupá-los em um único DTO/Interface tipada.

---

## 3. Tratamento Explícito de Erros & Exceções Semânticas
- ❌ **Try/Catch Silencioso ou Genérico:** Proibido engolir erros (`catch (e) {}`) ou lançar a classe genérica `Error("erro")` para violações de negócio.
- ✅ **Exceções de Domínio:** Crie classes semânticas herdadas (ex: `NotFoundException`, `BusinessRuleException`).
- ✅ **Códigos Internos Semânticos:** Toda resposta de erro de domínio deve incluir um código interno único: formato `PREFIX_TRES_LETRAS-NUMERO` (ex: `FIN-001`, `AUTH-004`).
- ✅ **Global Exception Handler:** Centralize o mapeamento de exceções em middleware global (`@RestControllerAdvice` no Spring Boot ou Exception Handler no FastAPI), evitando repetição de `try/catch` em controllers.

---

## 4. Contratos de API REST (Envelope Padrão)
- ❌ **Respostas Soltas ou Falso 200:** Proibido retornar arrays ou objetos soltos na raiz sem envelope, e terminantemente vetado retornar HTTP 200 com `{ "success": false }` em caso de erro.
- ✅ **Envelope Obrigatório:**
  ```json
  {
    "data": { "id": "123", "name": "Item" },
    "meta": { "timestamp": "2026-10-29T20:00:00Z", "page": 1, "total": 50 }
  }
  ```
- ✅ **Semântica HTTP Rigorosa:** Use 400 (validação), 401 (sem autenticação), 403 (sem permissão), 404 (não encontrado), 409 (conflito de recurso), 422 (regra de negócio violada). Mantenha padrão de casing uniforme (camelCase ou snake_case).

---

## 5. Performance de Banco de Dados & Anti-N+1
- ❌ **Problema do N+1:** Proibido iterar sobre listas e disparar queries ao banco dentro do loop.
- ✅ **Eager Loading e Batch:** Utilize cláusulas `IN (:ids)`, `JOIN FETCH` (JPA) ou `.includes()`/`.populate()` para carregar relacionamentos em lote.
- ❌ **Consultas Sem Limite:** Toda rota ou query que retorne coleções DEVE implementar paginação obrigatória com `limit` e `offset` (ou cursor).
- ✅ **Índices Estruturais:** Toda chave estrangeira (FK) e campos usados frequentemente em filtros e ordenações DEVEM possuir índices criados na migration.
