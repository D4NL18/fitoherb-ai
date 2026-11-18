# Design Plan: Mapeamento de Código ERP por SKU, Sabores/Apresentações e Governança Admin (`product_code_mapping_flavors`) 📐🎨

> **Localização Mandatória:** `.agents/docs/design/plans/product_code_mapping_flavors.md`  
> **Autor:** Designer (`designer`) / `uiux-expert`  
> **Auditor:** UX Reviewer (`ux_reviewer`)  
> **Executor:** Desenvolvedor (`developer`)  
> **Referências:**  
> - `fitoherb-frontend-v2/.agents/docs/design/DESIGN_SYSTEM.md` e `DESIGN_KIT.html`  
> - `fitoherb-frontend-v2/src/colors.scss` e `fitoherb-frontend-v2/src/styles.scss`  
> - `.agents/rules/frontend-ui-anti-patterns.md` e `.agents/rules/frontend-design-system-rules.md`  
> - `.agents/docs/business_rules/product_code_mapping_flavors.md` (`P-400` a `P-409`)  
> - `.agents/docs/tasks/product_code_mapping_flavors.md` (`US-P1` a `US-P6`)  
> - `.agents/docs/GLOSSARY.md`

```css
/* Hallmark · macrostructure: 05-workbench + progressive-sku-matrix · pre-emit critique: P5 H5 E5 S5 R5 V5 · contrast: pass (40–41) · tokens: pass (48) · mobile: pass (34, 49, 50–57) */
```

---

## 1. Identificação & Objetivo da Tarefa

- **User Stories Relacionadas:**
  - `US-P2`: Obrigatoriedade, validação ERP e exibição admin do código `Id_Pro` (Produto Simples).
  - `US-P3`: Gestão de códigos ERP por sabor e apresentação — Matriz `ProductSku` (`P-405`).
  - `US-P4`: Busca direta e importação em lote de variações do ERP Atrio no `ModalEntityComponent` (`P-407`).
  - `US-P5`: Compatibilidade e saneamento atômico na vitrine pública (`ItemCardGalleryComponent`, `ModalGalleryComponent`) sem vazamento de dados ERP (`P-401`, `P-408`).
  - `US-P6`: Filtro admin de pendências ERP (`ErpMappingStatus`) e política visual para `inativo_pro = 1` (`P-406`, `P-408`).
- **Objetivo de UX:**
  Permitir que o administrador cadastre ou edite qualquer produto no `/admin` com **rastreabilidade 1:1 de código ERP (`Id_Pro`)**, eliminando o preenchimento manual frágil por vírgulas e resolvendo o principal atrito operacional relatado pelo usuário: *preencher rapidamente os códigos individuais de todos os sabores e/ou apresentações de um produto sem erros de digitação, duplicidade ou perda de contexto*.
- **Decisões de Arquitetura Visual (Execução Direta Solicitada pelo Usuário):**
  1. **Macroestrutura `05-workbench` aplicada ao `ModalEntityComponent`:** Quando `type() === 'Produtos'`, o modal evolui de `600px` para uma estação de trabalho focal de `920px` (`width: min(95vw, 920px)`), dividindo claramente Identidade/Mídia, Seletor de Topologia (`P-405`), Buscador/Importador ERP em Lote (`P-407`) e Grade Estruturada de SKUs (`FormArray`).
  2. **Drawer Inline em vez de Modal-sobre-Modal:** A busca e importação em lote do ERP Atrio abre como painel expansível integrado *dentro* do fluxo de SKUs (acima da grade), evitando empilhamento de overlays/focus-traps e mantendo visíveis o nome e o fornecedor do produto durante a seleção.
  3. **Sinalização Clara e Colorblind-Safe:** Segue o padrão oficial do `DESIGN_KIT.html` para tags e status — preenchimento escuro semântico + texto `$white` + ícone Font Awesome (`fa-solid`) obrigatório.
  4. **Zero Regressão na Vitrine Pública:** A loja (`/produtos`) continua consumindo apenas `flavours` e `presentation` saneados e deduplicados (`P-401`), sem expor `Id_Pro`, `inativo_pro` ou `Estoque` (`P-408`).

---

## 2. Checklist Anti-IA (Filtro Anti-Slop & Hallmark v1.1)

> [!CAUTION]
> O **UX Reviewer** auditará cada item abaixo na Etapa 4 antes de aprovar a entrega.

- [x] **Sem "AI Purple":** Zero gradientes azul-roxo; âncora exclusiva na escala verde Fitoherb (`$green-600` a `$green-900`) e neutros quentes (`$cream`, `$gray-100`).
- [x] **Sem 3 Colunas Mecânicas:** Nenhum grid genérico de 3 colunas com ícones decorativos; layout orientado ao fluxo de trabalho real (identidade → topologia → busca ERP → grade de SKUs).
- [x] **Pureza Tipográfica & Font Pairing (Gate 37–38a):**
  - Headings (`h2`, `h3`) em `Playfair Display`, **sempre em estilo romano normal (`font-style: normal`)** — proibido itálico em títulos do painel admin ou headers de seção do modal.
  - UI, inputs, labels, badges, tabelas e botões exclusivamente em `Outfit` (`var(--font-body)`).
  - Códigos numéricos (`Id_Pro`, `EAN`) usam `Outfit` com `font-variant-numeric: tabular-nums` para alinhamento tabular sem introduzir uma 3ª família tipográfica (evitando violar a regra `2+1` de fontes).
  - **Nota de correção:** Alinhar `<app-input>`, `<app-select>`, `<app-textarea>` e `<app-table-filter>` para `font-family: var(--font-body)` (`Outfit`), eliminando referências legadas a `"DM Sans"` que não é carregada no `index.html`.
- [x] **Sem Cards Aninhados com Sombras Pesadas:** Blocos internos do modal utilizam divisores `1px solid $gray-200` e mudança sutil de superfície (`$white`, `$cream`, `$green-50`), sem empilhar `box-shadow` repetidos.
- [x] **Biblioteca Única de Ícones (Gate 30):** Exclusivamente **Font Awesome 6** (`fa-solid` / `fa-regular`) com `aria-hidden="true"` em ícones decorativos. Proibido usar emojis (`✅`, `⚠️`, `🔒`, `✨`) na interface.
- [x] **Zero Spinners Solitários:** Busca assíncrona no ERP e carregamento da tabela `Produtos` exibem **Skeleton Loaders Shimmer** geométricos idênticos às linhas reais; spinner inline é permitido apenas dentro do botão durante submissão (`[loading]="isSaving()"`).
- [x] **Zero Telas/Listas Brancas Vazias:** `DynamicTableComponent`, Grade de SKUs e Lista de Busca ERP possuem **Empty States** contextualizados com ícone, explicação e CTA acionável.
- [x] **Copywriting Humano e Honesto:** Textos práticos voltados ao operador de catálogo; zero buzzwords (*"Seamless"*, *"Empower"*, *"Next-Gen"*) e zero métricas fabricadas.
- [x] **Zero `transition: all` e Suporte a Movimento Reduzido:** Todas as transições declaram propriedades explícitas (`background-color`, `border-color`, `transform`, `box-shadow`) e respeitam `@media (prefers-reduced-motion: reduce)`.

---

## 3. Tokens do Design System Aplicados nesta Feature

O Desenvolvedor **NÃO** deve inventar valores hexadecimais, raios fora da escala ou paddings arbitrários. Antes de estilizar os novos componentes, deve consolidar o bloco `:root` oficial do `DESIGN_KIT.html` em `fitoherb-frontend-v2/src/styles.scss` (mantendo os imports SCSS de `src/colors.scss` compatíveis):

