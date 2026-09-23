# UI/UX Anti-Patterns (Filtro Anti-Slop Genérico)

**ATENÇÃO AGENTES DE DESIGN E REVIEWERS:**
Interfaces geradas por IA frequentemente sofrem do viés da "média estatística", resultando em layouts genéricos, sem alma e excessivamente previsíveis (conhecido como "AI Slop"). 
Para garantir um visual *Premium* e com toque humano, as seguintes práticas estão **TERMINANTEMENTE PROIBIDAS**:

## 1. Cores e Gradientes
- ❌ **"AI Purple":** Proibido o uso do gradiente genérico padrão da IA (azul para roxo / `bg-gradient-to-r from-blue-500 to-purple-500`), especialmente em modo escuro (Dark Mode).
- ❌ **Paletas Tailwind Base:** Evite as cores cruas do Tailwind (ex: `blue-600`, `slate-500`). Use cores HSL customizadas ou paletas curadas.

## 2. Componentes e Formas (Bordas e Sombras)
- ❌ **Glassmorphism Excessivo:** Fundos semi-transparentes borrados (`backdrop-blur`) aplicados em todos os elementos da tela.
- ❌ **Cards Aninhados com Sombras Genéricas:** Criar "cards dentro de cards" usando sombras macias padrão (`shadow-md`) repetidamente.
- ❌ **Arredondamento Padrão Absoluto:** Aplicar o clássico `border-radius: 1rem` (`rounded-xl`) em tudo sem critério hierárquico.

## 3. Tipografia Genérica
- ❌ **Fontes de Sistema Puristas:** O uso isolado de Arial, Roboto ou Inter para tudo.
- ✅ **A Solução:** Sempre exija e aplique um "Font Pairing" (Pareamento de Fontes) distinto. Ex: Fonte Serifada Moderna (Playfair Display) para títulos + Sans-Serif Limpa (Outfit/Inter) para corpo.

## 4. Estrutura e Layout
- ❌ **O Padrão SaaS "3 Colunas":** Uma seção de features engessada em exatas 3 colunas, cada uma com um ícone de "foguete/escudo/engrenagem" centralizado acima do texto.
- ❌ **Sessão "Hero" Genérica:** Um título gigantesco centralizado, seguido de um subtítulo cinza, seguido de UM ÚNICO botão centralizado no meio do nada.
- ❌ **Simetria Mecânica e Sufocante:** Espaçamento exato em todos os cantos sem deixar respiro ou áreas de descanso para os olhos (White Space / Negative Space).

## 5. Micro-Interações e Detalhes
- ❌ **O "Hover" Pobre:** O botão apenas muda levemente de tom ao passar o mouse, sem transição suave ou escala.
- ❌ **Excesso de Emojis de Magia:** O uso excessivo do emoji ✨ ("Sparkles") para indicar que algo foi feito por IA ou para "enfeitar" títulos vazios.

## 6. Copywriting e Textos (UX Writing)
- ❌ **Palavras-Chave de Buzzword da IA:** O uso repetitivo de palavras como "Revolutionize", "Empower", "Seamless", "Elevate", "Next-Gen" ou "Desbloqueie o poder de...". Escreva como um humano focado em benefícios reais.
- ❌ **Lorem Ipsum Gigante:** Preencher layouts com blocos de texto sem sentido ao invés de simular dados reais do domínio de negócio.

## 7. Composição e Imagens
- ❌ **A "Forma 3D Flutuante":** Usar ilustrações abstratas de formas geométricas brilhantes voando no espaço como imagem genérica de "tecnologia".
- ❌ **Centralização Absoluta:** Centralizar textos longos, formulários e botões no meio da tela o tempo todo. Leituras humanas preferem alinhamento à esquerda em LTR; a assimetria gera designs mais sofisticados e editoriais.

## 8. Padrões de Interface (UX)
- ❌ **Dashboard Preguiçoso:** Achar que toda área logada precisa ser um "Dashboard" com um menu lateral esquerdo fixo cinza e um gráfico de barras no centro.

> **Regra de Ouro:** Se o seu layout se parece com o template padrão que o ChatGPT ou v0 fariam na primeira tentativa, você **FALHOU** como Designer. Inove, traga assimetria, respiro, textos com intenção real e identidade de marca!
