# Isolamento Rígido de Regra de Negócio (Clean Arch) 🏗️

**ATENÇÃO ARQUITETOS, DESENVOLVEDORES E REVIEWERS:**
O framework que você usa hoje será obsoleto amanhã. A Regra de Negócio é soberana e não pertence ao Framework.

## 1. Controllers Não Pensam (API Backend)
- ❌ **A Regra de Negócio na Porta:** É PROIBIDO injetar lógica "Se o valor X for maior que Y calcule Z e salve no banco" diretamente na função da rota (Controller / Route Handler / Resolver).
- ✅ **A Solução:** O Controller tem apenas três funções:
  1. Receber o input do cliente.
  2. Acionar a camada correta (Service / Use Case).
  3. Devolver o output transformado pro cliente.
  O "Se, E, Ou" mora apenas nas Camadas de Domínio.

## 2. Frontend "Burro" (Dumb Visuals)
- ❌ **O Botão que Faz Mágica:** No Frontend, os componentes Visuais (HTML/CSS + TS/JS básicos) não podem consultar APIs diretamente nem formatar moedas em tempo de renderização misturados com tags `<div>`.
- ✅ **A Solução:** Os componentes devem receber e despachar Ações. Toda a mágica acontece nos `Services` ou em utilitários e pipes. O componente Visual só sabe desenhar o que lhe é mandado.

## 3. Isolamento do Banco de Dados (Repository Pattern)
- ❌ **Acoplamento ORM Indireto:** A regra de negócio principal (`UserDomain`) não deve importar funções nativas do ORM (ex: `PrismaClient` ou `Mongoose` dentro da função de Cálculo de Saldo).
- ✅ **A Solução:** Todo acesso ao banco deve ser abstraído via *Repositories*. A regra de negócio pede para o `UserRepository.save(user)` e nunca importa como o Repository se vira para executar o SQL real.
