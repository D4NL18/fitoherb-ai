# Regras de Negócio — E-mail de Contato (Mail)

> **Módulo:** Formulário de Contato e Captação de Leads  
> **Identificador:** P-MAIL-001 a P-MAIL-004

---

## P-MAIL-001: Validações Estritas de Entrada
1. O campo `name` é obrigatório, não pode conter apenas espaços em branco e deve respeitar o intervalo de 3 a 150 caracteres.
2. O campo `email` deve seguir o padrão RFC 5322.
3. O campo `phone` é obrigatório para possibilitar contato imediato da equipe de televendas.
4. O campo `message` deve possuir conteúdo substancial (mínimo de 10 caracteres) e limite de 2000 caracteres para mitigar abusos.

---

## P-MAIL-002: Proteção contra Falhas e Mascaramento de Erros
1. Se ocorrer indisponibilidade na porta SMTP ou rejeição de autenticação pelo servidor Gmail, a exceção `MailSendingException` é disparada.
2. As credenciais e senhas de app não devem sob hipótese alguma ser expostas nas mensagens de erro retornadas aos clientes da API.

---

## P-MAIL-003: Higienização contra Injeção de Cabeçalhos
1. Entradas com quebras de linha (`\r`, `\n`) em campos de cabeçalho (`name`, `subject`) devem ser tratadas para evitar Header Injection SMTP.

---

## P-MAIL-004: Conformidade com LGPD
1. Os dados de contato fornecidos pelo titular destinam-se exclusivamente ao atendimento da solicitação de contato comercial iniciada pelo próprio titular.