| Categoria | Token SCSS (`colors.scss`) | Token CSS (`:root` / `styles.scss`) | Valor | Aplicação na Feature |
| :--- | :--- | :--- | :--- | :--- |
| **Primária / Marca** | `$green-600` / `$primary-color` | `--color-primary` | `#38582f` | Botões primários, checkboxes, foco, estado ativo dos seletores de topologia e filtros |
| **Hover Primário** | `$green-700` | `--color-primary-hover` | `#2e4f24` | Hover de botões primários e itens ativos |
| **Fundo Suave Verde** | `$green-50` / `$bg-green-base` | `--green-50` / `--bg-green-base` | `#f0f8eb` / `#f4f9f1` | Fundo do painel de busca ERP e destaque de linhas recém-importadas |
| **Borda Verde Suave** | `$green-200` / `$green-300` | `--green-200` / `--green-300` | `#b5d4a8` / `#82b074` | Borda de cards/drawers de busca ERP e pills selecionadas |
| **Superfícies Neutras** | `$white` / `$cream` / `$gray-100` | `--white` / `--cream` / `--gray-100` | `#ffffff` / `#faf8f3` / `#f5f5f0` | Fundo do modal (`#ffffff`), footer/preview (`#faf8f3`), cabeçalhos de grade (`#f5f5f0`) |
| **Bordas & Divisores** | `$gray-200` / `$gray-300` | `--gray-200` / `--gray-300` / `--border-field` | `#e8e8e0` / `#d0d0c8` / `#e0e0e0` | Divisores `1px` entre seções, borda constante `1px` de inputs |
| **Textos (WCAG AA)** | `$gray-900` / `$gray-700` | `--text-strong` / `--text-body` / `--text-subtle` | `#1a1a12` / `#4a4a3a` / `#757575` | **Atenção:** usar `--text-subtle` (`#757575`, >= 4.5:1) em vez de `$gray-500` (`#8a8a7a`, 3.5:1) para textos pequenos sobre fundo claro |
| **Tags Escuras (AA)** | — | `--tag-brand` / `--tag-success` / `--tag-warning` / `--tag-danger` / `--tag-info` | `#243d1c` / `#065f46` / `#92400e` / `#991b1b` / `#1e40af` | Fundo sólido de todas as tags/badges com texto `--white` (`#ffffff`) e ícone obrigatório |
| **Superfícies de Alerta** | `$warning` / `$error` | `--surface-warning` (`--surface-warning-fg`) / `--surface-danger` (`--surface-danger-fg`) | `#fef3c7` (`#92400e`) / `#fee2e2` (`#991b1b`) | Caixa de alerta `inativo_pro = 1` (`P-406`) e banners de erro `409`/`422`/`503` |
| **Feedback Borda/Ícone** | `$error` / `$success` / `$warning` | `--error` / `--success` / `--warning` | `#c0392b` / `#27ae60` / `#e67e22` | Borda constante `1px` de erro/sucesso em inputs e borda esquerda `4px` em alertas |
| **Tipografia** | — | `--font-display` / `--font-body` | `'Playfair Display', serif` / `'Outfit', sans-serif` | Headings em `Playfair Display` (romano); corpo, tabelas, formulários e códigos em `Outfit` |
| **Escala de Espaço** | — | `--space-1` a `--space-8` | `0.25rem` (`4px`) a `2rem` (`32px`) | Gaps, paddings de células e respiros da grade |
| **Raios Hierárquicos** | — | `--radius-xs` / `--radius-sm` / `--radius-md` / `--radius-lg` / `--radius-xl` / `--radius-pill` | `4px` / `8px` / `12px` / `16px` / `24px` / `50px` | Checkboxes (`4px`), botões/linhas (`8px`), inputs (`12px`), painéis (`16px`), modal (`20px`/`24px`), chips (`50px`) |
| **Foco Acessível** | — | `--outline-focus` / `--ring-focus` | `2px solid rgba(56, 88, 47, 0.65)` | Anel instantâneo em `:focus-visible` (`outline-offset: 2px`) |
| **Movimento** | — | `--dur-fast` / `--dur-base` / `--ease-interact` / `--ease-snap` | `200ms` / `300ms` / `cubic-bezier(0.165, 0.84, 0.44, 1)` | Transições explícitas de cor, elevação e abertura de popover |

> [!NOTE]
> **Contraste do anel de foco (Gate 40):** `DESIGN_SYSTEM.md` usa `rgba(56, 88, 47, 0.4)` no `:focus-visible`, que fica suave demais sobre fundo verde claro (`$green-50`). Para novos controles interativos sobre superfícies claras ou verdes, usar `outline: 2px solid var(--green-700)` (`#2e4f24`, contraste > 8:1 contra branco e > 6:1 contra `$green-50`) com `outline-offset: 2px`.

---

## 4. Anatomia dos Componentes e Layout

### 4.1. `ModalEntityComponent` — Cadastro e Edição de Produto (`type() === 'Produtos'`)

#### A. Layout Geral do Modal (Macroestrutura `05-workbench`)
Quando `type() === 'Produtos'`, o `.modal-card` aplica a classe modificadora `.modal-card--product` (`max-width: 920px; width: min(95vw, 920px); max-height: 90dvh`), mantendo `header` fixo no topo, corpo `.modal-content` rolável com padding `--space-6` (`24px`) a `--space-8` (`32px`), e `footer` fixo na base (`background: var(--cream)`).

```text
+------------------------------------------------------------------------------------+
| Adicionar Produto / Editar Produto                                             [X] |
+------------------------------------------------------------------------------------+
| [ Bloco A: Identidade & Mídia ]                                                    |
|  +-----------+  Nome * [_____________________________________________________]     |
|  |  Imagem   |  Categoria * [Select v]         Fornecedor * [Select v]             |
|  |  120x120  |  Descrição   [Textarea 4 linhas ______________________________]     |
|  +-----------+                                                                     |
|------------------------------------------------------------------------------------|
| [ Bloco B: Estrutura do Produto no Catálogo (P-405) ]                              |
|  (o) Produto Simples   ( ) Apenas Sabores   ( ) Apenas Apresentações   ( ) Matriz  |
|      1 código ERP          Múltiplos sabores    Múltiplos volumes       Sabor x Ap |
|                                                                                    |
|  +------------------------------------------------------------------------------+  |
|  | [v] Buscar e Importar do ERP Atrio (P-407)            [Fechar / Abrir Busca] |  |
|  |  [ 🔍 Nome, Código Id_Pro, EAN ou Marca ERP...             ] [   Buscar   ]  |  |
|  |  * Busca ampla no ERP Atrio (não restringe pelo fornecedor do site)          |  |
|  |  +------------------------------------------------------------------------+  |  |
|  |  | [x] 131476 | 100% PURE WHEY 900G BAUNILHA · PROBIOTICA  [Ativo no ERP] |  |  |
|  |  |     EAN: 789... · Sugestão: Sabor "Baunilha"                           |  |  |
|  |  | [x] 131477 | 100% PURE WHEY 900G CHOCOLATE · PROBIOTICA [Inativo ERP!] |  |  |
|  |  | [x] 131478 | 100% PURE WHEY 900G MORANGO · PROBIOTICA   [Ativo no ERP] |  |  |
|  |  | [ ] 131490 | WHEY ZERO 900G BAUNILHA ...    [Bloqueado: Já em Prod X] |  |  |
|  |  +------------------------------------------------------------------------+  |  |
|  |  3 selecionado(s) · 1 inativo no ERP   [Limpar]  [Importar 3 Selecionado(s)] |  |
|  +------------------------------------------------------------------------------+  |
|                                                                                    |
| [ Bloco C: Código(s) ERP & Variações ]                                             |
|  Modo Simples:  Código ERP (Id_Pro) * [ 131476      ]  [v CREATINA 300G · Ativo]  |
|  -- OU --                                                                          |
|  Modo Multi-SKU: Variações e Códigos ERP (3 SKUs)            [+ Adicionar Variação]|
|  +----------------+-----------------+---------------+--------------------+-------+ |
|  | Apresentação * | Sabor *         | Código ERP *  | Vínculo / Status   | Ações | |
|  | [ 150g       ] | [ Baunilha    ] | [ 204510    ] | [Ativo] B.O.P.E..  | [Dup][X]|
|  | [ 150g       ] | [ Chocolate   ] | [ 204511    ] | [Inativo!] B.O.P.E | [Dup][X]|
|  | [ 300g       ] | [ Morango     ] | [ 204515    ] | [!] Não encontrado | [Dup][X]|
|  +----------------+-----------------+---------------+--------------------+-------+ |
|                                                                                    |
| [ Bloco D: Alerta Condicional de Inativo no ERP (exibido se inativo_pro = 1) ]     |
|  [!] Atenção: 1 código selecionado está inativo no ERP Atrio (204511).             |
|      [ ] Confirmo que desejo vincular código(s) marcado(s) como inativo(s)...      |
|                                                                                    |
| [ Bloco E: Prévia na Vitrine Pública (P-401 / P-408) ]                             |
|  Vitrine exibirá (sem códigos ERP): Apresentações: 150g, 300g · Sabores: Baunilha..|
+------------------------------------------------------------------------------------+
|                                             [ Cancelar ]  [ Cadastrar / Salvar ]   |
+------------------------------------------------------------------------------------+
```

