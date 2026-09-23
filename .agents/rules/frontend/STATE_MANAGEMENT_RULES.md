# Regras de Gerenciamento de Estado (Frontend) ⚛️

**ATENÇÃO AGENTES DE FRONTEND (ANGULAR/REACT):**
O estado mal gerido é a principal causa de vazamento de memória e re-renders desnecessários.

## 1. O Problema do "Prop Drilling"
- ❌ **Cascata de Propriedades:** É estritamente proibido passar uma variável de estado (ou função de atualização) por 3 ou mais camadas de componentes filhos apenas para que o último componente possa lê-la.
- ✅ **A Solução:** Se um dado afeta sub-árvores profundas, ele DEVE ser movido para um Estado Global localizado (ex: `Context API`, `NgRx/Signals no Service`, `Zustand`), tornando os componentes intermediários alheios ao dado.

## 2. Separação de Estado Local vs Global
- ❌ **Globalização Prematura:** Não jogue variáveis de formulário (ex: `passwordInput`) dentro do gerenciador de Estado Global.
- ✅ **A Regra:**
  - **Estado Local:** Pertence exclusivamente ao componente e não interessa a mais ninguém (ex: `isDropdownOpen`, `isLoadingButton`).
  - **Estado Global:** Dados do domínio que precisam sobreviver a mudanças de página ou afetam partes completamente distantes do app (ex: `currentUser`, `shoppingCart`, `themePreferences`).

## 3. Mutabilidade Direta (O Pecado Capital)
- ❌ **Alterar o Estado Diretamente:** Em frameworks declarativos, é um erro crasso fazer `state.user.name = "Novo Nome"`. Isso quebra o ciclo de detecção de mudanças.
- ✅ **A Solução (Imutabilidade):** Trate todos os objetos e arrays de estado como **somente leitura**. Sempre retorne uma nova referência utilizando "spread operator" (`...`) ou métodos puros (`map`, `filter`).

## 4. Sincronização Server State vs Client State
- ❌ **Duplicação da Verdade:** Não salve no Estado Global a lista de Usuários que você acabou de buscar da API, a menos que você vá aplicar cache complexo ou lógicas offline.
- ✅ **A Solução:** Trate a API como a verdadeira dona daquele dado. Utilize bibliotecas próprias de cache e sincronia de requisições (ex: `TanStack Query` no React ou RxJS agressivo no Angular) ao invés de duplicar as respostas da API no gerenciador de estado visual.
