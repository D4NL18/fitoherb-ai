# Regras de MLOps, Deploy e Prevenção de Drift 🔄📦

**ATENÇÃO ESPECIALISTA EM IA, DEVOPS E REVIEWERS:**
Modelos de Machine Learning e Deep Learning não são softwares estáticos; eles sofrem degradação contínua ao longo do tempo.

---

## 1. Separação Física entre Treino e Inferência
- ❌ **Código de Treino no Servidor de Produção:** É TERMINANTEMENTE PROIBIDO carregar datasets crus de treino (CSVs gigantes), scripts de grid search e rotinas de treino dentro da imagem Docker do backend produtivo.
- ✅ **A Solução:**
  1. O código de experimentação e treino DEVE residir na pasta `training_scripts/`.
  2. A imagem Docker de produção DEVE conter apenas a pasta de serviço (`app/ml/` ou `services/`) e os pesos matemáticos serializados (`weights/`).
  3. Adicione `training_scripts/` e `datasets/` no `.dockerignore`.

---

## 2. Monitoramento Contínuo de Drift
- ❌ **Modelo Abandonado em Produção:** Subir um modelo e nunca monitorar a distribuição dos dados de entrada.
- ✅ **A Solução:**
  1. Monitore **Data Drift**: Verifique se a média, variância e distribuição das features de entrada estão divergindo dos dados com os quais o modelo foi treinado.
  2. Monitore **Concept Drift**: Verifique se a relação entre as features e os resultados de negócio reais sofreu ruptura.
  3. Quando um drift estatisticamente significativo for detectado, configure alerta para retreinamento supervisionado com *Human-in-the-Loop*.

---

## 3. Imutabilidade e Versionamento de Pesos
- ❌ **Sobrescrever Pesos Sem Rastreabilidade:** Substituir um arquivo `.joblib` ou `.pth` em produção sem tag de versão.
- ✅ **A Solução:**
  1. Cada modelo deve possuir versão declarada nos metadados (ex: `v1.2.0`).
  2. Utilize registries consolidados como **MLflow** ou **Hugging Face Hub** para rastreabilidade de hiperparâmetros, métricas de validação e dataset de origem.
