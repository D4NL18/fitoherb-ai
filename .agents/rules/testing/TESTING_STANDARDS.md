# Padrões Rígidos de Testes de Software 🧪

**ATENÇÃO TESTER E QA:**
Testes escritos apenas para "atingir a meta de 80% de cobertura" e testar apenas o "caminho feliz" são código morto. Siga estas diretrizes.

## 1. Estruturação AAA (Arrange, Act, Assert)
- ❌ **Teste Bagunçado:** Não faça blocos gigantescos de código.
- ✅ **A Solução:** Separe VISUALMENTE cada teste unitário nas 3 etapas lógicas, deixando um espaço/comentário entre elas:
  - **Arrange (Preparar):** Instanciação das classes e Mocks.
  - **Act (Agir):** A chamada única ao método que está sendo testado.
  - **Assert (Validar):** As checagens (`expect`, `assertEquals`) para garantir o retorno.

## 2. Proibição de Falsos Positivos (Isolamento)
- ❌ **Testes Integrados Acidentais:** Um teste unitário NUNCA deve encostar em recursos de rede, banco de dados real (mesmo que de teste na nuvem), ou ler arquivos físicos não-mockados.
- ✅ **A Solução:** Utilize **Mocks** (e Stubs/Spies) rigorosamente para simular a camada de repositório, APIs externas ou o sistema de arquivos.

## 3. O Foco nos Casos Extremos (Edge Cases)
- ❌ **Teste "Caminho Feliz" Exclusivo:** Um pull request será REJEITADO se a suíte de testes verificar apenas o cenário onde o usuário preencheu tudo certo.
- ✅ **A Solução:** Você DEVE prever a quebra e criar cenários agressivos:
  1. O que acontece se a string vier `null` ou vazia `""`?
  2. O que acontece se a API externa demorar ou retornar `500` (Simulação de Timeout)?
  3. O que acontece se o array passado estiver vazio `[]`?
  4. Números negativos em cálculos financeiros ou quantitativos.