#### B. Decomposição Detalhada dos Sub-blocos do Modal

1. **Bloco A — Identidade Básica & Mídia:**
   - Grid superior: `grid-template-columns: 148px minmax(0, 1fr); gap: var(--space-6);` no desktop (`> 640px`), colapsando para `1fr` no mobile (`< 640px`).
   - À esquerda: caixa de upload `136px × 136px` com preview e botão/label `"Selecionar Imagem"` / `"Alterar Imagem"` com área clicável mínima de `44px`.
   - À direita: `<app-input>` `Nome *`, seguido de sub-grid `grid-template-columns: repeat(2, minmax(0, 1fr)); gap: var(--space-4);` com `<app-select>` `Categoria *` e `Fornecedor *` (ambos com `[searchable]="true"`), e abaixo `<app-textarea>` `Descrição` (`[rows]="4"`).

2. **Bloco B — Seletor de Estrutura do Produto (`P-405`):**
   - Componente visual: **Segmented Control / Radio Cards compactos** em `role="radiogroup"` com `aria-label="Estrutura do produto no catálogo"`.
   - Grid responsivo: `grid-template-columns: repeat(4, minmax(0, 1fr));` (> 768px), `repeat(2, minmax(0, 1fr))` (480–768px), `1fr` (< 480px).
   - Opções (100% alinhadas às 4 topologias de `P-405` — proíbe hibridismo inconsistente):
     1. **Produto Simples** (`SIMPLE`): *"1 código ERP único, sem sabores ou tamanhos"*.
     2. **Apenas Sabores** (`FLAVOUR_ONLY`): *"Um código ERP para cada sabor"* (ex.: Whey 900g).
     3. **Apenas Apresentações** (`PRESENTATION_ONLY`): *"Um código ERP para cada volume/peso"* (ex.: Stevita 25ml / 60ml).
     4. **Sabor × Apresentação** (`MATRIX`): *"Matriz por tamanho e sabor, mesmo esparsa"* (ex.: B.O.P.E 150g/300g).
   - **Comportamento inteligente de troca:**
     - Na criação (`mode() === 'create'`), inicia em `SIMPLE`.
     - Na edição (`mode() === 'edit'`), detecta automaticamente a topologia a partir dos SKUs recebidos (ou arrays legados `flavours`/`presentation` caso o produto ainda seja `UNMAPPED`).
     - Se o operador alterar a topologia tendo dados preenchidos que perderiam um eixo (ex.: passar de `MATRIX` para `FLAVOUR_ONLY`), exibe confirmação inline não-intrusiva ou limpa apenas o eixo desativado mantendo os códigos `Id_Pro` existentes.

3. **Bloco C — Painel Integrado "Buscar e Importar do ERP Atrio" (`P-407`):**
   - **Gatilho de abertura:** Botão secundário alinhado ao cabeçalho da seção de códigos (`"Buscar e Importar do ERP Atrio"`, `variant="outline"`, ícone `fa-solid fa-magnifying-glass`, altura `44px`). Pode iniciar aberto por padrão em `create` quando usuário clica no gatilho, ou alternável a qualquer momento.
   - **Barra de Busca ERP:**
     - Input (`min-height: 44px`, borda constante `1px solid var(--border-field)`) + botão `"Buscar"` (`height: 44px`, nunca menor/maior que o input — Gate 39!) + botão `"Limpar"` (`44×44px`) quando houver termo.
     - Suporta busca por `Enter` ou clique em `"Buscar"` (e debounce opcional de `400ms` após `>= 2` caracteres ou qualquer código numérico exato `Id_Pro`, evitando disparar carga de 6.946 itens com termo vazio).
     - Texto auxiliar permanente (`--text-subtle`, `0.8rem`): *"Pesquise por nome, código `Id_Pro`, código de barras (`EAN`) ou marca no ERP. Não restringe pelo fornecedor selecionado no site."* (resolve `C-10`, ex.: site `Arrebite` vs ERP `GUARANAPIS`).
   - **Lista de Resultados da Busca ERP:**
     - Container com `max-height: 280px; overflow-y: auto; border: 1px solid var(--gray-200); border-radius: var(--radius-md); background: var(--white);`.
     - Cada item (`.erp-result-row`) em grid `44px minmax(0, 1fr) auto` (Mobile: empilha badge de status abaixo do texto):
       - **Coluna 1 (Checkbox):** `<input type="checkbox">` com área de toque `44×44px`, `accent-color: var(--color-primary)`. Desabilitado quando `alreadyMapped === true` **e** o vínculo pertencer a **outro** produto (diferente do slug atualmente editado).
       - **Coluna 2 (Dados Oficiais ERP):**
         - Linha 1: Pill `Id_Pro` (`tabular-nums`, fundo `--gray-100`, texto `--gray-900`, `font-weight: 700`) + Título oficial `descricao_pro` (`overflow-wrap: anywhere; min-width: 0`).
         - Linha 2 (Metadados): `Marca ERP: <marcaPro>` · `EAN: <codbarraPro || '—'>`.
         - Linha 3 (Sugestão automática quando disponível, `P-407`): Chip discreto de pré-visualização `Sugestão: Sabor "Chocolate"` / `Apres. "300g"` (com expansão `CHOCO → Chocolate` destacada antes mesmo de importar).
       - **Coluna 3 (Badges de Governança — padrão escuro + ícone):**
         - Se `alreadyMapped && !belongsToCurrentProduct`: Badge `--tag-danger` (`#991b1b`) com `fa-solid fa-lock` e texto `Já vinculado: <mappedProductName>` (truncado com `title` completo e texto legível em tooltip/quebra limpa).
         - Se `belongsToCurrentProduct`: Badge `--tag-info` (`#1e40af`) com `fa-solid fa-link` e texto `Já neste produto`.
         - Se `inativoPro`: Badge `--tag-warning` (`#92400e`) com `fa-solid fa-triangle-exclamation` e texto `Inativo no ERP`.
         - Caso contrário: Badge `--tag-success` (`#065f46`) com `fa-solid fa-circle-check` e texto `Ativo no ERP`.
   - **Barra de Ação em Lote (Footer do Painel ERP):**
     - Fundo `--bg-green-base` (`#f4f9f1`), borda superior `1px solid var(--green-200)`, `align-items: center; justify-content: space-between;`.
     - À esquerda: contador dinâmico (`"4 item(ns) selecionado(s)"` + nota se algum selecionado estiver inativo no ERP).
     - À direita: botão texto `"Limpar seleção"` + botão primário `"Importar X Selecionado(s)"` (`type="button"`, `height: 44px`, `white-space: nowrap`, desabilitado quando `0` selecionados).
     - **Ação ao importar:**
       - Converte cada item selecionado em linha do `FormArray` preenchendo `erpCode`, `flavour` (sugerido e editável), `presentation` (sugerido e editável), `erpDescription`, `inactiveInErp` e `erpVerified = true`.
       - Se o operador selecionou `> 1` item ou itens com variação detectada estando em modo `SIMPLE`, comuta automaticamente para a topologia compatível (`FLAVOUR_ONLY`, `PRESENTATION_ONLY` ou `MATRIX`).
       - Se selecionou exatamente `1` item sem sabor/apresentação e está em `SIMPLE`, preenche diretamente o campo `Id_Pro` do produto simples.
       - Não duplica `Id_Pro` já presente na grade atual e destaca as novas linhas com animação sutil de fundo (`--green-50` → `--white`, `600ms`, respeitando `prefers-reduced-motion`).

