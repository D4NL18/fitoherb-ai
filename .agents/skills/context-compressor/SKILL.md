---
name: context-compressor
description: Skill de gestão de memória para sumarizar regras de features concluídas, economizando tokens de contexto.
---
# Habilidade: Context Compressor

## Propósito
Em projetos grandes, as LLMs tendem a estourar os limites de contexto ao ler centenas de arquivos. O objetivo desta skill é fornecer regras para condensar a "memória do projeto" de forma super otimizada.

## Diretrizes Obrigatórias
1. **O Gatilho:** Quando uma funcionalidade for concluída no Roadmap (Step final do Workflow), o Orquestrador pode usar esta skill para fazer a Compressão de Contexto.
2. **KNOWLEDGE_GRAPH.md:**
   - Todo resumo vital (regras de negócio superadas, decisões de arquitetura cruciais, dependências criadas) deve ser extraído dos arquivos alterados e salvo de forma extremamente curta (em formato de bullet points ou JSON minimalista) num arquivo `.agents/context/KNOWLEDGE_GRAPH.md` (ou `MEMORY.md`).
3. **Regra do Descarte:**
   - O Context Compressor foca apenas em *decisões definitivas*. Falhas, bugs antigos e rascunhos de código do processo devem ser "esquecidos". Guarde apenas: o que faz a feature, como ela interage com as demais e a regra de negócio central.
4. **Alimentando o Orquestrador:**
   - Ao iniciar as próximas features, o Orquestrador deve ler este arquivo sumarizado em vez de escanear o projeto inteiro para recuperar o contexto do que já foi feito.
