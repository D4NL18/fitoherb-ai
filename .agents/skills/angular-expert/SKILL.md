---
name: angular-expert
description: Especialista oficial em desenvolvimento Angular moderno, arquitetura reativa com Signals, Signal Forms, criação de novas aplicações com Angular CLI, SSR, Angular Aria, injeção com inject() e estilização com SCSS/Tailwind.
license: MIT
metadata:
  author: Angular Team @ Google & Core Architecture Team
  version: '2.0'
---

# Habilidade: Angular Expert & Modern Architecture 🅰️⚡

## Propósito
Você é a autoridade máxima em desenvolvimento Angular moderno, arquitetura de software frontend, reatividade orientada a Signals e boas práticas oficiais do time do Angular (Google). Sua missão é guiar a criação de novas aplicações robustas via Angular CLI, arquitetar componentes declarativos de alta performance, gerenciar estado reativo com Signals, garantir acessibilidade via Angular Aria e manter código TypeScript estritamente tipado e testável.

---

## Diretrizes Gerais e Ciclo de Qualidade

1. **Análise de Versão:** Sempre analise a versão do Angular do projeto antes de propor soluções, pois recursos e padrões (ex: Signal Forms, `resource`, `linkedSignal`, Control Flow `@if`/`@for`) variam entre versões. Para novos projetos, adote a versão estável mais recente.
2. **TypeScript em Modo Estrito:** Obrigatório o uso de TypeScript com `"strict": true`. Tipagens implícitas (`any`) são expressamente vetadas.
3. **Validação de Build Mandatória:** Ao finalizar qualquer geração ou modificação de código, execute `ng build` (ou `npx ng build`) para certificar-se de que não existem erros de compilação ou de template. Se houver falhas, corrija-as antes de prosseguir.

---

## 1. Criação de Novos Projetos (`ng new`)

Quando solicitado a criar um novo projeto Angular, siga o fluxo de execução:

### 1.1 Verificação do Angular CLI
- No Windows: `where ng` ou `gcm ng` (PowerShell).
- Se não estiver instalado globalmente, sugira a instalação ou execute diretamente via `npx`:
  ```bash
  npx @angular/cli@latest new <project-name> [flags]
  ```

### 1.2 Comando e Flags Recomendadas
```bash
npx ng new <app-name> --style=scss --routing --ssr --ai-config=agents --interactive=false
```
- **Flags Importantes:**
  - `--style=scss`: Formato oficial de folhas de estilo (ou `--style=css`).
  - `--routing`: Configuração automática de roteamento modularizado.
  - `--ssr`: Habilitação de Server-Side Rendering e hidratação para alta performance e SEO.
  - `--ai-config=agents`: Configura os arquivos de contexto de IA para ferramentas como Gemini e Copilot.
  - `--prefix=<prefix>`: Prefixo customizado dos seletores dos componentes (padrão: `app`).

Para guia detalhado de criação de apps, consulte [references/new-app.md](references/new-app.md).

---

## 2. Scaffolding com Angular CLI

Sempre utilize o Angular CLI para gerar artefatos, garantindo a nomenclatura padronizada e o registro correto no framework:
- **Componentes:** `npx ng generate component <nome>`
- **Serviços:** `npx ng generate service <nome>`
- **Pipes:** `npx ng generate pipe <nome>`
- **Diretivas:** `npx ng generate directive <nome>`
- **Interfaces:** `npx ng generate interface <nome>`
- **Guards:** `npx ng generate guard <nome>`
- **Interceptors:** `npx ng generate interceptor <nome>`
- **Resolvers:** `npx ng generate resolver <nome>`

Para melhores práticas do CLI, consulte [references/cli.md](references/cli.md).

---

## 3. Componentes Modernos (Standalone & Signals)

Angular moderno opera exclusivamente com **Standalone Components** (módulos `NgModule` são legados).

### 3.1 Anatomia e Controle de Fluxo
- Utilize a sintaxe moderna de controle de fluxo no template: `@if`, `@for (item of items(); track item.id)`, e `@switch`.
- Utilize tags auto-fecháveis (`<app-card />`) em componentes sem projeção de conteúdo.
- Consulte [references/components.md](references/components.md).

### 3.2 Signal Inputs e Outputs
- **Inputs:** Substitua o antigo decorator `@Input()` pela função de sinal `input()` ou `input.required()`:
  ```typescript
  title = input.required<string>();
  disabled = input<boolean>(false, { transform: booleanAttribute });
  ```
  Consulte [references/inputs.md](references/inputs.md).
- **Outputs:** Substitua `@Output() = new EventEmitter()` pela função `output()`:
  ```typescript
  itemSelected = output<string>();
  ```
  Consulte [references/outputs.md](references/outputs.md).
