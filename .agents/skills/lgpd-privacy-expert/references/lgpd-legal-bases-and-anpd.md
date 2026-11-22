# Referência Técnica: LGPD, Bases Legais, Direitos do Titular e Gestão de Incidentes ANPD

Guia de consulta aprofundada para arquitetura, revisão de código e governança sob a **Lei nº 13.709/2018 (LGPD)** e regulamentações da **ANPD (Autoridade Nacional de Proteção de Dados)**.

---

## 1. Os 7 Princípios de Privacy by Design e Privacy by Default (Ann Cavoukian)

| # | Princípio | Tradução Prática em Engenharia de Software | Anti-Padrão Comum |
| :--- | :--- | :--- | :--- |
| 1 | **Proativo, não Reativo** | Modelagem de ameaças de privacidade (LINDDUN) e revisão de contratos antes do código. | Corrigir exposição de PII apenas após notificação da ANPD ou vazamento. |
| 2 | **Privacy by Default** | Opt-in explícito, cookies não essenciais desativados, perfil privado por padrão, coleta mínima. | Checkboxes pré-marcados de marketing ou `SELECT *` retornando campos desnecessários. |
| 3 | **Privacidade Incorporada ao Design** | Minimização no schema, segregação de PII em tabelas/vaults dedicados, RBAC/ABAC e RLS. | Tratar privacidade como banner de aviso sem alterar o fluxo real de dados. |
| 4 | **Funcionalidade Total (Soma-Positiva)** | Privacidade + UX fluida (ex.: autenticação passwordless segura, consentimento granular claro). | Bloquear toda a aplicação se o usuário recusar cookies de publicidade. |
| 5 | **Segurança de Ponta a Ponta** | TLS 1.3 em trânsito, AES-256 em repouso, mascaramento em logs, TTL e expurgo criptográfico. | Guardar dados indefinidamente sem política de retenção/descarte. |
| 6 | **Visibilidade e Transparência** | Avisos de privacidade em linguagem simples, logs de auditoria de acesso a PII, inventário (ROPA). | Termos genéricos que escondem compartilhamento com terceiros/operadores. |
| 7 | **Respeito ao Usuário (User-Centric)** | Portal ou endpoints de autoatendimento para exercício dos direitos do Art. 18. | Exigir processo manual burocrático para revogar consentimento dado em 1 clique. |

---

## 2. Classificação de Dados: Pessoais vs. Sensíveis vs. Pseudonimizados vs. Anonimizados

### 2.1 Dado Pessoal (Art. 5º, I)
Informação relacionada a pessoa natural identificada ou identificável:
- **Identificadores diretos:** Nome completo, CPF, RG, e-mail nominal, telefone, matrícula.
- **Identificadores indiretos (quase-identificadores):** Endereço IP, cookie de sessão, ID de dispositivo, geolocalização precisa, combinação de CEP + data de nascimento + profissão.

### 2.2 Dado Pessoal Sensível (Art. 5º, II)
Exige base legal mais restrita (**Art. 11**, sem Legítimo Interesse) e controles técnicos reforçados:
- Origem racial ou étnica;
- Convicção religiosa;
- Opinião política;
- Filiação a sindicato ou a organização de caráter religioso, filosófico ou político;
- Dado referente à saúde ou à vida sexual;
- Dado genético ou biométrico, quando vinculado a uma pessoa natural (ex.: reconhecimento facial, impressão digital, voz para autenticação).

> **Dados de Crianças e Adolescentes (Art. 14):** Sempre no melhor interesse; para crianças (< 12 anos), exige consentimento específico e em destaque de pelo menos um dos pais ou responsável legal, com esforço razoável de verificação.

### 2.3 Pseudonimização vs. Anonimização (Art. 12 e Art. 13, § 4º)
- **Pseudonimização:** Substituição de identificadores por tokens/chaves mantidas em cofre separado. **Continua sendo dado pessoal** sujeito à LGPD, mas reduz significativamente o risco em caso de incidente.
- **Anonimização:** Processo técnico irreversível considerando meios técnicos razoáveis e disponíveis na ocasião do tratamento (ex.: k-anonimato, l-diversidade, privacidade diferencial, agregação irreversível). **Fora do escopo da LGPD**, exceto se o processo puder ser revertido ou usado para formação de perfil comportamental (Art. 12, § 2º).

