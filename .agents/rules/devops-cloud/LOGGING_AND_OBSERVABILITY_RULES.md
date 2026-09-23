# Regras de Logging e Observabilidade 🔍

**ATENÇÃO ENGENHEIROS DE BACKEND E DEVOPS:**
Se ocorrer um erro às 3 da manhã na sexta-feira, os logs devem nos contar exatamente o que aconteceu.

## 1. Fim dos "Console Logs" Amadores
- ❌ **Logs em Texto Simples:** Proibido o uso de `console.log("Usuário logou com id 10")` em produção. Eles são impossíveis de indexar e realizar buscas cruzadas no Datadog/Kibana/Cloud Logging.
- ✅ **A Solução (Structured Logging):** Todos os logs de Produção DEVEM ser escritos em formato **JSON**. A biblioteca de log (ex: Pino, Winston, Logrus) deve gerar automaticamente os campos de timestamp e severity.
  ```json
  // Correto
  { "level": "info", "timestamp": "2024-10...", "event": "USER_LOGIN", "userId": 10 }
  ```

## 2. A Lei da Correlação (Traceability)
- ❌ **Requisições Órfãs:** Num ambiente de alta concorrência ou microserviços, dezenas de logs se misturam. Impossível saber qual log pertence a qual chamada.
- ✅ **A Solução (Correlation ID):** Todo Request que entra na API deve receber/gerar um UUID (ex: `x-correlation-id`). ESSE ID deve ser obrigatoriamente injetado em TODOS os logs disparados durante a execução daquela requisição e deve ser enviado para serviços externos (banco, APIs terceiras).

## 3. Segurança no Transporte de Logs
- ❌ **Logs com PII:** Conforme reforçado na regra de Segurança, NENHUM log pode conter Dados Pessoais (Senhas, CPFs, Cartões).
- ✅ **A Solução:** A ferramenta de logger deve ser configurada na base da aplicação (via *Redaction*) para ofuscar (substituir por `***`) automaticamente chaves sensíveis como `password`, `token` e `document`.

## 4. O Sistema de Alertas
- ❌ **Alerte o Mundo:** Não crie alertas ou envie notificações no Slack para logs nível `INFO` ou `WARN` irrelevantes, causando "Fadiga de Alertas".
- ✅ **A Solução:** O nível `ERROR` é reservado exclusivamente para falhas sistêmicas que quebram o fluxo do usuário (Bancos fora, APIs fora, Bugs severos). `FATAL` deve disparar paginação pro engenheiro de plantão (SRE).
