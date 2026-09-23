# Regras de Otimização de Assets e Mídia 🖼️

**ATENÇÃO AGENTES DE FRONTEND E DESIGNERS:**
Não importa quão bom seja o seu servidor se o usuário precisa baixar 5MB de imagem não otimizada. Performance percebida é UX.

## 1. Proibição de Formatos Arcaicos
- ❌ **PNGs e JPGs Pesados:** O uso de formatos de imagem ultrapassados não otimizados no código fonte da interface é proibido.
- ✅ **A Solução:**
  - Imagens estáticas DEVERÃO obrigatoriamente ser formatadas em `WebP` (ou `AVIF`).
  - Ilustrações sólidas e ícones DEVEM ser obrigatoriamente servidos em `SVG` para resolução infinita e peso zero.

## 2. Lazy Loading é Lei
- ❌ **Eager Loading para o Mundo:** NUNCA carregue imagens que estão fora do "Above the Fold" (A primeira área de rolagem da tela) de forma instantânea.
- ✅ **A Solução:** Todas as imagens, banners e vídeos devem conter o atributo nativo `loading="lazy"` para que o navegador só baixe a foto quando o usuário rolar até ela.
  - Componentes complexos da rota (ex: Modais, Tabs secundárias) devem usar Code Splitting/Lazy Loading para não virem todos atrelados no pacote JS inicial.

## 3. Dimensões Explícitas e Layout Shift (CLS)
- ❌ **CLS Acidental:** NUNCA omita a largura e a altura de imagens ou containers. A tela não pode pular quando a imagem finalmente terminar de carregar, isso quebra o *Cumulative Layout Shift* do Google.
- ✅ **A Solução:** Sempre forneça o `width` e `height` base no HTML, ou mantenha a relação de aspecto (Aspect Ratio) no CSS para reservar o espaço físico do esqueleto.