4. **Bloco D — Entrada de SKU Simples vs. Grade Estruturada de SKUs (`FormArray`) (`P-402`, `P-403`, `P-404`, `P-405`):**
   - **Quando `topology === 'SIMPLE'`:**
     - Linha limpa em 2 colunas (`minmax(0, 240px) minmax(0, 1fr)` no desktop):
       - Input numérico `Código ERP (Id_Pro) *` (`inputmode="numeric"`, altura `44px`, apenas dígitos inteiros `> 0`, validação instantânea em `blur`).
       - Cartão/pill de resolução ERP à direita exibindo: estado `Não verificado` (neutro), `Validando...` (shimmer inline), `Ativo no ERP · <descricao_pro>` (sucesso), `Inativo no ERP · <descricao_pro>` (alerta) ou erro específico (`Não encontrado no ERP` / `Já vinculado a <produto>`).
   - **Quando `topology !== 'SIMPLE'` (Multi-SKU `FormArray`):**
     - Cabeçalho da grade: título `Grade de Variações (SKUs)` + badge de contagem (`3 variações` / `1 pendência`) + botão outline `"+ Adicionar Variação"` (`type="button"`, `height: 44px`, `white-space: nowrap`).
     - **Colunas adaptativas por topologia (`P-405`):**
       - `FLAVOUR_ONLY`: `[Sabor *] | [Código ERP (Id_Pro) *] | [Status ERP] | [Ações]`
       - `PRESENTATION_ONLY`: `[Apresentação *] | [Código ERP (Id_Pro) *] | [Status ERP] | [Ações]`
       - `MATRIX`: `[Apresentação *] | [Sabor *] | [Código ERP (Id_Pro) *] | [Status ERP] | [Ações]`
     - **Ergonomia de Matriz Esparsa e Repetição Rápida:**
       - Em cada linha, além do botão `Remover` (`fa-trash-can`, `44×44px`), incluir botão `Duplicar` (`fa-regular fa-clone`, `44×44px`, `title="Duplicar variação mantendo apresentação"`, visível especialmente em `MATRIX`) para que, ao cadastrar manualmente `B.O.P.E 150g` em 3 sabores, o operador não precise redigitar `"150g"` três vezes.
       - Ao digitar/alterar `Id_Pro` manualmente (sem usar o importador em lote), no evento `blur` (ou debounce `450ms` após dígito válido), consulta o catálogo espelhado do ERP para preencher em tempo real a descrição oficial (`descricao_pro`), alertar se `inativo_pro = 1`, ou acusar `404`/`422`/`409` antes mesmo de clicar em salvar!
     - **Validação de Linha (`min-height: 1lh` reservado para mensagens — zero layout shift):**
       - Erro de `Id_Pro` obrigatório / não numérico / `<= 0` (`P-402`).
       - Erro de `Id_Pro` duplicado dentro da própria grade (`P-404`).
       - Erro de combinação `(flavour, presentation)` duplicada normalizada dentro da mesma grade (`P-404`).
       - Erro de sabor/apresentação vazio ou apenas pontuação ex.: `"."` (`P-401`).
       - Erro de `Id_Pro` inexistente no ERP (`P-403`) ou vinculado a outro produto (`P-404`).

5. **Bloco E — Alerta e Confirmação Obrigatória para Inativos (`P-406`):**
   - Exibido automaticamente sempre que qualquer SKU da grade (ou o SKU simples) possuir `inativoPro === true`, ou se a API retornar `422` com código `ERP_SKU_INACTIVE_CONFIRMATION_REQUIRED`.
   - Estilo: fundo `--surface-warning` (`#fef3c7`), texto `--surface-warning-fg` (`#92400e`), borda `1px solid var(--warning)`, borda esquerda `4px solid var(--warning)`, `border-radius: var(--radius-md)`, padding `--space-4`.
   - Conteúdo:
     - Ícone `fa-solid fa-triangle-exclamation` + Título *"Código(s) marcado(s) como inativo(s) no ERP Atrio (`inativo_pro = 1`)"*.
     - Lista compacta dos códigos afetados (ex.: `204511 — B.O.P.E 150G CHOCOLATE`).
     - Checkbox acessível (`min-height: 44px` clicável no `<label>`): *"Estou ciente de que este(s) item(ns) consta(m) como inativo(s) no ERP e confirmo o vínculo ao catálogo do site."*
   - Se o operador tentar salvar sem marcar o checkbox quando houver SKU inativo, o foco é movido para o checkbox e a borda do banner reforça o destaque de erro (`--error`) sem fechar o modal.

6. **Bloco F — Prévia Deduplicada para Vitrine Pública (`P-401`, `P-408`):**
   - Exibido apenas em topologias Multi-SKU (`FLAVOUR_ONLY`, `PRESENTATION_ONLY`, `MATRIX`) quando houver ao menos 1 sabor ou apresentação preenchido.
   - Superfície `--cream` (`#faf8f3`), borda `1px solid var(--gray-200)`, `border-radius: var(--radius-sm)`, padding `--space-3 --space-4`.
   - Mostra exatamente os chips únicos que serão gerados após saneamento e deduplicação (`Apresentações (2): 150g · 300g` | `Sabores (3): Baunilha · Chocolate · Morango`) e nota: *"Códigos ERP não são exibidos na loja pública."*

7. **Ajustes Obrigatórios em Componentes Base & Fluxo de Erro (`D-06`):**
   - **`ButtonComponent` (`button.component.ts` / `.html`):** Adicionar `type = input<'button' | 'submit' | 'reset'>('button')` e bind `[attr.type]="type()"` no `<button>` nativo! Atualmente `modal-entity.component.html` passa `type="submit"` e `type="button"` para `<app-button>`, mas o componente ignora esse input, o que faria botões auxiliares dentro do `<form>` (como `"Buscar"`, `"+ Adicionar Variação"` ou `"Importar"`) dispararem `ngSubmit` acidentalmente!
   - **`AdminComponent.handleSave` (`admin.component.ts:500-511`):** Remover o override estático de `409` (`'Já existe um produto com este nome para este fornecedor.'`), exibindo sempre a mensagem real de conflito retornada pelo backend (`err.error?.message`, ex.: `"O código ERP '131476' já está vinculado ao produto '100% Pure Whey 900g'."`), mantendo o `ModalEntityComponent` aberto com os dados preenchidos para correção imediata!

---

### 4.2. `AdminComponent` & `DynamicTableComponent` — Tabela `Produtos` (`P-408`, `Q-05`, `US-P6`)

