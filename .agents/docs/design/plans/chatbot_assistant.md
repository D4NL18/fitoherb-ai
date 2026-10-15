# Design Plan: Assistente Virtual Flutuante (Chatbot Gemini)

> **Feature:** `chatbot-assistant`  
> **Repositório:** `fitoherb-frontend-v2`  
> **Design System:** `.agents/docs/design/DESIGN_SYSTEM.md`  

---

## 1. Visão Geral da Interface
Componente de chat flutuante ancorado no canto inferior direito das páginas públicas do portal institucional da Fitoherb. Quando aberto, renderiza uma janela moderna e limpa, consistente com a paleta florestal (`$green-600`, `$bg-green-base`, `$cream`) e tipografia oficial (`Outfit`).

---

## 2. Componentes e Estrutura Visual

### 2.1 Botão Flutuante (Floating Action Button - FAB)
- **Posicionamento:** `position: fixed; bottom: 24px; right: 24px; z-index: 1000;`
- **Dimensões:** 56px x 56px, circular (`border-radius: 50%`).
- **Cores:** Fundo `$green-600` (`#38582f`), ícone branco (`fas fa-comment-dots` quando fechado, `fas fa-times` quando aberto). Efeito hover com `$green-700` e elevação suave (`box-shadow: 0 4px 16px rgba(26, 45, 20, 0.25)`).
- **Acessibilidade:** `aria-label="Abrir assistente virtual Fitoherb"`, `aria-expanded="false/true"`.

### 2.2 Janela de Conversação (Chat Panel)
- **Dimensões:** Desktop: largura fixa 380px, altura 540px. Mobile (< 640px): tela cheia ou bottom sheet (90vh, 100vw).
- **Cabeçalho:**
  - Título: "Assistente Fitoherb" (Fonte `Playfair Display`, negrito).
  - Subtítulo/Badge: Ícone verde com texto "Inteligência Artificial Oficial".
  - Botões de Ação no topo: Botão minimizar (`_`), botão limpar conversa (`trash`), botão fechar (`x`).
- **Área de Mensagens:**
  - Mensagens do Usuário: Alinhadas à direita, fundo `$green-600`, texto branco, cantos arredondados com terminação direita suave.
  - Mensagens do Assistente: Alinhadas à esquerda, fundo `$cream` ou `$bg-green-base`, texto `$gray-900`, borda sutil `$green-200`.
  - Micro-aviso de Privacidade: Faixa discreta no topo da conversa: "Ambiente seguro. Não envie dados pessoais ou bancários."
- **Card de Ação / Redirecionamento (Inline Banner):**
  - Quando a resposta incluir `action.type === 'NAVIGATE_CATALOG'`, o chat renderiza um card verde suave com ícone `fas fa-external-link-alt`, informando: *"Filtros aplicados no catálogo: [tags]"* com botão secundário de clique manual caso o usuário queira reforçar a navegação.
- **Área de Entrada (Footer Input):**
  - Campo de texto ajustável (máx. 255 caracteres).
  - Contador visível no canto inferior: `0/255` em `$gray-500` (fica vermelho caso atinja o limite).
  - Botão de envio com ícone `fas fa-paper-plane`, ativado apenas se houver texto válido.

---

## 3. Matriz dos 8 Estados Obrigatórios

| Estado | Comportamento Visual |
| :--- | :--- |
| **1. Vazio / Inicial** | Exibe boas-vindas acolhedora com sugestões clicáveis ("O que é a Fitoherb?", "Onde fica a distribuidora?", "Quais as opções de Whey?"). |
| **2. Carregando / Digitando** | Balão do assistente com 3 pontinhos animados pulsantes (typing dots) em `$green-500`. |
| **3. Sucesso** | Mensagem renderizada com tipografia clara, sem quebras desnecessárias de layout. |
| **4. Erro com Retry** | Alerta suave em `$error` com botão "Tentar novamente" sem perder a mensagem digitada. |
| **5. Rate Limited** | Balão informativo amarelo/laranja avisando para aguardar alguns instantes. |
| **6. Offline** | Indicador cinza avisando perda de conexão com a internet. |
| **7. Degradado** | Resposta concisa direta obtida via fallback local com link para o formulário de contato. |
| **8. Limite de Caracteres** | Bloqueio de digitação no caracter 255 com feedback visual da borda do input. |

---

## 4. Integração de Navegação Sem Fechamento
Ao disparar o auto-redirecionamento:
- O Angular Router navega para `/produtos` com `queryParams: { category, supplier, search }`.
- O chat flutuante permanece com seu estado aberto na lateral da tela, permitindo que o visitante examine a galeria de produtos recém-filtrada enquanto visualiza os esclarecimentos do assistente.
