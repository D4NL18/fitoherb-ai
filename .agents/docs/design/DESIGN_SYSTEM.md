# Design System Oficial da Aplicação 🎨✨

> **Localização Mandatória:** `.agents/docs/design/DESIGN_SYSTEM.md`  
> **Status:** Ativo / Vivo  
> **Responsável:** Designer (`designer.md`) / `uiux-expert`  
> **Auditor:** UX Reviewer (`ux_reviewer.md`)  
> **Regras de Governança:** `.agents/rules/frontend/UI_ANTI_PATTERNS.md` e `.agents/rules/frontend/DESIGN_SYSTEM_RULES.md`

---

## 1. Princípios de Identidade Visual (Filtro Anti-IA)

> [!IMPORTANT]
> **Padrão Anti-IA:** Esta aplicação segue estética *Soft SaaS Premium*. É terminantemente proibido o uso de gradientes azul-roxo ("AI Purple"), sombras pretas duras, arredondamento indiscriminado sem hierarquia e templates clichês de IA (como 3 colunas rígidas com ícones de foguete ou formas 3D flutuantes). Toda interface deve priorizar assimetria intencional, tipografia editorial emparelhada e respiro visual.

- **Identidade:** Clean, Confiável, Tecnológica e Humana.
- **Tipografia:** Pareamento expressivo entre títulos geométricos modernos e corpo com legibilidade cristalina.
- **Contraste:** Acessibilidade universal WCAG AA em todas as combinações de cor e texto.

---

## 2. Paleta de Cores Oficial

### 2.1. Neutros Profundos (Escala Slate Curada)
*Substitui pretos absolutos por tons ricos com saturação sutil.*

| Token | Valor HEX | Aplicação |
| :--- | :--- | :--- |
| `--color-neutral-50` | `#F8FAFC` | Background de página (Light Mode) |
| `--color-neutral-100` | `#F1F5F9` | Superfícies secundárias, headers de tabelas, inputs |
| `--color-neutral-200` | `#E2E8F0` | Linhas divisórias e bordas sutis |
| `--color-neutral-300` | `#CBD5E1` | Bordas de botões outline e separadores |
| `--color-neutral-400` | `#94A3B8` | Ícones secundários e textos terciários |
| `--color-neutral-500` | `#64748B` | Placeholders e legendas de suporte |
| `--color-neutral-600` | `#475569` | Rótulos de formulário (labels) |
| `--color-neutral-700` | `#334155` | Textos de corpo em fundos claros |
| `--color-neutral-800` | `#1E293B` | Superfície de cartões no modo escuro |
| `--color-neutral-900` | `#0F172A` | Títulos e texto principal (Light Mode) |
| `--color-neutral-950` | `#020617` | Fundo principal profundo (Dark Mode) |

### 2.2. Cores da Marca e Funcionais
*Cores selecionadas para transmitir autoridade sem cair no roxo genérico de IA.*

| Categoria | Token | HEX | Aplicação |
| :--- | :--- | :--- | :--- |
| **Marca Primária** | `--color-primary` | `#0D9488` (Teal 600) | Ações principais, links de navegação ativa e botões |
| **Primária Hover** | `--color-primary-hover` | `#0F766E` (Teal 700) | Estado hover com transição suave de 200ms |
| **Primária Sutil** | `--color-primary-subtle` | `#F0FDFA` (Teal 50) | Badges de status e seleção de itens em listas |
| **Acento / Conversão** | `--color-accent` | `#F59E0B` (Amber 500) | Pontos focais de atenção e badges de destaque |
| **Sucesso** | `--color-success` | `#10B981` (Emerald 500) | Confirmações e badges de status aprovado |
| **Sucesso Fundo** | `--color-success-bg` | `#ECFDF5` (Emerald 50) | Alertas e banners de sucesso |
| **Alerta** | `--color-warning` | `#F59E0B` (Amber 500) | Advertências e estados pendentes |
| **Alerta Fundo** | `--color-warning-bg` | `#FFFBEB` (Amber 50) | Alertas e caixas de atenção |
| **Erro / Destrutivo** | `--color-danger` | `#EF4444` (Red 500) | Falhas, exclusões e campos com erro |
| **Erro Fundo** | `--color-danger-bg` | `#FEF2F2` (Red 50) | Banners de erro e toasts destrutivos |

---

## 3. Tipografia Modular (Font Pairing)

- **Display / Títulos:** `'Plus Jakarta Sans'`, sans-serif (pesos 600, 700, 800).
- **Corpo de Texto (Body):** `'Inter'`, sans-serif (pesos 400, 500).
- **Código / Números:** `'JetBrains Mono'`, monospace.

