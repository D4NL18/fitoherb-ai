# Relatório de Impacto e Privacidade (RIPD/DPIA) & Privacy by Design: Chatbot Gemini

**Documento:** Auditoria Prévia de Privacidade e Enquadramento LGPD (Passo 3)  
**Encarregado (DPO / Privacy Officer):** `privacy_officer.md`  
**Base Legal:** Legítimo Interesse (Art. 7º, IX da LGPD) e Consentimento Implícito de Navegação  

---

## 1. Mapeamento de Fluxo de Dados e Minimização
- **Nenhum Dado Sensível Solicitado:** O chat é expressamente configurado para atender consultas de catálogo e institucionais. Não solicita CPF, nome, dados de pagamento ou prontuários médicos.
- **Guardrail de Saúde Ativo (Art. 11 da LGPD):** Caso o usuário relate espontaneamente dados sobre sua saúde física (ex: doenças, dores, sintomas), a regra `P-303` intercepta deterministicamente a mensagem. O texto não é enviado para o Gemini, não é gravado em cache e não é registrado em logs.
- **Sanitização de PII na Borda:** Expressões regulares mascaram preventivamente eventuais números de CPF, telefones pessoais, cartões e e-mails de visitantes antes de qualquer comunicação de rede.
- **Allowlist Institucional:** Os dados públicos da própria Fitoherb (CNPJ, telefone comercial, e-mail institucional) são cadastrados em allowlist para não sofrerem mascaramento indevido.

---

## 2. Transferência Internacional de Dados e Provedor de IA
- **Provedor:** Google Cloud Platform (Gemini API).
- **Enquadramento:** Projeto do DAM possui **faturamento ativo (billing ativo)**, o que garante contratualmente com a Google Cloud que os dados enviados via API corporativa **não são utilizados para treinamento de modelos públicos da Google**, resguardando o sigilo comercial da Fitoherb.
- **Efemeridade:** As conversas não são armazenadas em banco relacional no servidor. Ficam restritas à memória de sessão do navegador (`sessionStorage`) com expiração máxima de 30 minutos e controle de exclusão pelo usuário ("Limpar conversa").

---

## 3. Parecer do Privacy Officer
- **Status:** **APROVADO** com as salvaguardas técnicas acordadas (255 caracteres, sanitização de PII, guardrail de saúde e ausência de banco de logs de conversas com dados pessoais).