#### A. Barra Superior de Pesquisa e Filtros (`admin.component.html`)
1. **Input de Busca (`#search`):** Quando `pageTitle() === 'Produtos'`, o placeholder muda dinamicamente de `"Pesquisar..."` para `"Buscar por nome, sabor ou código ERP (Id_Pro)..."` (`P-408`, cenário `C-13`).
2. **Filtro Rápido de Status ERP (Pills Segmentadas — exclusivo da aba `Produtos`):**
   - Posicionado logo abaixo da linha `.table-header-container` (ou integrado em faixa dedicada `.erp-status-bar`) para evitar que o botão `"Adicionar produto"` quebre em duas linhas ou comprima os selects em telas médias (`992px–1200px`).
   - Pills com `role="group"` e `aria-label="Filtrar produtos por status no ERP"`:
     - `Todos` (default selecionado)
     - `Sem Código` (`UNMAPPED` — ícone `fa-solid fa-circle-exclamation`)
     - `Completo` (`COMPLETE` — ícone `fa-solid fa-circle-check`)
     - `Alerta Inativo ERP` (`INACTIVE_ALERT` — ícone `fa-solid fa-triangle-exclamation`)
   - Estado ativo usa `--tag-brand` (`#243d1c`) com texto `--white` (ou `--tag-danger` / `--tag-warning` nos filtros específicos), altura mínima `36px` (ou `44px` em touch/mobile `< 768px`) e `white-space: nowrap`.
   - Clicar em `"Limpar Filtros"` restaura o filtro rápido para `Todos`, além de limpar busca textual, ordenação e filtros de Categoria/Fornecedor.

#### B. Novas Colunas na Tabela `Produtos` (`TableColumn.interface.ts` + `DynamicTableComponent`)
Atualizar `TableColumn.type` adicionando `'erp-code' | 'erp-status'` e configurar as colunas de `Produtos` em `admin.component.ts`:

| Ordem | Label | Key | Tipo | Comportamento Visual |
| :---: | :--- | :--- | :--- | :--- |
| 1 | `Imagem` | `imageUrl` | `image` | Miniatura `50×50px`, `border-radius: 8px` |
| 2 | `Nome` | `name` | `text` | Nome do produto |
| 3 | `Categoria` | `categoryName` | `badge` | Pill escura `--tag-brand` + `white` (conforme auditoria `DESIGN_KIT.html`), filtro multi-seleção mantido |
| 4 | `Fornecedor` | `supplierName` | `text` | Nome do fornecedor, filtro multi-seleção mantido |
| 5 | `Código ERP` | `erpSummary` | `erp-code` | **Simples:** numeral `131476` (`tabular-nums`, peso `600`). **Multi-SKU (`Q-05` Opção A):** botão pílula `6 SKUs · 131476` (`fa-layer-group` + `fa-chevron-down`) que abre Popover com a lista completa `(Apresentação / Sabor) → Id_Pro`. **Sem código:** traço `—` em `--text-subtle`. |
| 6 | `Status ERP` | `erpMappingStatus` | `erp-status` | Badge escuro com ícone obrigatório (`COMPLETE`, `UNMAPPED`, `INACTIVE_ALERT`) |
| 7 | `Ações` | `''` | `actions` | Ícones Editar (`fa-pen`) e Excluir (`fa-trash-can`) com área de toque expandida para `44×44px` |

#### C. Especificação Técnica do Popover Multi-SKU (`Q-05` — Anti-Clipping)
> [!IMPORTANT]
> A tabela `.table-responsive` possui `overflow-x: auto`. Qualquer dropdown posicionado com `position: absolute` dentro de uma `<td>` será cortado horizontal/verticalmente perto das bordas!
- **Solução obrigatória (`interaction-and-states.md`):** O popover da célula `Código ERP` DEVE renderizar em camada flutuante (`position: fixed` calculado com `getBoundingClientRect()` do botão disparador — ou Popover API nativa — com flip automático para cima se estiver nos últimos `220px` da viewport), `z-index: var(--z-dropdown)` (`100` ou superior dentro do contexto da página).
- **Conteúdo do Popover:**
  - Cabeçalho: `<Nome do Produto> · <N> SKUs mapeados` + botão fechar (`X`) em mobile.
  - Lista compacta (máx. `240px` altura com scroll): cada linha exibe `[Apresentação · Sabor]` à esquerda, `[Id_Pro]` (`tabular-nums`, peso `700`) e micro-tag `Inativo` se `inativoPro === true`.
  - Interação: abre/fecha no **clique** (funciona em mouse e touch) e teclado (`Enter`/`Space`), fecha com `Esc` ou clique fora. Opcionalmente exibe resumo breve em `title`/tooltip nativo no hover após `800ms`.

---

### 4.3. Vitrine Pública (`ItemCardGalleryComponent` & `ModalGalleryComponent`) (`P-401`, `P-408`)

1. **`ItemCardGalleryComponent` (`item-card-gallery.component.html` / `.scss`):**
   - Preserva o layout editorial do card (`$white`, `border-radius: 24px`, imagem `260px`, categoria, título `Playfair Display` e texto resumido).
   - **Exibição de variações saneadas (`P-401`):**
     - Quando `product().flavours.length > 0`, exibe `Sabores: Baunilha, Chocolate, Morango.` (valores já atômicos e deduplicados vindos do backend, sem `" e "` residual).
     - **Melhoria pontual:** Quando `product().flavours.length === 0` e `product().presentation?.length`, exibe `Apresentação: 25ml, 60ml.` usando exatamente a mesma classe `.flavours-text` (`-webkit-line-clamp: 2`), dando visibilidade na vitrine a itens de variação apenas por volume/peso (ex.: `Stevita Líquido`).
   - **Blindagem `P-408`:** Nenhum campo `erpCode`, `skus`, `inativoPro`, `erpMappingStatus` ou `Estoque` é recebido ou exibido no componente ou no card.

2. **`ModalGalleryComponent` (`modal-gallery.component.html` / `.scss`):**
   - Mantém os grupos separados `.flavours-chips` para `Sabores Disponíveis:` e `Apresentação:`.
   - Com o saneamento `P-401`, produtos matriz como `B.O.P.E` (6 SKUs = 2 apresentações × 3 sabores) exibem exatamente **3 chips de sabor** e **2 chips de apresentação** sem repetição.
   - **Ajuste de acessibilidade visual:** Na `.category-tag` / `.category-label` sobre fundo branco, recomenda-se ajustar de `#82b074` (contraste 2.5:1 — insuficiente na auditoria do `DESIGN_KIT.html`) para `var(--green-500)` (`#4a7040`, contraste > 5.4:1 — AA!).

---

## 5. Matriz de Estados Visuais Obrigatórios (8 Estados + Variações)

Todos os novos elementos interativos (**Buscador ERP**, **Grade de SKUs**, **Seletor de Topologia**, **Pills de Filtro ERP**, **Popover Multi-SKU**, **Tabela Admin**) implementam integralmente os estados abaixo:

