# Regras de CI/CD e Infraestrutura (DevOps) 🚀

**ATENÇÃO ENGENHEIROS DEVOPS E ARQUITETOS:**
A esteira de integração contínua (CI) é a barreira final antes da produção. O vazamento de um Secret compromete toda a empresa.

## 1. Gestão de Segredos (API Keys e Tokens)
- ❌ **Hardcoding de Segredos:** É TOTALMENTE PROIBIDO realizar *commit* de arquivos que contenham chaves de API, senhas de banco de dados, ou credenciais SSH em texto plano. 
- ✅ **A Solução (12 Factor App):**
  - Toda e qualquer variável de conexão DEVE vir das variáveis de ambiente (`process.env.SUA_VARIAVEL`).
  - O repositório deve conter um arquivo chamado `.env.example` apenas com a estrutura das variáveis (sem os valores reais).
  - Em produção (GCP/AWS/Azure), os valores devem ser providos pelo "Secret Manager" oficial da plataforma na nuvem.

## 2. Qualidade Mínima de Pipeline (CI)
- ❌ **Deploy Direto/Cego:** Nenhuma branch pode ser mesclada (*merged*) na `main` ou `develop` sem passar pela esteira CI/CD (GitHub Actions, GitLab CI, etc).
- ✅ **A Solução:** Todo *Pull Request* exige a criação de um arquivo de Workflow (`.github/workflows/ci.yml`) que contenha os 3 passos obrigatórios:
  1. Instalar as dependências e executar o linter (`npm run lint` ou similar).
  2. Executar a suíte de Testes Unitários de forma automatizada (se falhar, bloqueia o PR).
  3. Realizar o Build/Compilação do código para confirmar que a aplicação sobe sem quebrar.

## 3. Segurança Base de Repositório
- ❌ Nunca deixe a porta do banco de dados (ex: `5432` do Postgres, `3306` do MySQL) exposta para o mundo (`0.0.0.0`) no ambiente de produção. Utilize Virtual Private Clouds (VPC).
- ❌ Mantenha um arquivo `.gitignore` rigoroso desde o primeiro commit para impedir o envio das pastas `node_modules`, `/dist` ou `/build`.
