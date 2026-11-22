# Guia de Referência: Seleção de Algoritmos, Pré-processamento e Métricas (ML Clássico)

## 1. Mapa de Seleção de Algoritmos

| Problema | Baseline Rápido | Modelo de Produção | Cuidados |
| :--- | :--- | :--- | :--- |
| **Regressão** | Regressão Linear / Ridge | XGBoost / LightGBM / Random Forest | Validar resíduos, RMSE vs MAE (outliers) e $R^2$. |
| **Classificação Binária / Multiclasse** | Regressão Logística / Árvore Podada | XGBoost / LightGBM / Random Forest | Usar `StratifiedKFold`, `predict_proba` e calibrar threshold. |
| **Clustering / Segmentação** | K-Means (método do cotovelo / Silhouette) | DBSCAN (detecta outliers como `-1`) / HDBSCAN | **Obrigatório** aplicar `StandardScaler` antes de calcular distâncias. |
| **Redução de Dimensionalidade** | PCA (`n_components=0.95`) | PCA / UMAP | PCA combina colunas linearmente (não descarta colunas brutas); exige scaling prévio. |

## 2. Prevenção de Overfitting e Data Leakage
- **Poda de Árvores:** Controlar `max_depth`, `min_samples_split` e `min_samples_leaf` reduz variância e impede memorização do treino.
- **Feature Scaling:** `StandardScaler` (média 0, desvio 1) para modelos baseados em distância/gradiente (SVM, KNN, Regressão, Redes Neurais, PCA, DBSCAN); `MinMaxScaler` quando limites `[0, 1]` são exigidos.
- **Zero Data Leakage:** Todo `Imputer`, `Scaler`, `Encoder` e `PCA` deve residir dentro de um `sklearn.pipeline.Pipeline` ajustado (`fit`) **exclusivamente** no conjunto de treino.

## 3. Métricas de Validação por Tarefa
- **Regressão:** MAE (robusta a outliers), RMSE (penaliza erros grandes), MAPE e $R^2$.
- **Classificação Balanceada:** Acurácia e F1-Macro.
- **Classificação Desbalanceada (fraude, churn, saúde):** **ROC-AUC**, **PR-AUC (Precision-Recall)**, Recall da classe minoritária e Matriz de Confusão.
- **Interpretabilidade:** `shap.TreeExplainer` (árvores/boosting) e `shap.KernelExplainer` (modelos caixa-preta).