- **Host Elements:** Utilize o objeto `host` no decorator `@Component` ou funções de host binding:
  Consulte [references/host-elements.md](references/host-elements.md).
- **Convenções de Nomenclatura (v20+):** "Intenção sobre Papel" (*Intent over Role*):
  Consulte [references/naming-conventions.md](references/naming-conventions.md).

### 3.3 Componente Espelho Obrigatório
Antes de escrever componentes no projeto, espelhe a estrutura de comentários JSDoc e tipagem demonstrada em:
- [examples/angular-component.ts](examples/angular-component.ts)

---

## 4. Reatividade e Gerenciamento de Estado com Signals

Abandone o uso excessivo de RxJS em componentes quando Signals resolverem a reatividade de forma mais síncrona, previsível e sem *memory leaks*.

- **Signals Fundamentais (`signal`, `computed`):**
  - Crie estado reativo primário com `signal(initialValue)` e estado derivado puro com `computed(() => ...)`.
  - Use `untracked()` quando precisar ler um sinal dentro de um contexto reativo sem registrar dependência.
  - Consulte [references/signals-overview.md](references/signals-overview.md).
- **Estado Dependente Mutável (`linkedSignal`):**
  - Use `linkedSignal` para gerenciar estado que deriva de um sinal fonte mas precisa permitir sobrescrita manual pelo usuário (ex: seleção de opções).
  - Consulte [references/linked-signal.md](references/linked-signal.md).
- **Reatividade Assíncrona (`resource` & `httpResource`):**
  - Carregue dados assíncronos diretamente em um sinal reativo usando `resource()` ou `httpResource()`, simplificando estados de loading, value e error.
  - Consulte [references/resource.md](references/resource.md) e [references/http-client.md](references/http-client.md).
- **Efeitos Colaterais (`effect`):**
  - Restrinja `effect()` exclusivamente a logging, sincronização com APIs externas imperativas do DOM ou bibliotecas de terceiros (`afterRenderEffect`). Proibido alterar sinais dentro de `effect()` sem necessidade estrita.
  - Consulte [references/effects.md](references/effects.md).

---

## 5. Formulários: Signal Forms, Reactive e Template-Driven

1. **Novas Aplicações (Angular v22+):**
   - **Preferência Obrigatória: Signal Forms.** Gerencie o estado de formulários com base na nova API de sinais reativos.
   - Consulte o guia completo em [references/signal-forms.md](references/signal-forms.md).
2. **Formulários Reativos Tradicionais (Angular v15-v21):**
   - Use `FormGroup`, `FormControl` estritamente tipados com `NonNullableFormBuilder`.
   - Consulte [references/reactive-forms.md](references/reactive-forms.md).
3. **Formulários Simples baseados em Template:**
   - Para buscas pontuais e formulários simples, use Template-Driven Forms.
   - Consulte [references/template-driven-forms.md](references/template-driven-forms.md).

---

## 6. Injeção de Dependências e Comunicação HTTP

- **Uso da Função `inject()`:** Prefira a injeção via `inject(ServiceName)` diretamente na inicialização de campos no lugar de injeções verbosas no construtor.
- **Serviços Root:** Declare sempre `{ providedIn: 'root' }` em serviços singleton globais.
- **Comunicação HTTP:**
  - Configure provedores com `provideHttpClient(withFetch(), withInterceptors([...]))` em `app.config.ts`.
  - Maximize o uso do pipe `async` nos templates caso consuma Observables do `HttpClient`.
  - **Prevenção de Duplo Clique:** TODOS os botões de ação que disparam requisições assíncronas DEVEM ser desabilitados (`[disabled]="isLoading()"`) durante a espera, com feedback visual.
- Consulte:
  - [references/di-fundamentals.md](references/di-fundamentals.md)
  - [references/creating-services.md](references/creating-services.md)
  - [references/defining-providers.md](references/defining-providers.md)
  - [references/injection-context.md](references/injection-context.md)
  - [references/hierarchical-injectors.md](references/hierarchical-injectors.md)
  - [references/http-client.md](references/http-client.md)

---

## 7. Acessibilidade Headless com Angular Aria

Ao criar componentes customizados com suporte completo a acessibilidade WAI-ARIA, utilize as primitivas do **Angular Aria**:
- Padrões suportados: Accordion, Listbox, Combobox, Menu, Tabs, Toolbar, Tree, Grid.
- Consulte a referência oficial em [references/angular-aria.md](references/angular-aria.md).

---

## 8. Roteamento, SSR e Estratégias de Renderização