| Estado | Inputs (Código ERP / Sabor / Apres. / Busca ERP) | Botões & Pills (Topologia / Importar / Filtros) | Linhas da Lista ERP & Grade SKU | Tabela Admin `Produtos` |
| :--- | :--- | :--- | :--- | :--- |
| **1. Default** | `border: 1px solid var(--border-field)` (`#e0e0e0`), `outline: 2px solid transparent`, `background: var(--bg-field)`, altura fixa `44px` | Primary: `--color-primary` + `--white`; Outline/Pills: `--white` + borda `1px solid var(--gray-300)` + `--text-body` | Linha branca com divisor inferior `1px solid var(--gray-200)`; tag escura de status ERP com ícone | Células alinhadas verticalmente ao centro, badges escuras de status e código `tabular-nums` |
| **2. Hover** *(somente `@media (hover: hover)`)* | `background: var(--gray-100)` sutil, `border-color: var(--gray-300)` — **`border-width` permanece `1px` (zero layout shift)** | Primary: `--color-primary-hover` + `translateY(-2px)`; Outline/Pills: `--bg-green-base` + `border-color: var(--green-500)` | Item selecionável ERP muda fundo para `--green-50`; botão ícone remover muda para `--surface-danger` / `--surface-danger-fg` | Linha da tabela usa `--bg-green-base`; badge Multi-SKU ganha borda `--green-600` |
| **3. Focus-Visible** *(teclado)* | `outline: 2px solid var(--green-700); outline-offset: 2px;` instantâneo (sem transição de fade) | `outline: 2px solid var(--green-700); outline-offset: 2px;` instantâneo | Checkbox, linha focalizável e botões de ação exibem anel instantâneo `2px` de alto contraste | Botão Multi-SKU, filtros e paginação exibem anel instantâneo `2px` |
| **4. Active** *(pressed)* | Mantém estado de foco (não cria 2º estilo de digitação) | `transform: translateY(1px); filter: brightness(0.95);` | Feedback de pressão ao clicar no checkbox ou botão remover | Feedback de pressão ao abrir popover ou aplicar filtro |
| **5. Disabled / Blocked** | `opacity: 0.55; cursor: not-allowed; background: var(--gray-100);` + `aria-disabled="true"` | `opacity: 0.55; cursor: not-allowed; box-shadow: none; transform: none;` + motivo visível (ex.: `0 selecionado(s)`) | Item ERP já vinculado a outro produto (`P-404`): `opacity: 0.68; cursor: not-allowed;`, checkbox `disabled` + tag vermelha `Já vinculado: <Produto>` | Ações desabilitadas para perfil restrito com ícone cadeado e `title` explicativo |
| **6. Loading** *(Skeleton Shimmer)* | Validação assíncrona de `Id_Pro` exibe spinner discreto `14px` no slot reservado à direita (`24px` fixos, sem empurrar texto), **mantendo input editável** | Botão `"Cadastrar"` / `"Salvar"` mostra spinner inline substituindo o ícone e bloqueia duplo clique | **Busca ERP em curso:** 4 linhas **Skeleton Shimmer** espelhando checkbox (`20×20`), pill código (`64×22`), barra título (`70% × 16`) e chip status (`96×22`) | **Carregamento da tabela:** 5 linhas **Skeleton Shimmer** espelhando thumbnail `50×50`, barras de nome/categoria/fornecedor, pill código ERP e tag status |
| **7. Empty State** | — | — | **Busca ERP sem resultados:** ícone `fa-solid fa-box-open`, título `"Nenhum SKU encontrado no ERP Atrio"`, subtítulo `"Tente buscar pelo código Id_Pro, código de barras EAN ou parte da descrição sem a marca."`, botão `"Limpar busca"` | **Tabela filtrada vazia:** ícone `fa-solid fa-filter-circle-xmark`, título `"Nenhum produto corresponde aos filtros"`, texto explicativo + botão `"Limpar Filtros"` (`UNMAPPED` zerado mostra mensagem positiva: `"Todos os produtos possuem código ERP vinculado."`) |
| **8. Error State** | `border-color: var(--error); background: var(--bg-field-invalid);` (`border-width` constante `1px`), `aria-invalid="true"`, `aria-describedby`, slot reservado `min-height: 1lh` com ícone `fa-circle-exclamation` + texto explicativo | Banner de erro de API no topo/base do modal (`--surface-danger` / `--surface-danger-fg`): preserva mensagem real de `409` (conflito `Id_Pro`), `422` (inexistente/estrutura) e `503` (catálogo ERP indisponível + botão `"Tentar novamente"`) | Linha da grade SKU com erro recebe destaque sutil `--bg-field-invalid` + mensagem específica logo abaixo da linha (ex.: `"Código ERP '999' não encontrado no ERP Atrio."`) | Banner no topo da tabela em falha de listagem com botão `"Recarregar lista"`, preservando filtros aplicados |
| **9. Success State** | Borda `--success` sutil + ícone `fa-solid fa-circle-check` no slot direito quando `Id_Pro` é validado no catálogo ERP (limpa automaticamente ao editar novamente) | Toast existente `<app-toast>` para confirmação de criação/edição concluída (`"Produto cadastrado com sucesso!"`) | Linhas recém-importadas recebem pulso suave de destaque `--green-50` (`600ms`) + resumo `"X SKU(s) importado(s) para revisão"` | Tag `--tag-success` (`Completo`) nos produtos com 100% dos SKUs ativos vinculados |

### Especificação CSS do Skeleton Shimmer (Obrigatório em Busca ERP e Tabela Admin)
```scss
.skeleton-shimmer {
  background: linear-gradient(
    90deg,
    var(--gray-100) 25%,
    var(--cream) 50%,
    var(--gray-100) 75%
  );
  background-size: 400px 100%;
  animation: fh-shimmer 1.4s ease-in-out infinite;
  border-radius: var(--radius-xs);
}

@keyframes fh-shimmer {
  0% { background-position: -400px 0; }
  100% { background-position: 400px 0; }
}

@media (prefers-reduced-motion: reduce) {
  .skeleton-shimmer {
    animation: none;
    background: var(--gray-100);
  }
}
```

---

## 6. Responsividade e Breakpoints (320 / 375 / 414 / 768 / 1024+ px)

Regras universais de segurança de layout (Hallmark Gates 34, 49, 50–57):
- `overflow-x: clip` no root da página admin e corpo do modal (evita corte de elementos `sticky`/`fixed`).
- Todos os grids contendo imagens ou textos longos usam `minmax(0, 1fr)` (nunca `1fr` puro).
- Títulos e descrições longas de produtos/ERP aplicam `overflow-wrap: anywhere; min-width: 0;`.
- Todos os botões, abas e pills de filtro declaram `white-space: nowrap` (nunca texto clicável quebrando em 2 linhas).
- Área mínima de toque `44×44px` em botões de ícone (excluir variação, fechar popover, editar/excluir linha, checkbox).

| Breakpoint | `ModalEntityComponent` (Produtos) | Buscador ERP & Grade de SKUs (`FormArray`) | Tabela `Produtos` (`AdminComponent`) |
| :--- | :--- | :--- | :--- |
| **Mobile (`< 640px`, testado em `320px`, `375px`, `414px`)** | Modal ocupa `calc(100vw - 16px)` e `max-height: 94dvh`; seção Identidade empilha em `1fr` (imagem centralizada acima); Seletor de Topologia em `1fr` ou `2×2` compacto; botões do footer empilham ou dividem `50%` com labels curtos (`Cancelar` / `Salvar`). | Barra de busca empilha input + botão `"Buscar"` full-width (`height: 44px`); cada item da busca ERP empilha título, metadados e badge de status verticalmente. **Grade de SKUs transforma cada linha em cartão-bloco vertical limpo** (sem scroll horizontal dentro do modal!). | Barra de filtros empilha busca, ordenação e botão adicionar em coluna única; pills de Status ERP permitem scroll horizontal suave (`overflow-x: auto; scrollbar-width: none`) sem quebrar texto; popover Multi-SKU vira bottom-sheet/card centralizado responsivo (`width: min(92vw, 360px)`). |
| **Tablet (`640px – 1024px`, testado em `768px`)** | Modal com `width: 94vw`; Identidade em 2 colunas (`136px minmax(0, 1fr)`); Seletor de Topologia em grade `2×2`. | Barra de busca em linha única; Grade de SKUs mantém colunas compactas ou 2 linhas por item (`Apresentação + Sabor` na linha 1, `Código ERP + Status + Remover` na linha 2). | `.table-header-container` em coluna ou 2 linhas balanceadas; pills de Status ERP com `flex-wrap: wrap`; `.table-responsive` com scroll horizontal suave apenas quando necessário. |
| **Desktop (`> 1024px`, testado em `1280px` e `1440px`)** | Modal `max-width: 920px`; Identidade em 2 colunas assimétricas + `Categoria` e `Fornecedor` lado a lado; Seletor de Topologia em 4 colunas uniformes. | Barra de busca em linha única (`input` flex `1` + botão `44px`); Grade de SKUs em linha tabular fluida com colunas adaptadas à topologia ativa. | Toolbar em linha + faixa de pills Status ERP alinhada à esquerda; todas as 7 colunas visíveis sem aperto em `1280px+`; popover Multi-SKU ancorado ao botão via `getBoundingClientRect()`. |