---

## 3. As 10 Bases Legais do Art. 7º e as Bases do Art. 11 (Dados Sensíveis)

### 3.1 Matriz das 10 Bases Legais (Art. 7º — Dados Pessoais Comuns)

| Inciso | Base Legal | Quando Usar | Requisitos / Cuidados Técnicos |
| :--- | :--- | :--- | :--- |
| I | **Consentimento** | Marketing, newsletters, analytics não essenciais, compartilhamento opcional. | Livre, informado, inequívoco, granular; registrar prova (timestamp, versão do termo, escopo) e permitir revogação fácil. |
| II | **Obrigação Legal ou Regulatória** | Logs do Marco Civil (6 meses), emissão de NF-e, eSocial, prevenção à lavagem de dinheiro (COAF). | Citar norma específica (lei, decreto, resolução) e respeitar o prazo legal exato de retenção. |
| III | **Execução de Políticas Públicas** | Administração Pública em leis, regulamentos ou convênios. | Não aplicável a empresas privadas fora de delegação pública. |
| IV | **Estudos por Órgão de Pesquisa** | Institutos de pesquisa oficialmente reconhecidos. | Garantir anonimização sempre que possível. |
| V | **Execução de Contrato** | Dados estritamente necessários para entregar o produto/serviço contratado ou procedimentos preliminares a pedido do titular. | Não usar como "guarda-chuva" para marketing ou venda de dados. |
| VI | **Exercício Regular de Direitos** | Defesa em processos judiciais, administrativos ou arbitrais. | Preservar evidências dentro do prazo prescricional aplicável. |
| VII | **Proteção da Vida / Incolumidade Física** | Emergências médicas ou risco iminente à vida do titular ou terceiro. | Uso excepcional e proporcional à emergência. |
| VIII | **Tutela da Saúde** | Procedimentos exclusivamente por profissionais de saúde, serviços de saúde ou autoridade sanitária. | Restrito ao ecossistema de saúde; não se aplica a apps fitness genéricos sem vínculo assistencial. |
| IX | **Legítimo Interesse** | Prevenção a fraudes, segurança de rede, comunicação com clientes ativos dentro da expectativa razoável. | **Proibido para dados sensíveis.** Exige **LIA (Teste de Balanceamento)** documentado, transparência e mecanismo de **Opt-Out**. |
| X | **Proteção do Crédito** | Consultas e registros em birôs de crédito (SPC/Serasa) conforme legislação específica. | Respeitar também o Código de Defesa do Consumidor e Lei do Cadastro Positivo. |

### 3.2 Bases Legais para Dados Sensíveis (Art. 11)
Para dados sensíveis, **não existe Legítimo Interesse** nem **Proteção do Crédito**. As hipóteses são:
1. **Consentimento específico e destacado** para finalidades específicas (Art. 11, I);
2. Sem consentimento, apenas quando **indispensável** para (Art. 11, II):
   - (a) Cumprimento de obrigação legal ou regulatória;
   - (b) Tratamento compartilhado de políticas públicas pela Administração Pública;
   - (c) Estudos por órgão de pesquisa (com anonimização sempre que possível);
   - (d) Exercício regular de direitos (inclusive em contrato e processo judicial/administrativo/arbitral);
   - (e) Proteção da vida ou da incolumidade física;
   - (f) Tutela da saúde;
   - (g) **Garantia da prevenção à fraude e à segurança do titular**, nos processos de identificação e autenticação de cadastro em sistemas eletrônicos (ex.: biometria antifraude), resguardados os direitos do Art. 9º.

---

## 4. Direitos do Titular (Art. 18 da LGPD) e Mapeamento de API

