# Design System Core

Este arquivo contém os tokens e definições visuais globais da aplicação. Toda vez que um componente novo for criado ou refatorado, os valores abaixo DEVEM ser respeitados para garantir consistência visual em todo o projeto.

## 1. Cores (Color Palette)

Evite cores absolutas (`#000`, `#FFF`, `#FF0000`). Utilize esta escala refinada (inspirada em tailwind moderno):

- **Background Principal:** `#F8FAFC` (Slate 50) para fundo de página, ou `#0F172A` (Slate 900) no Dark Mode.
- **Background de Componentes (Cards):** `#FFFFFF` (Branco) para dar destaque em relação ao fundo da página.
- **Texto Primário:** `#0F172A` (Slate 900) para máxima legibilidade sem o peso visual do preto puro.
- **Texto Secundário / Mutado:** `#64748B` (Slate 500) para descrições, placeholders e textos de suporte.
- **Bordas e Linhas de Divisão:** `#E2E8F0` (Slate 200). Nunca use linhas escuras para separar grids.
- **Ação Principal (Brand Color):** *(A Definir)*. Evite azul padrão; sugere-se Indigo (`#6366F1`) ou Violet (`#8B5CF6`).
- **Estado de Erro (Destrutivo):** `#EF4444` (Red 500) com fundo suave `#FEF2F2` (Red 50) em alertas.

## 2. Tipografia (Modular Scale)

Font-family principal: `'Inter', 'Roboto Flex', sans-serif;`

- **Base (1rem = 16px):** Corpo de texto padrão.
- **H1 (Display):** `3rem` (48px) | Peso: 800 | Tracking (Letras): Mais juntas (`-0.02em`).
- **H2 (Seção):** `2.25rem` (36px) | Peso: 700.
- **H3 (Card Title):** `1.5rem` (24px) | Peso: 600.
- **H4 (Subtítulo):** `1.25rem` (20px) | Peso: 500.

## 3. Espaçamentos (8pt Grid)

Uso estrito de múltiplos de 8px para garantir harmonia espacial. Se algo parecer "apertado", dobre o espaço em vez de adicionar apenas 4px.

- **Micro (gap de ícone/texto):** `4px` ou `8px`.
- **Pequeno (padding interno de botão):** `16px` lateral x `8px` vertical.
- **Médio (gap entre cards/elementos):** `24px` ou `32px`.
- **Grande (margin bottom de seções):** `48px`.
- **Gigante (espaço de respiro entre blocos de página):** `64px` ou `96px`.

## 4. Bordas e Elevação (Radius & Shadows)

O padrão de UI da aplicação deve fugir da estética "bloco quadrado e rígido" gerado por IAs genéricas.

- **Border Radius Padrão:** `8px` (0.5rem) para botões, inputs e cards menores.
- **Border Radius Grandes:** `16px` para modais e grandes containers, garantindo um visual *Soft SaaS*.
- **Sombras de Elevação (Drop Shadows):**
  - **Sombra Nível 1 (Hover em Cards):** `box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05);`
  - **Sombra Nível 2 (Modais/Popovers):** `box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);`

*Nota: Utilize sombras em vez de bordas duras para dar destaque a elementos sobrepostos (ex: headers fixos e dropdowns).*