---

## 7. Decisão Aberta para Validação no Checkpoint (`Q-05`) & Refinamentos

Para confirmação do usuário no Checkpoint de saída da Etapa 2 (`.agents/docs/tasks/product_code_mapping_flavors.md`, Seção 1.2):

- **Recomendação Visual para `Q-05` (Exibição do Código ERP na Tabela Admin para Multi-SKU):**
  - **Adotar Opção A (Recomendada):**
    - Produto Simples: exibe código direto com peso tabular (`131476`).
    - Produto Multi-SKU: exibe botão/pílula resumida `6 SKUs · 131476` (`fa-layer-group` + `fa-chevron-down`) que abre Popover flutuante listando todos os pares `[Apresentação / Sabor → Id_Pro]` e badge de inatividade.
    - *Por quê:* Preserva altura uniforme das linhas da tabela (`50px–72px`), evita poluição visual em produtos com 6 a 12 variações e garante usabilidade idêntica em mouse, touch e teclado.

---

## 8. Critérios de Aceite para UX Reviewer (DoD Visual)

- [ ] Todos os estilos novos e atualizados consomem exclusivamente tokens do `DESIGN_SYSTEM.md` / `:root` de `styles.scss` (zero hexadecimais mágicos ou `DM Sans` residuais).
- [ ] Stamp Hallmark preservado no topo do SCSS do módulo de catálogo admin e zero violações de Anti-Slop (zero AI Purple, zero 3 colunas mecânicas, zero headers em itálico, zero emojis como ícones).
- [ ] `ModalEntityComponent` suporta fluidamente as 4 topologias (`P-405`), busca cross-brand + importação em lote do ERP (`P-407`), validação individual de cada `Id_Pro` (`P-402`, `P-403`, `P-404`) e alerta + confirmação para `inativo_pro = 1` (`P-406`).
- [ ] `ButtonComponent` aceita `[type]="'button' | 'submit' | 'reset'"`, impedindo submits acidentais ao clicar em ações auxiliares do formulário.
- [ ] `AdminComponent` exibe a mensagem real de erro `409`/`422`/`503` sem mascarar conflito de código ERP como conflito de nome/fornecedor (`D-06`), mantendo os dados do modal preservados.
- [ ] Tabela `Produtos` (`AdminComponent` + `DynamicTableComponent`) exibe colunas `Código ERP` (com Popover anti-clipping em Multi-SKU) e `Status ERP`, busca unificada por `Id_Pro`, pills de filtro (`Todos`, `Sem Código`, `Completo`, `Alerta Inativo ERP`), Skeleton Shimmer e Empty State.
- [ ] Vitrine pública (`ItemCardGalleryComponent` e `ModalGalleryComponent`) renderiza apenas `flavours` e `presentation` saneados e deduplicados (`P-401`), sem expor `Id_Pro`, `inativo_pro` ou `Estoque` (`P-408`).
- [ ] Todos os 8 estados interativos, contraste WCAG AA (`>= 4.5:1`), navegação por teclado (`:focus-visible`, `Esc`, `Tab`), `@media (prefers-reduced-motion: reduce)` e responsividade em `320 / 375 / 414 / 768 / 1280px` validados sem scroll horizontal.

---

## 9. Adendo Incremental — Onda 4: Central de Curadoria Rápida (`QuickCurationPanel`), Vitrine Sem Foto (`P-412`) e Visibilidade Admin (`US-P7` / `US-P8`)

```css
/* Hallmark · macrostructure: triage-queue-strip + inline-action-drawer · pre-emit critique: P5 H5 E5 S5 R5 V5 · contrast: pass (40–41) · tokens: pass (48) · mobile: pass (34, 49, 50–57) */
```

> [!NOTE]
> **Reconciliação Estrita de Tokens (`DESIGN_SYSTEM.md` & `DESIGN_KIT.html`):** Este adendo consome exclusivamente a paleta e tipografia reais definidas em `fitoherb-frontend-v2/.agents/docs/design/DESIGN_SYSTEM.md`, `DESIGN_KIT.html`, `src/colors.scss` e `src/index.html`: marca verde `--color-primary` (`#38582f` / `$green-600`) e escala `#1a2d14`–`#f0f8eb`, superfícies `--white` (`#ffffff`), `--cream` (`#faf8f3`), `--gray-100` (`#f5f5f0`) e `--bg-green-base` (`#f4f9f1`), além das fontes efetivamente carregadas `--font-display` (`'Playfair Display', Georgia, serif`, sempre estilo romano `font-style: normal`) e `--font-body` (`'Outfit', sans-serif` com `tabular-nums` para `Id_Pro` e contadores). Nenhum hexadecimal arbitrário ou fonte não carregada deve ser introduzido no código.

### 9.1. Identificação, Objetivo de UX & Checklist Anti-IA (`US-P7` / `US-P8`)

- **User Stories e Regras Cobertas:** `US-P7` (`P-411`, `P-412` — fallback visual limpo na vitrine sem foto e badge `Oculto na Vitrine (Inativo no ERP)` na tabela `/admin`) e `US-P8` (`P-413` — `QuickCurationPanel` no `/admin` para `ROLE_ADMIN`/`ROLE_USER`, abertura de `ModalEntityComponent` pré-preenchido com foco no dropzone e descarte auditável).
- **Checklist Anti-IA Validado (Hallmark v1.1):** Zero 3 colunas mecânicas (`triage-queue-strip`); zero emojis AI-slop (exclusivamente ícones Font Awesome 6 `aria-hidden="true"`); tipografia `--font-display` romana + `--font-body` com `tabular-nums`; header sem eyebrow lateral; sem botões aninhados (`trigger` e `Ignorar` como irmãos no DOM); `type="button"` explícito em `ButtonComponent` e em todos os botões auxiliares.

### 9.2. Mapeamento Adicional de Tokens (Onda 4)

