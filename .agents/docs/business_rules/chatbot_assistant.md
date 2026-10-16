# Regras de Negócio: Assistente Virtual Inteligente (Chatbot Gemini)

**Domínio:** Atendimento ao Cliente, Catálogo e Inteligência Artificial  
**Feature:** Chat Flutuante Integrado ao Catálogo e Perfil Institucional  

---

## 1. Regras de Negócio (P-300 a P-312)

### P-300: Delimitação Estrita de Escopo Institucional e Catálogo
O assistente é exclusivamente dedicado a responder sobre a **Fitoherb** (histórico, missão, dados públicos de contato, redes sociais oficiais, localização) e seu **catálogo de produtos** (categorias, marcas/fornecedores parceiros, sabores e formatos de apresentação).
- Qualquer questionamento que fuja deste domínio (ex: política externa, programação genérica, receitas culinárias não relacionadas aos produtos, piadas, futebol) deve ser respondido com recusa cortês padrão informando que o assistente só está habilitado para informações sobre a Fitoherb e seus produtos distribuídos.

### P-301: Fidelidade Institucional e Proibição de Alucinação Factual
Informações sobre a empresa (incluindo telefone fixo `(71) 3379-7717`, WhatsApp `(71) 99241-9709`, e-mail `comercial@fitoherb.com.br` e Instagram `@fitoherb` / `https://www.instagram.com/fitoherb`) devem derivar estritamente do arquivo de perfil institucional (`company_profile.yaml`).
- O assistente não deve inventar dados ausentes (como horários específicos de expediente, nomes de funcionários ou redes sociais não cadastradas). Se o dado não constar na base, a resposta deve declarar claramente: *"Não disponho dessa informação no momento. Para detalhes adicionais, entre em contato com nossa equipe comercial pelo telefone (71) 3379-7717, WhatsApp (71) 99241-9709 ou e-mail comercial@fitoherb.com.br."*

### P-302: Proibição de Valores Comerciais, Estoque e Tabelas Nutricionais
O assistente está terminantemente proibido de fornecer ou estimar:
1. Preços, valores monetários ou orçamentos.
2. Níveis de estoque ou prazos de entrega específicos.
3. Tabelas nutricionais detalhadas, laudos laboratoriais ou composição miligramada não contida na descrição do produto.
- Em tais casos, o assistente deve responder sucintamente que não possui acesso a valores comerciais ou estoque e convidar o cliente a contatar o time de vendas.

### P-303: Veto a Pareceres Médicos e Farmacêuticos (ANVISA)
O assistente não prescreve, indica tratamentos nem diagnostica patologias. Caso o usuário descreva sintomas clínicos, dosagens ou solicite recomendações de cura, a resposta deve orientar a consulta a um profissional de saúde qualificado (médico ou nutricionista). Esta resposta é acionada deterministicamente via guardrail, sem invocação de LLM nem retenção em logs.

### P-304: Neutralidade Absoluta e Isonomia de Fornecedores e Marcas
O assistente deve tratar todas as marcas e fornecedores parceiros da Fitoherb com absoluta equidade.
- É vedado fazer sugestões unilaterais de "melhor marca", ranquear fornecedores ou incentivar compra de determinada empresa em detrimento de outra.
- Ao listar opções (ex: "Whey 100%"), deve apresentar os itens correspondentes no catálogo sem emitir juízo de valor ou preferência.

### P-305: Redirecionamento Automático com Filtros no Catálogo
Quando o usuário solicitar listagem, opções ou recomendações de produtos (ex: "quais as opções de whey 100%?"), o sistema deve:
1. Identificar as facetas (`category`, `supplier`) e o termo de busca textual (`search`).
2. Retornar no payload da API a instrução de ação `NAVIGATE_CATALOG` com os parâmetros higienizados.
3. No front-end, redirecionar automaticamente a rota para `/produtos` aplicando os query params (`/produtos?category=...&supplier=...&search=...`).
4. O chat deve permanecer aberto durante a navegação, exibindo a resposta direta sem cobrir totalmente a lista de produtos carregada.

