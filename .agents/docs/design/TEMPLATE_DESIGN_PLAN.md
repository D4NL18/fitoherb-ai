# Design Plan: [Nome da Feature / Tela / Componente] 📐🎨

> **Localização Mandatória:** `.agents/docs/design/plans/<nome-da-feature>.md`  
> **Autor:** Designer (`designer.md`) / `uiux-expert`  
> **Auditor:** UX Reviewer (`ux_reviewer.md`)  
> **Executor:** Desenvolvedor (`developer.md`)  
> **Referências:** `.agents/docs/design/DESIGN_SYSTEM.md` e `.agents/rules/frontend/UI_ANTI_PATTERNS.md`

---

## 1. Identificação & Objetivo da Tarefa
- **User Story Relacionada:** [Ex: US-02 - Painel de Pacientes e Anamnese]
- **Objetivo de UX:** [O que o usuário deve conseguir realizar nesta tela de forma fluida, sem atrito e com clareza visual.]
- **Decisões do Brainstorming:** [Resumo das preferências alinhadas na sessão de brainstorming prévia com o usuário.]

---

## 2. Checklist Anti-IA (Filtro Anti-Slop Obrigatório)

> [!CAUTION]
> Se o design contiver qualquer um dos itens proibidos abaixo, o **UX Reviewer VETARÁ** a entrega no passo 9.

- [ ] **Sem "AI Purple":** Nenhum gradiente genérico azul-roxo utilizado.
- [ ] **Sem 3 Colunas Mecânicas:** Layout foge do padrão previsível de 3 colunas com ícones de foguete/engrenagem.
- [ ] **Tipografia com Font Pairing:** Títulos utilizam a fonte de display do Design System (`Plus Jakarta Sans`), enquanto textos usam `Inter` ou `DM Sans`.
- [ ] **White Space Ativo:** Margens e respiros amplos garantem que os elementos não fiquem sufocados.
- [ ] **Copywriting Humano:** Textos orientados à ação clara; zero buzzwords vazias como *"Empower"*, *"Seamless"*, *"Revolutionize"*.
- [ ] **Zero Spinners Solitários:** A tela possui especificação de **Skeleton Loaders Shimmer** para carregamento.
- [ ] **Zero Telas Brancas Vazias:** A tela possui **Empty State** desenhado com ilustração/ícone, mensagem amigável e botão de ação.

---

## 3. Tokens do Design System Aplicados nesta Tela

*O Desenvolvedor NÃO deve inventar valores hexadecimais ou paddings arbitrários. Use estritamente estes tokens:*

| Categoria | Tokens Utilizados | Valores Associados |
| :--- | :--- | :--- |
| **Cores de Superfície** | `--color-neutral-50`, `--color-neutral-100` | `#F8FAFC`, `#F1F5F9` |
| **Cores de Texto** | `--color-neutral-900`, `--color-neutral-600` | `#0F172A`, `#475569` |
| **Ação / Destaque** | `--color-primary`, `--color-primary-hover` | `#0D9488`, `#0F766E` |
| **Feedback** | `--color-danger`, `--color-success` | `#EF4444`, `#10B981` |
| **Espaçamentos** | `--space-2`, `--space-4`, `--space-6`, `--space-8` | `8px`, `16px`, `24px`, `32px` |
| **Bordas & Raios** | `--radius-md` (inputs/btns), `--radius-lg` (cards) | `8px`, `12px` |
| **Sombras** | Nível 1 (cards base), Nível 2 (hover) | Sombras sutis em camadas |

---

## 4. Anatomia dos Componentes e Layout

### 4.1. Hierarquia da Página
1. **Header da Feature:**
   - Título `H2` (`--font-family-display`), subtítulo com `--color-neutral-600`.
   - Ação principal alinhada à direita (`Button Primary`).
2. **Área de Conteúdo Principal:**
   - [Descreva os cards, listas, tabelas ou formulários].
3. **Barra Lateral / Detalhes (se aplicável):**
   - [Descreva elementos contextuais].

---

## 5. Matriz de Estados Visuais Obrigatórios

### 5.1. Estado Default (Ocioso)
- [Descrição visual dos elementos quando a tela carrega com sucesso com dados].

### 5.2. Estados Interativos (Hover, Active, Focus-Visible)
- **Botões:** Transição de `200ms`, elevação sutil `transform: translateY(-1px)` e escurecimento para `--color-primary-hover`.
- **Inputs:** Anel de foco com `outline: 2px solid var(--color-primary); outline-offset: 2px;`.

### 5.3. Estado de Carregamento (Loading com Skeleton Shimmer)
- Proibido rodinhas giratórias centralizadas.
- O layout deve espelhar a estrutura final com blocos de animação shimmer:
  - Header: 1 barra de `120px x 32px`.
  - Conteúdo: 3 cartões skeleton com dimensões idênticas às dos cards reais.

### 5.4. Estado Vazio (Empty State)
- Quando não houver dados cadastrados:
  - **Ícone / Ilustração:** Ícone temático contextualizado com fundo suave `--color-neutral-100`.
  - **Título:** `"[Nenhum registro encontrado]"`
  - **Texto explicativo:** `"Cadastre seu primeiro registro para visualizar métricas e relatórios."`
  - **Call-to-Action:** Botão Primário `"[+ Criar Registro]"`.

### 5.5. Estado de Erro / Falha de API
- Banner suave no topo com fundo `--color-danger-bg`, borda `--color-danger` e botão de *"Tentar Novamente"*, sem bloquear a navegação geral da aplicação.

---

## 6. Responsividade e Breakpoints

| Breakpoint | Comportamento do Layout |
| :--- | :--- |
| **Mobile (< 640px)** | Coluna única vertical, paddings laterais `--space-4` (16px), botões full-width |
| **Tablet (640px - 1024px)** | Grade de 2 colunas, menu recolhível |
| **Desktop (> 1024px)** | Grade balanceada com respiro amplo, paddings laterais `--space-8` (32px) |

---

## 7. Critérios de Aceite para UX Reviewer (DoD Visual)
- [ ] Todos os elementos utilizam estritamente as variáveis de `:root` definidas no `DESIGN_SYSTEM.md`.
- [ ] O componente possui Skeleton Shimmer implementado e funcional durante requests assíncronos.
- [ ] O Empty State foi implementado com ilustração, texto humano e botão de ação.
- [ ] Estados de `hover` e `focus-visible` estão presentes em todos os elementos clicáveis.
- [ ] Nenhuma violação do `UI_ANTI_PATTERNS.md` foi cometida.
