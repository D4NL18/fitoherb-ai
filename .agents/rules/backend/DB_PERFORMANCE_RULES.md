# Regras de Performance e Banco de Dados ⚡

**ATENÇÃO AGENTES DE BACKEND, DBA E REVIEWERS:**
O código deve ser desenhado para suportar milhões de linhas amanhã, mesmo que hoje tenha dez.

## 1. O Problema do N+1
- ❌ **Consultas em Loop:** É TERMINANTEMENTE PROIBIDO iterar sobre uma lista e fazer uma chamada ao banco de dados dentro do loop (ex: iterar sobre 50 pedidos e buscar o nome do cliente 50 vezes separadas no banco).
- ✅ **A Solução:** Colete todos os IDs necessários e faça uma única consulta usando as cláusulas `IN (ids)` ou utilize `JOINs/Eager Loading` otimizados no seu ORM (ex: `JOIN FETCH` no Hibernate ou `.populate()` no Mongoose).

## 2. Volume de Tráfego e Paginação
- ❌ **O Mortal `SELECT *` Sem Limites:** Nenhuma rota ou método de repositório que retorne uma "lista" de registros pode existir sem controle de paginação. Se o cliente pedir "todos os produtos", a API deve proteger a memória retornando os primeiros `N`.
- ✅ **A Solução:** Sempre requeira e aplique `limit` (tamanho da página) e `offset` (ou cursor). Retorne ao Frontend os metadados para navegação (`totalItems`, `totalPages`).

## 3. Índices Estruturais
- ❌ **Chaves Estrangeiras "Nuas":** Nunca crie uma Tabela/Migration contendo uma `Foreign Key` que aponta para outra tabela sem criar imediatamente um Índice (`Index`) nessa coluna de FK. A ausência desses índices é a principal causa de lentidão e "Table Locks" durante exclusões massivas.
