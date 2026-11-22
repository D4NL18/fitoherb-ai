---
description: "Use quando projetar, implementar ou auditar interfaces frontend, componentes, Design System, acessibilidade (A11y), otimizacao de assets, gestao de estado e filtro Anti-IA Slop."
trigger: model_decision
---

# Regras de Frontend, Design System & UX Anti-Slop 🎨✨

**ATENÇÃO DESIGNERS, DESENVOLVEDORES FRONTEND E UX REVIEWERS:**
A interface do usuário deve combinar acabamento estético de nível internacional, acessibilidade universal e performance extrema.

---

## 1. Governança de Design System & Tokens
- ❌ **Proibição de Valores Mágicos de CSS:** É VETADO injetar valores literais soltos no CSS/SCSS (ex: `color: #3b82f6;`, `padding: 13px;`, `border-radius: 7px;`).
- ✅ **Consumo Obrigatório de Tokens:** Todo estilo DEVE consumir as variáveis semânticas do `DESIGN_SYSTEM.md` (`var(--color-primary)`, `var(--spacing-md)`, `var(--radius-lg)`).
- ✅ **8 Estados Interativos Mandatórios:** Todo componente interativo DEVE implementar seus 8 estados previstos: *Default, Hover, Active/Pressed, Focus-Visible, Disabled, Loading, Error, Empty State*.
- ✅ **Carregamento Elegante:** Proibido spinners genéricos bloqueando telas inteiras; use *Skeleton Loaders* estruturados respeitando a geometria dos componentes.

---

## 2. Acessibilidade (A11y) & WCAG AA
- ❌ **Foco Invisível:** NUNCA remova o outline de foco (`outline: none`) sem fornecer `:focus-visible` customizado e nítido.
- ❌ **Focus Trap Ausente:** Modais, Dropdowns e Drawer menus DEVEM prender a navegação por teclado (`Tab`) dentro do componente enquanto abertos.
- ❌ **Botões Sem Rótulo Semântico:** Botões que contêm apenas ícones DEVEM ter `aria-label` descritivo ou tag `sr-only`.
- ✅ **Contraste WCAG AA:** Relação mínima de contraste de `4.5:1` para texto normal em relação ao fundo. Jamais transmita status ou erro apenas por cor: sempre associe ícone ou texto explicativo.

---

## 3. Performance de Assets, Imagens e Mídia
- ❌ **Formatos Pesados Arcaicos:** Proibido usar PNG/JPG não otimizados no bundle.
- ✅ **WebP/AVIF e SVGs:** Imagens estáticas em WebP ou AVIF; ícones e ilustrações vetoriais estritamente em SVG limpo.
- ✅ **Lazy Loading & Layout Shift (CLS):** Todas as imagens abaixo do fold devem ter `loading="lazy"`. Declare sempre `width` e `height` explícitos ou `aspect-ratio` no CSS para evitar saltos visuais durante o carregamento.

---

## 4. Gestão de Estado & Imutabilidade
- ❌ **Mutabilidade Direta:** Proibido alterar propriedades de estado diretamente (`state.user.name = "X"`). Use imutabilidade rigorosa (spread `...`, métodos puros `map/filter` ou Signals imutáveis).
- ❌ **Duplicação de Server State:** Não clone dados crus da API para stores globais de UI a menos que haja necessidade comprovada de cache/offline; use cache dedicado (ex: TanStack Query ou RxJS reativo).
- ✅ **Componentes Dumb (Visuais Burros):** O componente visual apenas renderiza dados recebidos e emite eventos; lógicas de transformação, formatação complexa e orquestração de rede residem em Services/Pipes.

---

## 5. Filtro Anti-IA Slop (Estética Premium Humana)
Evite os padrões visuais genéricos de "média estatística" comumente gerados por IAs:
- ❌ **"AI Purple / Blue Gradient":** Proibido o clássico gradiente padrão azul-para-roxo sem identidade (`from-blue-500 to-purple-500`).
- ❌ **Glassmorphism Excessivo:** Não aplique `backdrop-blur` indiscriminadamente em todos os cards da tela.
- ❌ **Cards Aninhados com Sombras Genéricas:** Evite caixas dentro de caixas usando sombras idênticas (`shadow-md`).
- ❌ **SaaS 3 Colunas Engessado:** Não force qualquer apresentação em exatas 3 colunas com ícones idênticos centralizados.
- ❌ **Centralização Absoluta:** O ser humano prefere ritmo editorial, assimetria intencional e alinhamento à esquerda em LTR com áreas generosas de respiro (*whitespace*).
- ❌ **Copywriting Clichê de IA:** Evite termos batidos como *"Revolutionize"*, *"Empower"*, *"Seamless"*, *"Next-Gen"* ou *"Desbloqueie o poder de..."*. Escreva copy claro, orientado ao benefício prático do usuário.
