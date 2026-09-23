# Design System Oficial: [Nome do Projeto / Aplicação] 🎨✨

> **Localização Mandatória:** `.agents/docs/design/DESIGN_SYSTEM.md`  
> **Responsável:** Designer (`designer.md`) / `uiux-expert`  
> **Auditor:** UX Reviewer (`ux_reviewer.md`)  
> **Conformidade Obrigatória:** `.agents/rules/frontend/UI_ANTI_PATTERNS.md` e `.agents/rules/frontend/DESIGN_SYSTEM_RULES.md`

---

## 1. Princípios de Design & Identidade Visual (Anti-IA Slop)

> [!IMPORTANT]
> **Filtro Anti-IA:** Esta interface DEVE ter personalidade de marca e toque humano. É terminantemente proibido o uso de gradientes "AI Purple" (azul-roxo padrão), sombras artificiais pesadas, cartões simétricos repetitivos em 3 colunas com ícones de foguete, e fontes sem pareamento. Priorize assimetria editorial, espaços de respiro generosos (*Negative Space*) e contrastes sutis.

- **Vibe / Mood:** [Ex: Moderno, Sofisticado, Confiável, Editorial, Minimalista Refinado]
- **Arquétipo Visual:** [Ex: Clean B2B SaaS, Luxury Editorial, High-Tech Dark Mode]
- **Regra de Pareamento de Cores:** Paletas HSL com neutros profundos (Slate/Zinc) e cor de acento com identidade real.

---

## 2. Paleta de Cores (Color Palette & Semantics)

### 2.1. Escala Tonal de Neutros (Base & Superfícies)
*Nunca use preto puro `#000000` nem branco ofuscante cru para todas as áreas.*

| Token | Código HEX / HSL | Uso Primário |
| :--- | :--- | :--- |
| `--color-neutral-50` | `#F8FAFC` | Fundo principal da página (Light Mode) |
| `--color-neutral-100` | `#F1F5F9` | Superfícies secundárias, inputs e hover sutil |
| `--color-neutral-200` | `#E2E8F0` | Bordas e divisores discretos |
| `--color-neutral-300` | `#CBD5E1` | Bordas ativas e estados de hover em botões secundários |
| `--color-neutral-400` | `#94A3B8` | Ícones inativos e textos de suporte secundário |
| `--color-neutral-500` | `#64748B` | Placeholders e textos secundários |
| `--color-neutral-600` | `#475569` | Rótulos de formulário e subtítulos leves |
| `--color-neutral-700` | `#334155` | Textos de corpo em fundos claros |
| `--color-neutral-800` | `#1E293B` | Superfície de cartões no Dark Mode |
| `--color-neutral-900` | `#0F172A` | Texto primário (Light Mode) / Fundo secundário (Dark) |
| `--color-neutral-950` | `#020617` | Fundo principal (Dark Mode profundo) |

### 2.2. Cores da Marca e Funcionais
*Proibido usar gradientes de azul para roxo genéricos de IA.*

| Categoria | Token | Código HEX | Finalidade de Uso |
| :--- | :--- | :--- | :--- |
| **Marca Primária** | `--color-primary` | `#0D9488` (Teal 600) / `#4F46E5` | Ações principais, CTAs, botões primários |
| **Primária Hover** | `--color-primary-hover` | `#0F766E` / `#4338CA` | Hover refinado com transição de 200ms |
| **Primária Leve** | `--color-primary-subtle` | `#F0FDFA` / `#EEF2FF` | Badges de destaque e backgrounds de seleção |
| **Acento / Destaque** | `--color-accent` | `#F59E0B` (Amber) / `#E11D48` | Elementos de conversão e pontos focais |
| **Sucesso** | `--color-success` | `#10B981` (Emerald 500) | Confirmações, feedbacks positivos, badges ativos |
| **Sucesso Fundo** | `--color-success-bg` | `#ECFDF5` (Emerald 50) | Fundo de alertas e banners de sucesso |
| **Alerta** | `--color-warning` | `#F59E0B` (Amber 500) | Avisos, pendências, estados de atenção |
| **Alerta Fundo** | `--color-warning-bg` | `#FFFBEB` (Amber 50) | Fundo de avisos de atenção |
| **Erro / Destrutivo** | `--color-danger` | `#EF4444` (Red 500) | Exclusões, erros de validação e avisos críticos |
| **Erro Fundo** | `--color-danger-bg` | `#FEF2F2` (Red 50) | Banners de erro e campos com falha |

---

## 3. Tipografia Modular (Font Pairing Humano)

> [!IMPORTANT]
> Proibido utilizar Roboto ou Arial puras sem pareamento. Títulos e cabeçalhos devem ter fonte com personalidade expressiva.

- **Fonte de Títulos (Display/Headings):** `'Outfit'`, `'Plus Jakarta Sans'`, ou `'Fraunces'` (serif moderna editorial).
- **Fonte de Corpo (Body Text):** `'Inter'`, `'DM Sans'`, ou `'Plus Jakarta Sans'`.
- **Fonte Monospaçada (Código/Dados):** `'JetBrains Mono'`, `'Fira Code'`, ou `'Roboto Mono'`.

### Escala de Tipografia
| Nível | Tamanho | Line-Height | Peso (Weight) | Tracking (Letter Spacing) |
| :--- | :--- | :--- | :--- | :--- |
| **Display 1** | `3.00rem` (48px) | `1.15` | `800` (ExtraBold) | `-0.025em` (Mais compacto) |
| **H1 (Título)** | `2.25rem` (36px) | `1.20` | `700` (Bold) | `-0.020em` |
| **H2 (Seção)** | `1.75rem` (28px) | `1.30` | `600` (SemiBold) | `-0.015em` |
| **H3 (Subseção/Card)** | `1.25rem` (20px) | `1.40` | `600` (SemiBold) | `-0.010em` |
| **Body Large** | `1.125rem` (18px) | `1.55` | `400` / `500` | `0` |
| **Body Regular** | `1.00rem` (16px) | `1.50` | `400` (Regular) | `0` |
| **Body Small** | `0.875rem` (14px) | `1.45` | `400` / `500` | `+0.010em` |
| **Caption / Label** | `0.75rem` (12px) | `1.40` | `600` (SemiBold) | `+0.040em` (Mais espaçado) |

