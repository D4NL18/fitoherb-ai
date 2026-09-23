# Regras de Governança de Design System & Design Plans 🎨📏

**ATENÇÃO DESIGNER, DESENVOLVEDOR E UX REVIEWER:**
A consistência visual e o acabamento premium da aplicação exigem disciplina rigorosa na aplicação dos padrões de design.

---

## 1. Proibição Terminante de Valores Mágicos de CSS/SCSS
- ❌ **Cores e Paddings Arbitrários:** É PROIBIDO escrever valores como `color: #333333;`, `padding: 13px;`, `border-radius: 7px;` ou `margin-top: 27px;` soltos nos arquivos de folha de estilo ou tags HTML.
- ✅ **A Solução:** Todo valor de cor, tipografia, raio de borda, sombra e espaçamento DEVE consumir estritamente as variáveis declaradas no Design System (ex: `var(--color-primary)`, `var(--space-4)`, `var(--radius-md)`).

---

## 2. Obrigatoriedade do Design Plan Antes da Codificação
- ❌ **Programar Tela Sem Especificação Visual:** É expressamente VETADO ao Desenvolvedor iniciar a criação de componentes ou páginas de Frontend sem que o Designer tenha produzido e aprovado o **Design Plan** da funcionalidade em `.agents/docs/design/plans/<feature>.md`.
- ✅ **A Solução:** O Orquestrador e o Reviewer devem conferir a existência do Design Plan antes de aceitar qualquer código de frontend na esteira.

---

## 3. Conformidade com o Filtro Anti-IA (`UI_ANTI_PATTERNS.md`)
- Todo Design Plan e toda implementação em código DEVE respeitar as regras anti-slop:
  1. Proibido gradiente azul-roxo ("AI Purple").
  2. Proibido layout mecânico de 3 colunas com ícones de foguete/engrenagem.
  3. Proibido o uso solitário de Inter ou Roboto sem font-pairing distinto para títulos.
  4. Proibido spinner de carregamento isolado; a implementação de **Skeleton Loaders** é obrigatória.
  5. Proibido telas ou listas vazias em branco; a implementação de **Empty States** ricos é obrigatória.

---

## 4. Acessibilidade e Contraste (WCAG AA)
- Todos os textos normais devem ter razão de contraste mínima de `4.5:1` contra o fundo.
- Todos os elementos interativos devem possuir estados de `:focus-visible` com anel de foco bem demarcado para navegação por teclado.
