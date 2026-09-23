# Regras de Acessibilidade (A11y) ♿

**ATENÇÃO DESIGNERS, DESENVOLVEDORES E UX REVIEWERS:**
Acessibilidade não é opcional. Uma interface não é utilizável se não puder ser acessada por leitores de tela ou navegada via teclado.

## 1. Navegação por Teclado e Foco
- ❌ **Sem Outline de Foco:** NUNCA remova o contorno visual padrão de foco (`outline: none`) sem fornecer uma alternativa clara (como um `box-shadow` no estado `:focus-visible`).
- ❌ **Focus Trap Inexistente:** Modais, Dropdowns e Menus laterais abertos DEVEM prender a navegação do `<Tab>` dentro deles. O usuário não deve conseguir focar em elementos "atrás" do modal.
- ✅ **A Solução:** Use diretivas ou bibliotecas robustas para garantir o "Focus Trap" e gerencie os atributos de acessibilidade (ARIA) dinamicamente (`aria-expanded`, `aria-hidden`).

## 2. Rótulos e Semântica (ARIA)
- ❌ **Botões Invisíveis aos Leitores:** É estritamente proibido criar botões que contêm apenas um ícone (ex: `X` para fechar ou lupa de busca) sem nenhum texto.
- ✅ **A Solução:** Todo botão interativo sem texto visível DEVE obrigatoriamente ter a propriedade `aria-label` ou uma tag `sr-only` (Screen Reader Only).
  - Ex: `<button aria-label="Fechar Modal"> <Icon name="close"/> </button>`.

## 3. Contraste Visual e Cores
- ❌ **Aviso Baseado Apenas em Cor:** Não passe mensagens de erro ou sucesso dependendo exclusivamente da cor (ex: texto verde ou vermelho isolado), pois usuários daltônicos não distinguirão. Sempre coloque um ícone (Check/Alerta) junto com o texto.
- ✅ **Contraste WCAG AA:** Garanta que a taxa de contraste entre o fundo e o texto alcance, no mínimo, `4.5:1` para texto normal, seguindo a certificação WCAG AA. Textos esmaecidos (gray) em fundos claros (white) costumam falhar nisso.
