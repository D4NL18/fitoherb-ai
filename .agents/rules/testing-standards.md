---
description: "Use quando escrever, revisar ou executar testes automatizados (unitarios, integracao, contrato, E2E), TDD, mocks, cobertura ou Auto-Healer de testes."
trigger: model_decision
---

# Padrões Rígidos de Testes de Software 🧪✅

**ATENÇÃO TESTER, QA, DESENVOLVEDORES E REVIEWERS:**
A suíte de testes automatizados é a salvaguarda de qualidade do sistema. Testes frágeis ou viciados apenas no "caminho feliz" são código morto.

---

## 1. Disciplina TDD First (Test-Driven Development)
- ✅ **Testes Antes da Lógica:** Os testes unitários e de contrato DEVEM ser escritos antes de qualquer linha de lógica produtiva. O teste deve falhar inicialmente (Red), ser satisfeito pela implementação mínima (Green) e refatorado em seguida (Refactor).

---

## 2. Estruturação AAA (Arrange, Act, Assert)
- ❌ **Testes Monolíticos e Desordenados:** É proibido misturar instanciações, múltiplas invocações e checagens dispersas.
- ✅ **A Separação Visual:** Divida visualmente cada teste em 3 blocos bem definidos:
  1. **Arrange (Preparação):** Configuração de mocks, stubs e dados de entrada.
  2. **Act (Ação):** A chamada única ao método ou endpoint sob teste.
  3. **Assert (Verificação):** As asserções estritas dos retornos e efeitos colaterais esperados.

---

## 3. Isolamento Estrito & Proibição de Falsos Positivos
- ❌ **I/O Oculto em Teste Unitário:** Testes unitários NUNCA devem acessar conexões reais de rede, banco de dados ou sistemas de arquivos sem mock.
- ✅ **Mocks Determinísticos:** Isole dependências externas via mocks limpos (Mockito no Spring Boot / `unittest.mock` no Python / Jasmine-Jest no Angular), garantindo tempo de execução em milissegundos e reprodutibilidade independente de infraestrutura.

---

## 4. Foco Prioritário em Edge Cases (Cenários Extremos)
- ❌ **Falso Sucesso (Testar Apenas Caminho Feliz):** Um Pull Request será sumariamente REJEITADO se a suíte de testes cobrir apenas entradas válidas perfeitas.
- ✅ **Cenários Adversos Mandatórios:** Todo teste deve validar o comportamento da aplicação sob:
  1. Parâmetros nulos (`null`/`None`), strings vazias (`""`) ou fora de padrão.
  2. Simulação de falha de dependência externa (Timeouts, HTTP 500, conexão recusada).
  3. Coleções vazias (`[]`) ou coleções com limite máximo de paginação.
  4. Valores numéricos extremos, negativos e divisões por zero.
