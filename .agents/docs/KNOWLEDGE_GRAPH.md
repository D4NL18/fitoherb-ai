# Knowledge Graph — Memória Comprimida do Projeto 🧠

> **Mantido por:** Orquestrador (`context-compressor`)

## 1. Épico 1: Roteirização Comercial Inteligente (`app/domains/routing/`)
- **Objetivo:** Otimização de rotas comerciais multi-parada (TDVRP) com Algoritmo Genético, modelo preditivo de tráfego por faixas horárias/corredores rodoviários, trava de ordem manual (`recalculate`) e geração de manifesto PDF.

## 2. Épico 2: Assistente Virtual Inteligente Fitoherb (`app/domains/chat/`)
- **Objetivo:** Chatbot flutuante (`POST /api/v1/chat/messages`) com guardrails determinísticos, roteamento semântico 0 tokens (`IntentRouter`), cache L1 SHA-256 (`ConversationCacheService`), busca neutra no catálogo (`CatalogIndex`) com redirecionamento automático (`NAVIGATE_CATALOG`) e integração enxuta com `gemini-2.5-flash` (`google-genai`).
- **Regras Centrais Ativas (`P-300` a `P-312`):**
  - `P-301` & `P-312`: Base institucional em `app/domains/chat/knowledge/company_profile.yaml` contendo telefone fixo `(71) 3379-7717`, WhatsApp oficial `(71) 99241-9709` (`https://wa.me/5571992419709`), Instagram oficial `@fitoherb` (`https://www.instagram.com/fitoherb`) e e-mail `comercial@fitoherb.com.br`.
  - `P-302` & `P-303`: Bloqueio determinístico de preços/estoque/tabela nutricional (`COMMERCIAL_RESTRICTED`) e de aconselhamento médico/ANVISA (`MEDICAL_RESTRICTED`) com 0 tokens.
  - `P-304` & `P-305`: Neutralidade absoluta entre marcas parceiras e redirecionamento automático (`NAVIGATE_CATALOG`) para `/produtos`.
  - `P-306` & `P-307`: Limite de entrada de 255 caracteres, proibição de travessões no meio de frases explicativas e compactação de histórico a partir de 5 mensagens.
  - `P-308` & `P-312`: `IntentRouter` responde com 0 tokens (`STATIC_KB`) para saudações (`GREETING`), endereço (`COMPANY_LOCATION`), redes sociais/Instagram (`COMPANY_SOCIAL`), telefone/WhatsApp/e-mail (`COMPANY_CONTACT`), história (`COMPANY_ABOUT`) e cobertura (`COMPANY_COVERAGE`), fazendo bypass para o `ChatOrchestrator` quando há menção composta a produtos.