### Escala de Tamanhos e Entrelinha
- **Display H1:** `2.5rem` (40px) | Line-height: `1.2` | Tracking: `-0.025em` | Peso: 800
- **H2 (Seção):** `1.875rem` (30px) | Line-height: `1.25` | Tracking: `-0.020em` | Peso: 700
- **H3 (Card Title):** `1.25rem` (20px) | Line-height: `1.35` | Tracking: `-0.010em` | Peso: 600
- **H4 (Subtítulo):** `1.125rem` (18px) | Line-height: `1.40` | Tracking: `0` | Peso: 600
- **Body Regular:** `1.00rem` (16px) | Line-height: `1.50` | Tracking: `0` | Peso: 400
- **Body Small:** `0.875rem` (14px) | Line-height: `1.45` | Tracking: `+0.005em` | Peso: 400 / 500
- **Caption / Tag:** `0.75rem` (12px) | Line-height: `1.40` | Tracking: `+0.035em` | Peso: 600

---

## 4. Espaçamento (8pt Grid System)

- `--space-1`: `4px` (Micro-gap)
- `--space-2`: `8px` (Gap pequeno entre chips e ícones)
- `--space-3`: `12px` (Padding interno compacto)
- `--space-4`: `16px` (Padding de botões normais, gap entre inputs)
- `--space-5`: `20px` (Padding de cards leves)
- `--space-6`: `24px` (Padding padrão de containers e modais)
- `--space-8`: `32px` (Distância entre seções e blocos)
- `--space-10`: `40px` (Margem de cabeçalhos de tela)
- `--space-12`: `48px` (Espaço de respiro editorial)
- `--space-16`: `64px` (Margens amplas de respiro)

---

## 5. Bordas, Radius e Sombras

### Radius Hierárquico
- `--radius-sm`: `4px` (Badges, tags)
- `--radius-md`: `8px` (Inputs, botões normais, dropdowns)
- `--radius-lg`: `12px` (Cards, painéis de conteúdo)
- `--radius-xl`: `16px` (Modais e popovers principais)
- `--radius-full`: `9999px` (Pills, avatares)

### Sombras Suaves (Low-Opacity Layered Shadows)
- **Nível 1 (Card sutil):** `box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.05), 0 1px 2px -1px rgba(15, 23, 42, 0.05);`
- **Nível 2 (Hover):** `box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.07), 0 2px 4px -2px rgba(15, 23, 42, 0.05);`
- **Nível 3 (Dropdown/Popover):** `box-shadow: 0 10px 15px -3px rgba(15, 23, 42, 0.08), 0 4px 6px -4px rgba(15, 23, 42, 0.04);`
- **Nível 4 (Modais Centrais):** `box-shadow: 0 20px 25px -5px rgba(15, 23, 42, 0.10), 0 8px 10px -6px rgba(15, 23, 42, 0.05);`

---

## 6. Componentes e Padrões de Interação

### 6.1. Botões
- Micro-interação em hover: `transform: translateY(-1px);` com `transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);`.
- Focus visível: Anel com `outline: 2px solid var(--color-primary); outline-offset: 2px;`.

### 6.2. Skeleton Loaders (Proibido Spinner Isolado)
- Animação Shimmer em cinza sutil (`#F1F5F9` para `#E2E8F0`) emulando a geometria dos elementos que estão sendo carregados.

### 6.3. Empty States
- Sempre composto por: Ilustração ou ícone contextualizado em caixa com `--color-neutral-100`, título amigável, texto orientador e CTA de ação imediata.

---

## 7. Folha de Tokens em CSS (:root)

```css
:root {
  --color-neutral-50: #F8FAFC;
  --color-neutral-100: #F1F5F9;
  --color-neutral-200: #E2E8F0;
  --color-neutral-300: #CBD5E1;
  --color-neutral-400: #94A3B8;
  --color-neutral-500: #64748B;
  --color-neutral-600: #475569;
  --color-neutral-700: #334155;
  --color-neutral-800: #1E293B;
  --color-neutral-900: #0F172A;
  --color-neutral-950: #020617;

  --color-primary: #0D9488;
  --color-primary-hover: #0F766E;
  --color-primary-subtle: #F0FDFA;
  --color-accent: #F59E0B;
  --color-success: #10B981;
  --color-success-bg: #ECFDF5;
  --color-warning: #F59E0B;
  --color-warning-bg: #FFFBEB;
  --color-danger: #EF4444;
  --color-danger-bg: #FEF2F2;

  --font-family-display: 'Plus Jakarta Sans', sans-serif;
  --font-family-body: 'Inter', sans-serif;
  --font-family-mono: 'JetBrains Mono', monospace;

  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;

  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-full: 9999px;

  --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-normal: 250ms cubic-bezier(0.4, 0, 0.2, 1);
}
```