### P-306: Trava de Entrada e Limites Textuais Conciso
- A mensagem do usuário possui limite rígido de **255 caracteres**. Entradas superiores a 255 caracteres são rejeitadas na borda com código HTTP 400.
- A resposta gerada pelo assistente deve ser concisa, direta e curta (máximo de 200 a 250 tokens de saída).
- Evitar vocabulário rebuscado, palavras difíceis e evitar o uso de travessão (`-`) no meio de frases explicativas (permitido apenas como marcador de itens em listas/bullet points).

### P-307: Compactação Automática de Histórico (Memory Optimization)
A partir de **5 mensagens** no histórico da conversa, o cliente e o serviço de IA acionam a rotina de compactação e poda semântica:
- Mensagens mais antigas são condensadas em um contexto resumido único, preservando apenas as últimas 2 rodadas completas (usuário e assistente) para manter o consumo de tokens previsível e mínimo.

### P-308: Roteamento Semântico e Bypass de LLM para Fatos Simples
Perguntas diretas sobre fatos institucionais mapeados (endereço, telefone, WhatsApp, Instagram, redes sociais, e-mail institucional, quem somos) e saudações comuns são respondidas diretamente por templates estáticos da base de conhecimento no `IntentRouter`, consumindo **0 tokens** de modelo generativo.

### P-309: Versão Mais Recente e Resiliente do Gemini Flash
A integração com o Google Gemini deve utilizar o SDK oficial unificado `google-genai`. O modelo padrão utilizado deve ser a versão estável mais moderna disponível (alias preferencial dinâmico `gemini-2.5-flash`), com fallback determinístico caso ocorra instabilidade na API externa.

### P-310: Cache Semântico L1 com SHA-256 e TTL
Perguntas repetidas sobre a empresa e produtos utilizam cache em memória L1 baseado no hash SHA-256 da consulta normalizada.
- TTL para dados institucionais: 24 horas.
- TTL para catálogo: 1 hora (invalidado automaticamente ao atualizar o catálogo).
- Mensagens contendo potenciais dados pessoais (PII) ou relativas à saúde têm bypass compulsório de cache.

### P-311: Privacidade, Transparência e Efemeridade (LGPD)
Nenhuma conversa é persistida em banco de dados relacional no servidor.
- O histórico reside temporariamente no `sessionStorage` do navegador do cliente por no máximo 30 minutos.
- A interface disponibiliza botão "Limpar Conversa".
- O assistente se identifica expressamente como inteligência artificial e exibe aviso para não compartilhamento de dados pessoais ou bancários.

### P-312: Informações Oficiais de Redes Sociais e Canais Digitais (WhatsApp e Instagram)
Quando o usuário perguntar sobre redes sociais, Instagram, WhatsApp ou canais digitais da Fitoherb, o assistente DEVE fornecer os canais oficiais homologados:
- **WhatsApp Oficial:** `(71) 99241-9709` (link direto: `https://wa.me/5571992419709`)
- **Instagram Oficial:** `@fitoherb` (`https://www.instagram.com/fitoherb`)
- **Canais Complementares de Contato:** Telefone fixo `(71) 3379-7717` e e-mail comercial `comercial@fitoherb.com.br`.
- **Regras de Resolução e FinOps:**
  1. Consultas diretas por Instagram, WhatsApp ou redes sociais devem ser resolvidas com **0 tokens** pelo `IntentRouter` (em conformidade com a `P-308`).
  2. Os dados oficiais de redes sociais e WhatsApp devem estar presentes tanto no `company_profile.yaml` quanto na instrução de sistema (`system_instruction`) do `ChatOrchestrator`, assegurando que perguntas compostas processadas pelo Gemini incluam essas informações sem alucinar perfis inexistentes.
