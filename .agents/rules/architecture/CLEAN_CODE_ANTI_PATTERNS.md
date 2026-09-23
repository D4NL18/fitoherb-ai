# Anti-Padrões de Clean Code 🧹

**ATENÇÃO DESENVOLVEDORES, REVIEWERS E QA:**
O código é lido 10 vezes mais do que é escrito. Código "esperto" e de alta complexidade cognitiva será REJEITADO.

## 1. Early Return (O Fim do Código Hadouken)
- ❌ **Deep Nesting (Mais de 2 níveis):** É estritamente proibido criar "códigos flecha" onde lógicas de validação causam `if` dentro de `if` dentro de `if`.
- ✅ **A Solução (Fail Fast):** Toda função DEVE adotar o *Early Return*. Inverta as condições e expulse a lógica indesejada nas primeiras linhas da função.
  ```typescript
  // ❌ Errado:
  if (user != null) {
      if (user.isActive) { return doSomething(); }
  }
  
  // ✅ Certo:
  if (!user || !user.isActive) return;
  return doSomething();
  ```

## 2. O Limite de Responsabilidade (Tamanho das Funções)
- ❌ **God Functions:** Funções com mais de 30-40 linhas são inaceitáveis e indicam falta de abstração.
- ✅ **A Solução:** Divida o problema. Se uma função valida os dados, calcula taxas e salva no banco, ela está ferindo o princípio de *Single Responsibility*. Separe em sub-funções auto-explicativas.

## 3. Nomes Semânticos de Variáveis e Booleanos
- ❌ **Nomes Misteriosos:** Proibido usar siglas ou letras soltas (`let a`, `const usr`, `function clcTx()`).
- ❌ **Booleanos Ambíguos:** `is_ativo` ou `flag` não dizem nada.
- ✅ **A Solução:**
  - Seja prolixo se necessário: `function calculateMonthlyTaxesForPremiumUsers()`.
  - Prefixos Booleanos Obrigatórios: Todo booleano DEVE começar com verbos que indicam pergunta (ex: `isActive`, `hasPermission`, `shouldRender`, `canDelete`).

## 4. Números Mágicos (Magic Numbers)
- ❌ **Uso Literal no Código:** `if (status === 2)` ou `const max = 30;` espalhados pelo código dificultam a manutenção.
- ✅ **A Solução:** Extraia qualquer valor estático para Constantes ou Enums bem nomeados no topo do arquivo ou em um arquivo dedicado (`MAX_LOGIN_ATTEMPTS = 3`).

## 5. Limite de Parâmetros
- ❌ **Listas de Compras:** Funções que recebem 4, 5 ou mais parâmetros (ex: `createUser(name, email, age, role, password, isActive)`) são impossíveis de ler e altamente propensas a erros de ordem de passagem.
- ✅ **A Solução:** Se uma função precisa de mais de 3 parâmetros, englobe-os em um único Objeto (DTO ou Interface). Isso garante a passagem por nome e não por posição.
  ```typescript
  // Certo:
  createUser({ name: "Admin", email: "x@x", role: "admin" })
  ```

## 6. O Padrão de Comentários (Vibecoding Philosophy)
- ❌ **Comentários de Ruído:** Comentar "Inicia a variável i com 0" em um `let i = 0` é lixo visual.
- ❌ **Falta de Contexto:** Não explicar a motivação de uma função complexa.
- ✅ **A Solução Obrigatória:** O repositório exige alta densidade de comentários intencionais:
  1. **Topo da Página:** Todo arquivo deve ter um JSDoc/Comentário explicando qual o objetivo daquele módulo/componente.
  2. **Regras de Negócio:** Toda função ou variável central deve ter um comentário explicando *O QUE* faz e *POR QUE* faz.

## 7. YAGNI (You Aren't Gonna Need It)
- ❌ **Overengineering:** É PROIBIDO criar interfaces complexas genéricas, factories mirabolantes e abstrações de banco de dados para "suportar múltiplos bancos no futuro" se a tarefa atual exige apenas salvar um nome no Postgres.
- ✅ **A Solução:** Escreva a solução mais limpa e reta para o problema de *hoje*. Abstraia apenas quando o código doer ou duplicar pela terceira vez.

## 8. A Morte do Tipo `any` (TypeScript)
- ❌ **Tipagem Preguiçosa:** O uso do tipo `any` destrói a segurança de compilação que o TypeScript oferece e esconde bugs em tempo de execução. O uso de `any` em novos arquivos causa veto imediato no Code Review.
- ✅ **A Solução:** Se o formato de um dado é realmente desconhecido (ex: um payload de um webhook externo), utilize o tipo `unknown` e faça *Type Guards* ou verifique propriedades antes de acessar. Crie Interfaces/Types precisos para todo o resto.

## 9. A Lei de Demeter (Princípio do Menor Conhecimento)
- ❌ **Corrente de Objetos:** Fazer `pedido.getCliente().getEndereco().getCEP()` expõe fortemente a estrutura interna do objeto para o exterior, aumentando brutalmente o acoplamento.
- ✅ **A Solução:** Um módulo só deve acessar métodos dos seus objetos diretamente ligados. Exponha métodos facilitadores (ex: `pedido.getCEPCliente()`).
