# Anti-Padrões de Custo na Nuvem (FinOps) 💸

**ATENÇÃO ARQUITETOS, DEVOPS E DESENVOLVEDORES:**
A arquitetura Serverless e Cloud salva você da manutenção, mas cobra caro pela falta de governança.

## 1. Poison Messages e Exponential Backoff
- ❌ **Retentativas Infinitas em Fila:** É PROIBIDO escutar filas (SQS, Pub/Sub, RabbitMQ) e devolver erros continuamente. Se o banco falhar, o serviço tentará reler a mensagem milhões de vezes em minutos, estourando os custos.
- ✅ **A Solução:** Filas devem obrigatoriamente possuir uma configuração de `Dead Letter Queue (DLQ)` ou um limite estrito de `Max Receive Count` (ex: 3 vezes). Os processadores devem sempre implementar o *Exponential Backoff* (esperar 1s, 2s, 4s...) ao invés de bater repetidamente na API falha.

## 2. Storage Sem Ciclo de Vida
- ❌ **Lixo Eterno:** Jamais crie um Bucket no Cloud Storage ou S3 (arquivos de backup temporários, avatares antigos, faturas processadas) que mantenha o dado para sempre se ele for efêmero.
- ✅ **A Solução:** O Terraform ou script DevOps DEVE obrigatoriamente criar *Object Lifecycle Policies* (ex: "Excluir objetos na pasta /temp/ após 7 dias").

## 3. Limites de Alocação de Máquina
- ❌ **Scale-Up Infinito:** Nunca instancie funções na nuvem (Cloud Run, Lambda, Fargate) deixando a "CPU e RAM máxima" livres ou no valor mais alto. Um loop acidental na sua aplicação vai escalar as instâncias até o teto do seu cartão de crédito.
- ✅ **A Solução:** Use orçamentos estritos de CPU. Teste e prove que a aplicação sobrevive com *512MB RAM e 0.5 CPU*. Se precisar de mais, faça *profiling*, não aumente cegamente. E claro, use Scale-to-Zero para ambientes de Teste e Dev.