---

## 4. Espaçamento e Grid (8pt Grid System)

*Espaços intencionais com respiro humano, evitando layouts comprimidos.*

| Token | Valor em Pixels | Aplicação Recomendada |
| :--- | :--- | :--- |
| `--space-1` | `4px` | Espaçamento micro, gap entre ícone e texto |
| `--space-2` | `8px` | Padding vertical de botões compactos, gap em badges |
| `--space-3` | `12px` | Padding interno de inputs compactos |
| `--space-4` | `16px` | Padding de botões normais, gap entre inputs |
| `--space-5` | `20px` | Padding interno de cards compactos |
| `--space-6` | `24px` | Padding padrão de cards e containers internos |
| `--space-8` | `32px` | Distância entre seções e módulos |
| `--space-10` | `40px` | Margem vertical de cabeçalhos de página |
| `--space-12` | `48px` | Espaçamento de respiro entre blocos de conteúdo |
| `--space-16` | `64px` | Margem de seções de páginas longas |
| `--space-24` | `96px` | Espaço de respiro editorial de página |

---

## 5. Bordas, Arredondamento e Sombras de Elevação

### 5.1. Border Radius (Hierarquia Visual)
*Proibido arredondamento idêntico em todos os componentes sem critério.*
- `--radius-sm`: `4px` (Tags, badges e pequenos indicadores)
- `--radius-md`: `8px` (Inputs, botões e dropdowns)
- `--radius-lg`: `12px` (Cards, painéis e caixas de diálogo)
- `--radius-xl`: `16px` (Modais principais e painéis flutuantes)
- `--radius-full`: `9999px` (Pills, avatares e botões circulares)

### 5.2. Sombras de Elevação (Drop Shadows Sutis)
*Proibidas sombras pretas duras ou névoas escuras artificiais.*
- **Nível 1 (Base / Card Sutil):**  
  `box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.05), 0 1px 2px -1px rgba(15, 23, 42, 0.05);`
- **Nível 2 (Hover em Cards & Menus):**  
  `box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.07), 0 2px 4px -2px rgba(15, 23, 42, 0.05);`
- **Nível 3 (Dropdowns & Popovers):**  
  `box-shadow: 0 10px 15px -3px rgba(15, 23, 42, 0.08), 0 4px 6px -4px rgba(15, 23, 42, 0.04);`
- **Nível 4 (Modais Centrais):**  
  `box-shadow: 0 20px 25px -5px rgba(15, 23, 42, 0.10), 0 8px 10px -6px rgba(15, 23, 42, 0.05);`

---

## 6. Componentes Essenciais e Estados Visuais Mandatórios

> [!IMPORTANT]
> Todo componente DEVE possuir comportamentos documentados para todos os seus estados visuais. Nenhuma tela pode exibir spinners solitários ou telas brancas sem dados.

### 6.1. Botões (`Button`)
- **Primary:** Fundo `--color-primary`, texto branco, sombra Nível 1.
- **Secondary / Outline:** Fundo transparente, borda `1px solid --color-neutral-300`, texto `--color-neutral-800`.
- **Ghost:** Fundo transparente sem borda, hover com fundo `--color-neutral-100`.
- **Destructive:** Fundo `--color-danger`, texto branco.
- **Estados:**
  - `Hover`: Micro-elevação `transform: translateY(-1px)` e transição suave de `200ms`.
  - `Focus-Visible`: Anel de foco acessível `outline: 2px solid --color-primary; outline-offset: 2px;`.
  - `Disabled`: Opacidade `0.5`, cursor `not-allowed`, sem efeito de hover.

### 6.2. Formulários e Inputs
- Fundo `--color-neutral-50` ou branco, borda `--color-neutral-300`, texto `--color-neutral-900`.
- **Focus:** Borda `--color-primary` com sombra de anel sutil `box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.15)`.
- **Error:** Borda `--color-danger` e mensagem explicativa em texto vermelho abaixo do campo.

### 6.3. Skeleton Loaders (Proibido Spinner Isolado)
- Telas em carregamento DEVEM exibir blocos no formato do conteúdo futuro usando animação de gradiente deslizante (*Shimmer Effect*):
```css
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
.skeleton {
  background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-md);
}
```

### 6.4. Empty States (Telas Sem Dados)
- Listas ou tabelas vazias NUNCA exibem telas brancas. Devem conter:
  1. Ícone ou ilustração com personalidade temática (sem formas 3D clichês de IA).
  2. Título claro (ex: *"Nenhum cliente cadastrado ainda"*).
  3. Texto explicativo humano orientando o próximo passo.
  4. Botão de Call-to-Action proativo (ex: `[+ Novo Cliente]`).

---

## 7. Tokens Exportáveis em CSS (:root)

```css
:root {
  /* Cores Neutras */
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

  /* Cores da Marca */
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

  /* Tipografia */
  --font-family-display: 'Plus Jakarta Sans', sans-serif;
  --font-family-body: 'Inter', sans-serif;
  --font-family-mono: 'JetBrains Mono', monospace;

  /* Espaçamento */
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

  /* Raios */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-full: 9999px;

  /* Transições */
  --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-normal: 250ms cubic-bezier(0.4, 0, 0.2, 1);
}
```