- **Definição de Rotas:** Declare rotas em `app.routes.ts` com lazy loading nativo de componentes (`loadComponent: () => import('./views/home.component')`).
- **Guards e Resolvers:** Utilize funções puras funcionais (`canActivate: [authGuard]`) com `CanActivateFn`.
- **Estratégias de Renderização:** CSR, SSG (Prerendering) e SSR com hidratação client-side estável.
- **Transições Suaves:** Ative `withViewTransitions()` no `provideRouter` para animações fluidas de página.
- Consulte:
  - [references/define-routes.md](references/define-routes.md)
  - [references/loading-strategies.md](references/loading-strategies.md)
  - [references/show-routes-with-outlets.md](references/show-routes-with-outlets.md)
  - [references/navigate-to-routes.md](references/navigate-to-routes.md)
  - [references/route-guards.md](references/route-guards.md)
  - [references/data-resolvers.md](references/data-resolvers.md)
  - [references/router-lifecycle.md](references/router-lifecycle.md)
  - [references/rendering-strategies.md](references/rendering-strategies.md)
  - [references/route-animations.md](references/route-animations.md)

---

## 9. Estilização: SCSS e Tailwind CSS v4

1. **SCSS com Design Tokens:**
   - Adote variáveis globais centralizadas (ex: `colors.scss`, `spacing.scss`).
   - Importe no `styles.scss` utilizando a sintaxe `@forward` ou `@use`.
   - Consulte [references/component-styling.md](references/component-styling.md).
2. **Tailwind CSS v4:**
   - Adicione com `npx ng add tailwindcss` seguindo o guia moderno do Tailwind v4.
   - Consulte [references/tailwind-css.md](references/tailwind-css.md).
3. **Animações Nativas:**
   - Prefira animações nativas em CSS / Web Animations API; reserve a biblioteca de animações legada apenas para sistemas existentes.
   - Consulte [references/angular-animations.md](references/angular-animations.md).

---

## 10. Arquitetura de Pastas Padronizada do Repositório

Para manter a organização em escala:
```
src/app/
├── core/         # Interceptors, guards, provedores globais singletons
├── services/     # Serviços de comunicação HTTP e regras de negócio
├── shared/       # Componentes visuais reutilizáveis (botões, cards, modals, pipes)
├── views/        # Telas completas roteadas diretamente (pages)
└── types/        # Modelos e interfaces organizados por domínio
    ├── auth/     # AuthReq.interface.ts, AuthRes.interface.ts
    └── users/    # UserProfile.interface.ts
```
- **Nomenclatura Obrigatória de Tipos:** Requisições de API devem terminar com `Req.interface.ts` e respostas com `Res.interface.ts`.

---

## 11. Testes Automatizados (TDD)

- **Testes Unitários:** Utilize Vitest ou Jest/Karma com `TestBed` para testes rápidos e isolados.
- **Component Harnesses:** Use `ComponentHarness` oficial do Angular CDK para interagir com o DOM de forma desacoplada da implementação HTML.
- **Router Testing:** Utilize `RouterTestingHarness` para validar navegações e redirecionamentos de forma determinística.
- Consulte:
  - [references/testing-fundamentals.md](references/testing-fundamentals.md)
  - [references/component-harnesses.md](references/component-harnesses.md)
  - [references/router-testing.md](references/router-testing.md)
  - [references/e2e-testing.md](references/e2e-testing.md)

---

## 12. Angular MCP Server e Migrações

- **Angular MCP Server:** O Angular CLI inclui um MCP server nativo acessível via `npx ng mcp` fornecendo a ferramenta `get_best_practices` diretamente ao assistente de IA.
- **Migrações Automáticas:** Para modernizar códigos legados para control flow ou signals, utilize `ng generate @angular/core:<migration-name>`.
- Consulte [references/mcp.md](references/mcp.md) e [references/migrations.md](references/migrations.md).

---

## Quality Gates
- [ ] Código compilando com zero erros através de `npx ng build`.
- [ ] Componentes gerados exclusivamente como Standalone com novo Control Flow (`@if`, `@for`).
- [ ] Estado e reatividade manipulados preferencialmente por Signals (`signal`, `computed`, `linkedSignal`, `resource`).
- [ ] Prevenção de múltiplos cliques em botões assíncronos (`[disabled]="isLoading()"`).
- [ ] Interfaces separadas em `src/app/types/` no padrão `[Nome]Req`/`[Nome]Res`.
- [ ] Arquitetura de estilos com SCSS (`@use`/`@forward`) ou Tailwind CSS validada.
- [ ] Testes unitários implementados e validados via `TestBed` / `ComponentHarness`.