| Direito (Art. 18) | Significado Prático | Capacidade Técnica Esperada |
| :--- | :--- | :--- |
| **I. Confirmação de existência** | Informar se a organização trata dados do titular. | Consulta rápida por identificador verificado (resposta imediata em formato simplificado ou em até 15 dias em declaração completa — Art. 19). |
| **II. Acesso aos dados** | Fornecer cópia dos dados tratados, origem, critérios e finalidade. | Endpoint/exportação estruturada (JSON/PDF) sem expor segredos comerciais ou dados de terceiros. |
| **III. Correção** | Retificar dados incompletos, inexatos ou desatualizados. | Fluxo de atualização com propagação para réplicas/operadores. |
| **IV. Anonimização, bloqueio ou eliminação** | Para dados desnecessários, excessivos ou tratados em desconformidade. | Rotina de soft-delete + expurgo/anonimização definitiva (inclusive em backups/filas conforme política). |
| **V. Portabilidade** | Transferir dados a outro fornecedor de serviço/produto. | Exportação em formato interoperável (JSON/CSV) conforme regulamentação da ANPD. |
| **VI. Eliminação (Consentimento)** | Apagar dados tratados com base no consentimento. | Exceto nas hipóteses de conservação do Art. 16 (obrigação legal, estudo anonimizado, transferência a terceiro, uso exclusivo anonimizado). |
| **VII. Informação sobre compartilhamento** | Listar entidades públicas e privadas com quem houve compartilhamento. | Registro atualizado de operadores/suboperadores (ROPA). |
| **VIII. Informação sobre não consentir** | Explicar consequências claras de negar o consentimento. | UX transparente no momento da coleta. |
| **IX. Revogação do consentimento** | Retirar consentimento a qualquer momento por procedimento gratuito e facilitado. | Toggle/endpoint de revogação com efeito imediato no processamento futuro. |
| **Art. 20. Revisão de decisões automatizadas** | Solicitar revisão de decisões tomadas unicamente com base em tratamento automatizado (ex.: crédito, perfilamento). | Fila de revisão + explicação clara dos critérios (XAI), resguardado segredo comercial/industrial. |

---

## 5. Gestão de Incidentes de Segurança e Comunicação à ANPD (Resolução CD/ANPD nº 15/2024)

### 5.1 Quando Comunicar
A comunicação à ANPD e ao titular é obrigatória quando o incidente de segurança puder acarretar **risco ou dano relevante** aos titulares — caracterizado quando afetar significativamente interesses e direitos fundamentais **e** envolver pelo menos um destes critérios:
- Dados pessoais sensíveis;
- Dados de crianças, adolescentes ou idosos;
- Dados financeiros;
- Dados de autenticação em sistemas (senhas, tokens);
- Dados protegidos por sigilo legal, judicial ou profissional;
- Dados em larga escala.

### 5.2 Prazos Oficiais (Resolução CD/ANPD nº 15/2024)
- **Prazo geral:** **3 dias úteis** contados da data em que o controlador tomou conhecimento do incidente.
- **Agentes de pequeno porte (Resolução CD/ANPD nº 2/2022):** prazo em dobro (**6 dias úteis**).
- **Complementação de informações:** até **20 dias úteis** após a comunicação inicial (caso nem todas as evidências estejam concluídas nos primeiros 3 dias úteis).
- **Registro Interno de Incidentes (obrigatório mesmo sem comunicação):** manter registro por no mínimo **5 anos**.

### 5.3 Playbook de Resposta a Incidentes (5 Fases)
1. **Detecção e Triagem (T+0h):** Confirmar escopo, ativos afetados, tipo de comprometimento (confidencialidade, integridade ou disponibilidade) e acionar o DPO/Encarregado.
2. **Contenção e Preservação de Evidências (T+0h a T+4h):** Revogar credenciais/tokens, isolar serviços, preservar logs forenses (sem sobrescrever evidências).
3. **Avaliação de Risco Relevante (T+4h a T+24h):** Classificar categorias de dados, volume de titulares e impacto potencial; decidir pela notificação formal.
4. **Comunicação Formal (até 3 dias úteis):**
   - **À ANPD:** via formulário eletrônico oficial (descrição da natureza dos dados, titulares afetados, medidas técnicas/segurança adotadas, riscos, motivos de eventual atraso e medidas de mitigação).
   - **Aos Titulares:** em linguagem simples e direta, com orientações práticas de autoproteção e canal de contato do DPO.
5. **Erradicação, Lições Aprendidas e Registro:** Corrigir causa raiz, atualizar controles de segurança/RIPD e arquivar o registro interno por 5 anos.
