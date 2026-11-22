# Guia Prático: Roteiro de 1:1 e Exemplos de Feedback SBI

Material pronto para conduzir reuniões 1:1 produtivas e dar feedbacks claros, objetivos e construtivos.

---

## 1. Roteiro de Reunião 1:1 (30 a 45 minutos)

A 1:1 é o espaço do **liderado** — não deve virar uma reunião de *status report* de tarefas da sprint.

### Preparação (Documento Compartilhado)
Ambos adicionam tópicos até 2 horas antes da reunião:
- `[Liderado]` Temas que quero trazer hoje
- `[Líder]` Pontos de contexto, reconhecimento ou feedback
- `[Ações]` Combinados da última 1:1 e status

### Estrutura Sugerida (35 min)
1. **Check-in Humano (5–10 min):**
   - *"Como você está chegando nesta semana, dentro e fora do trabalho?"*
   - *"O que tem te dado energia e o que tem drenado sua energia?"*
2. **Desafios, Bloqueios e Dinâmica do Time (10–15 min):**
   - *"Onde você sentiu mais atrito ou retrabalho nos últimos dias?"*
   - *"Há alguma decisão técnica ou de produto que não ficou clara para você?"*
   - *"Como posso te ajudar a destravar algo hoje?"*
3. **Carreira, PDI e Feedback Recíproco (10 min):**
   - *"O que você gostaria de aprender ou assumir no próximo trimestre?"*
   - *"O que eu, como Tech Lead, posso fazer diferente para te apoiar melhor?"*

---

## 2. Exemplos de Feedback Estruturado (SBI + Radical Candor)

O modelo **SBI** (**S**ituação — **C**omportamento observável — **I**mpacto concreto) elimina julgamentos pessoais e abre espaço para ação.

### Exemplo A — Feedback Corretivo (Interrupção em Cerimônia)
- **Situação:** *"Na reunião de refinamento de ontem às 14h..."*
- **Comportamento:** *"...quando a Ana começou a explicar a proposta de modelagem, você a interrompeu duas vezes e apresentou sua solução antes de ela concluir."*
- **Impacto:** *"...isso reduziu o espaço para ela contribuir, e depois ela me procurou insegura sobre expor ideias no grupo — o que prejudica a segurança psicológica da squad."*
- **Próximo Passo (Convite):** *"Como podemos combinar um sinal ou prática para garantir que todos concluam o raciocínio antes de debatermos alternativas?"*

### Exemplo B — Feedback Corretivo (PR Gigante sem Contexto)
- **Situação:** *"No Pull Request `#412` aberto na terça-feira..."*
- **Comportamento:** *"...você agrupou a refatoração de 18 arquivos com a nova feature de checkout sem descrição do contexto nem testes unitários para o fluxo de erro."*
- **Impacto:** *"...o review levou quase dois dias, travou o deploy da sprint e aumentou o risco de regressão em produção."*
- **Próximo Passo:** *"Na próxima entrega, vamos quebrar a refatoração em um PR separado e menor para acelerar o review e manter o histórico limpo?"*

### Exemplo C — Feedback Positivo / Reconhecimento (Reforço de Comportamento)
- **Situação:** *"Durante o incidente de latência no banco de dados na quinta-feira à noite..."*
- **Comportamento:** *"...você manteve a calma, documentou a linha do tempo no canal de incidentes em tempo real e conduziu o rollback sem apontar culpados."*
- **Impacto:** *"...reduzimos o tempo de recuperação para 12 minutos e todo o time se sentiu seguro para colaborar no post-mortem blameless no dia seguinte."*
- **Próximo Passo:** *"Esse é exatamente o padrão de liderança técnica que queremos na equipe — gostaria que você compartilhasse esse fluxo de resposta com os novos membros."*
