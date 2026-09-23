# Padrão de Histórico e Commits (Git Rules) 📜

**ATENÇÃO DESENVOLVEDORES, DEVOPS E REVIEWERS:**
O histórico de commits é a principal documentação técnica de uma funcionalidade ao longo do tempo. Mensagens de commit lixo criam um repositório lixo.

## 1. Conventional Commits (Obrigatório)
- ❌ **Mensagens Vagas:** É EXPRESSAMENTE PROIBIDO fazer commits como: `git commit -m "update"`, `"fix typo"`, `"wip"`, ou `"corrigindo banco"`.
- ✅ **A Solução:** Abrace totalmente o padrão do *Conventional Commits*. O sistema de CI poderá rejeitar PRs que fujam deste formato:
  - `feat: adiciona login com oauth`
  - `fix(auth): corrige validacao de jwt nulo`
  - `docs(readme): atualiza variaveis de ambiente`
  - `chore(deps): atualiza versao do angular`
  - `refactor: move funcoes genericas para services`

## 2. A Lei do "Atomic Commit"
- ❌ **Commit Gigantesco:** Não trabalhe 5 dias sem fazer commit e lance tudo de uma vez como `feat: varias telas e apis do sistema`.
- ✅ **A Solução:** Commits devem ser **Atômicos**. Cada commit deve representar uma, e apenas UMA mudança lógica independente e funcional. (ex: Criação do banco é um commit, criação do repositório é outro, criação da UI é outro).

## 3. Descrição Obrigatória em Breaking Changes
- ❌ **Aviso Silencioso:** Se a mudança alterar um contrato de API que outros serviços consumiam, isso não pode ser disfarçado.
- ✅ **A Solução:** Para `BREAKING CHANGES`, adicione `!` após o prefixo (ex: `feat!: altera resposta da api de auth`) e descreva no rodapé do commit o que precisa ser migrado.