| Elemento Visual | Token SCSS / CSS | Valor Oficial | Regra de Contraste (WCAG AA) |
| :--- | :--- | :--- | :--- |
| **Container `QuickCurationPanel`** | `--white` + borda `1px solid var(--green-200)` + borda esquerda `4px solid var(--color-primary)` | `#ffffff` / `#b5d4a8` / `#38582f` | `--text-strong` (`#1a1a1a`) > `15:1` |
| **Cabeçalho do Painel** | `--bg-green-base` + borda inferior `1px solid var(--gray-200)` | `#f4f9f1` / `#e8e8e0` | Subtítulo `--text-muted` (`#666666`, `5.4:1`) |
| **Linha Pendente** | `--white` (hover: `--green-50`) + divisor `1px solid var(--gray-200)` | `#ffffff` / `#f0f8eb` / `#e8e8e0` | Sem `box-shadow` pesado aninhado |
| **Badge `Id_Pro` (Tabular)** | `--gray-100` + borda `1px solid var(--gray-300)` + `--text-strong` | `#f5f5f0` / `#d0d0c8` / `#1a1a1a` | `tabular-nums`, contraste > `14:1` |
| **Badge `Sem foto`** | `--tag-info` + `--white` + `fa-solid fa-image` | `#1e40af` / `#ffffff` | `8.7:1` |
| **Badge `Novo do ERP` / `Reativado`** | `--tag-new` + `--white` + `fa-solid fa-bolt` / `fa-rotate` | `#2e4f24` / `#ffffff` | `9.8:1` |
| **Badge Fallback Categoria / Fornecedor** | `--tag-warning` + `--white` + `fa-solid fa-triangle-exclamation` | `#92400e` / `#ffffff` | `7.0:1` |
| **Badge Tabela `Oculto na Vitrine (Inativo no ERP)`** | `--tag-danger` + `--white` + `fa-solid fa-eye-slash` | `#991b1b` / `#ffffff` | `8.1:1` |
| **CTA Primário `"Completar Foto"`** | `--color-primary` (hover `--color-primary-hover`) + `--white` | `#38582f` / `#2e4f24` / `#ffffff` | `8.2:1` / `9.8:1` |
| **Ação `"Ignorar / Não exibir no site"`** | `--white` + borda `var(--gray-300)` + `--tag-danger` (hover `--surface-danger`) | `#ffffff` / `#991b1b` (`#fee2e2`) | `8.1:1` / `7.2:1` |
| **Placeholder Vitrine (`imageUrl === null`)** | `--bg-green-base` / `--cream` + imagem íntegra sem `grayscale` | `#f4f9f1` / `#faf8f3` | `opacity: 0.92; filter: none;` |

### 9.3. Anatomia `QuickCurationPanel`, Modal Pré-Preenchido & Confirmação de Descarte

- **Posicionamento & RBAC (`AdminComponent`):** Imediatamente acima de `.table-container` na aba `Produtos`, renderizada via `@if` **apenas** para `currentUserRole() === 'ADMIN' || 'USER'` quando `pendingCount() > 0` (ou durante loading/error). Nunca dispara requisição ou renderiza para `SELLER`; desaparece completamente (`0` poluição visual) quando `pendingCount() === 0`.
- **Linha Pendente (`.curation-item`):** Bloco esquerdo clicável (`<button type="button" class="curation-item__trigger">`) com thumbnail `52×52px` (`assets/images/fitoherb-leaf-icon.png`), badge `Id_Pro <erpCode>`, nome do produto, fornecedor/categoria (destacados com `--tag-warning` se fallback) e badges `Sem foto` / `Novo do ERP`. Bloco direito irmão (`<div class="curation-item__actions">`) com `"Completar Foto"` e `"Ignorar / Não exibir no site"`. Limite inicial de 5 linhas visíveis com toggle `"Expandir"` quando `> 5`.
- **Abertura do `ModalEntityComponent` Pré-Preenchido:** Abre em `mode = 'edit'` com `name`, `description`, `category`, `supplier`, `topology` e `skus[]` pré-preenchidos, `[focusImageUpload]="true"` aplicando destaque (`2px dashed var(--color-primary)`, fundo `--bg-green-base`) e foco automático no upload (`label[for="image-input"]` com `tabindex="0"`, `Enter`/`Space`).
  - **Correção Crítica `isImageValid` (`modal-entity.component.ts:170-178`):** Em `mode() === 'edit'`, não bloquear salvamento se `imagePreview === null && selectedFile === null` — salvar alterações de texto/categoria mantendo `PENDING_IMAGE` (`toast` informativo), e remover imediatamente da fila + contador somente quando uma foto válida for salva.
- **Confirmação de Descarte (`"Ignorar / Não exibir no site"`):** Abre diálogo de confirmação (`ModalConfirmComponent` estendido) informando `"Ocultar produto do catálogo público?"`, nome + `Id_Pro`, campo opcional `"Motivo do descarte (opcional)"` e botão `"Confirmar e Ocultar"`.

### 9.4. Os 8 Estados Obrigatórios da `QuickCurationPanel`

| Estado | Comportamento |
| :--- | :--- |
| **Default** | Container branco acentuado à esquerda (`4px solid --color-primary`), header `--bg-green-base` com pill tabular de contagem + linhas de ação. |
| **Hover** *(`@media (hover: hover)`)* | Linha transita para `--green-50`; `"Completar Foto"` usa `--color-primary-hover`; `"Ignorar"` usa `--surface-danger`. |
| **Active** | `translateY(1px); filter: brightness(0.96);` imediato. |
| **Focus-Visible** | Anel instantâneo `2px solid var(--green-700); outline-offset: 2px;`. |
| **Disabled** | Enquanto ação do item em andamento: `opacity: 0.55; pointer-events: none; aria-disabled="true"`. |
| **Loading** | **2 linhas Skeleton Shimmer** (`.skeleton-shimmer`) espelhando thumbnail `52×52`, badge, título e 2 botões; sem spinner solitário e sem renderizar para `SELLER`. |
| **Empty** | `pendingCount === 0` ou `SELLER`: remoção completa do DOM (`@if`), zero espaço ocupado. |
| **Error** | Banner inline `--surface-danger` não-bloqueante acima da tabela (que segue 100% operável) com `"Tentar Novamente"` (`min-height: 44px`). |

### 9.5. Vitrine Sem Foto (`P-412`), Tabela Admin (`active = false`) e `ButtonComponent`

1. **`ItemCardGalleryComponent` & `ModalGalleryComponent`:** Atualizar `ProductRes.imageUrl: string | null`; criar `isPlaceholderImage = computed(() => !this.product()?.imageUrl && !this.hasImageError())`; adicionar `effect()` em `ItemCardGalleryComponent` para resetar `hasImageError` ao trocar `product()`; renderizar `'assets/images/fitoherb-leaf-icon.png'` sobre `--bg-green-base` / `--cream` com `.placeholder-image { opacity: 0.92; filter: none; object-fit: contain; }`, restringindo `.fallback-image` (`grayscale` + `0.55`) somente a falhas reais de rede (`(error)` com URL não-nula).
2. **`DynamicTableComponent` & `AdminComponent`:** Injetar fallback `'assets/images/fitoherb-leaf-icon.png'` quando `imageUrl === null` (`hasPlaceholderImage: true`, estilizado com `.product-img--placeholder`) para evitar `<img src="null">` quebrado; exibir badge `--tag-danger` `Oculto na Vitrine (Inativo no ERP)` (ou `Oculto na Vitrine (Ignorado)`) quando `active === false`, diferenciando de Multi-SKU parcial ativo (`--tag-warning` `Alerta Inativo ERP`) e `Sem foto` (`--tag-info`), com fundo neutro `var(--gray-100)` na linha `active === false` mantendo contraste AA.
3. **Hardening `ButtonComponent`:** `type = input<'button' | 'submit' | 'reset'>('button')` vinculado a `[attr.type]="type()"`, além de `type="button"` explícito em todos os botões auxiliares de modais, tabela e curadoria rápida (`modal-entity`, `modal-confirm`, `dynamic-table`, `QuickCurationPanel`).

### 9.6. Responsividade (`320 / 375 / 414 / 768 / 1280px`) & DoD Visual
- Mobile `< 640px`: ações da `QuickCurationPanel` empilham em coluna (`width: 100%; min-height: 44px`); `.table-responsive` com scroll horizontal suave e `overflow-x: clip`; card de vitrine mantém container `260px` alinhado na grade. Tablet/Desktop (`>= 640px` / `>= 1024px`): trigger à esquerda (`minmax(0, 1fr)`) + ações alinhadas à direita (`44px` de altura mínima).
- Validação em Quality Gate 4 garantirá ausência de scroll horizontal em `320px`, `44×44px` touch target, WCAG AA, respeito a `prefers-reduced-motion` e tokens exclusivos do `DESIGN_SYSTEM.md`.
