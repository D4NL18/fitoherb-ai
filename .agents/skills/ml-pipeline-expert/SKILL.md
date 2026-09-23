---
name: ml-pipeline-expert
description: Especialista em esteiras de Machine Learning tabular clássico com Scikit-Learn, pré-processamento, prevenção contra Data Leakage, calibração com predict_proba e serialização de modelos.
---
# Habilidade: Scikit-Learn ML Pipeline Engineer 📊🔬

## Propósito
Você é o especialista responsável pelo pré-processamento de dados, engenharia de atributos, modelagem estatística supervisionada e não-supervisionada, validação cruzada robusta e exportação de esteiras reprodutíveis de Machine Learning com **Scikit-Learn**, **XGBoost** e **LightGBM**.

---

## Gatilhos de Uso (Trigger & Scope)
Utilize esta skill obrigatoriamente quando:
- Construir ou otimizar esteiras de pré-processamento (imputação de nulos, normalização, one-hot encoding, redução dimensional com PCA).
- Treinar modelos para dados tabulares estruturados (Random Forest, XGBoost, Regressão Logística, SVM, KNN, K-Means).
- Prevenir vazamento de dados (*Data Leakage*) garantindo que todo escalonamento ocorra exclusivamente dentro do `Pipeline` e dos folds de validação cruzada.
- Otimizar hiperparâmetros utilizando `GridSearchCV` ou `RandomizedSearchCV` com métricas adequadas ao domínio (`f1_macro`, `recall`, `roc_auc`).
- Exportar e serializar pipelines completos contendo transformadores e estimadores em arquivos `.joblib` ou `.pkl`.

---

## Competências Principais e Boas Práticas

### 1. Prevenção Absoluta contra Data Leakage
- **Regra Inegociável:** NUNCA aplique `fit` ou `fit_transform` de um `StandardScaler`, `PCA` ou `SimpleImputer` no dataset inteiro antes de dividir em treino e teste (`train_test_split`).
- Encapsule transformadores e estimadores em um único objeto `Pipeline` ou `ColumnTransformer` do Scikit-Learn. O método `fit` deve ser acionado apenas nos dados de treino.

### 2. Inferência com `predict_proba()` vs `predict()`
- Para problemas de classificação em sistemas de produção (especialmente medicina, fraude ou score financeiro), utilize sempre `predict_proba()`.
- Obter a probabilidade calibrada permite implementar thresholds dinâmicos de decisão, zonas de incerteza (*Human-in-the-Loop*) e votação em sistemas de ensemble.

### 3. Métricas Alinhadas ao Domínio de Negócio
- Não confie em acurácia pura em datasets desbalanceados.
- Em cenários com classes raras (ex: diagnósticos médicos de câncer, detecção de fraude), maximize o **Recall** (Sensibilidade) para minimizar falsos negativos, ou utilize `F1-Score` e `PR-AUC`.

### 4. Serialização e Versionamento do Artefato
- Exporte o pipeline treinado via `joblib.dump(pipeline, "weights/modelo.joblib", compress=3)`.
- Salve sempre metadados com: versão das bibliotecas, métricas de validação cruzada, data de treino e schema esperado das features.

---

## Template de Implementação (Pipeline Completo + GridSearchCV + Exportação)

```python
import os
import joblib
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.metrics import classification_report, roc_auc_score

def build_and_train_pipeline(df, feature_cols_num, feature_cols_cat, target_col, output_path="weights/model_pipeline.joblib"):
    # 1. Separação de Treino e Teste com Estratificação
    X = df[feature_cols_num + feature_cols_cat]
    y = df[target_col]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 2. Pré-processadores por Tipo de Coluna
    numeric_transformer = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, feature_cols_num),
            ('cat', categorical_transformer, feature_cols_cat)
        ]
    )

    # 3. Pipeline Unificado (Evita Data Leakage)
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(random_state=42, class_weight='balanced'))
    ])

    # 4. Grade de Hiperparâmetros e Validação Cruzada Estratificada
    param_grid = {
        'classifier__n_estimators': [100, 200],
        'classifier__max_depth': [5, 10, None],
        'classifier__min_samples_split': [2, 5]
    }

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    grid_search = GridSearchCV(
        pipeline, param_grid, cv=cv, scoring='f1_macro', n_jobs=-1, verbose=1
    )

    grid_search.fit(X_train, y_train)

    # 5. Avaliação no Conjunto de Teste (Cego)
    best_model = grid_search.best_estimator_
    y_pred = best_model.predict(X_test)
    y_proba = best_model.predict_proba(X_test)[:, 1]

    print("=== Relatório de Classificação ===")
    print(classification_report(y_test, y_pred))
    print(f"ROC-AUC Score: {roc_auc_score(y_test, y_proba):.4f}")

    # 6. Serialização Segura do Pipeline Completo
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    joblib.dump(best_model, output_path, compress=3)
    print(f"Pipeline serializado com sucesso em: {output_path}")

    return best_model
```

---

## Quality Gates
- [ ] Pré-processadores e classificadores encadeados estritamente via `Pipeline`/`ColumnTransformer`.
- [ ] Zero *Data Leakage* (transformações aplicadas somente após divisão dos folds).
- [ ] Validação cruzada estratificada (`StratifiedKFold`) configurada na busca de hiperparâmetros.
- [ ] Avaliação por métricas alinhadas ao negócio (`Recall`, `F1-Score`, `ROC-AUC`).
- [ ] Modelo serializado com todos os transformadores incluídos para execução direta na API.

---

## Técnicas Avançadas de ML (Pós IA para Devs, p. 171-237)

### Feature Engineering Avançado
- **Criação de Features Derivadas:** Combinação de variáveis de domínio (ratios, interações multiplicativas, agregações estatísticas por grupo).
- **Tratamento de Datas e Séries Temporais:** Decomposição em componentes cíclicos (seno/cosseno do dia da semana e mês), extração de flags de feriados/dias úteis, lags temporais e médias móveis exponenciais.
- **Tratamento de Textos e Categóricas:** TF-IDF n-grams para campos textuais curtos, Target Encoding com regularização e One-Hot Encoding com descarte de alta cardinalidade para evitar explosão dimensional.

### Análise Bivariada e Correlação Pós-Encoding
- **Variáveis Categóricas e Numéricas em Heatmaps:** Aplicação de correlação de Spearman / Pearson pós-One-Hot Encoding ou Cramer's V / Theil's U para variáveis puramente categóricas.
- **Casos de Uso de Domínio:**
  - *MBA vs Contratação:* Avaliação de hipótese nula via teste qui-quadrado ($\chi^2$) e visualização bivariada de taxas de conversão de recrutamento.
  - *Salário vs Gênero:* Detecção e auditoria de dispersão salarial cruzada com anos de experiência para auditoria de viés antes do treinamento.

### Sensibilidade de Escala por Algoritmo
- **Sensíveis à Escala (Escalonamento OBRIGATÓRIO):**
  - **KNN (K-Nearest Neighbors), SVM e Redes Neurais / Deep Learning:** A distância euclidiana ou o gradiente descendente são diretamente dominados por features com ordens de grandeza elevadas. Obrigatório utilizar `StandardScaler` (distribuição normal) ou `MinMaxScaler` (intervalo fixo $[0, 1]$ ou dados com suporte limitado).
- **Invariantes à Escala (Escalonamento DESNECESSÁRIO):**
  - **Árvores de Decisão, Random Forest, Gradient Boosting, XGBoost, LightGBM, CatBoost:** As divisões nos nós (*splits*) dependem apenas da ordenação dos valores e do ganho de informação (Gini/Entropia), tornando transformações monotônicas de escala irrelevantes.

### Pipelines Scikit-Learn com ColumnTransformer e StratifiedKFold
```python
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.model_selection import StratifiedKFold, cross_val_score
from xgboost import XGBClassifier

# Definição de pipelines específicos por tipo de coluna
numeric_features = ['idade', 'renda_anual', 'score_credito']
numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())  # Crucial se modelos sensíveis forem testados
])

categorical_features = ['escolaridade', 'estado_civil', 'ocupacao']
categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
    ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
])

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ]
)

# Pipeline fim a fim
model_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', XGBClassifier(n_estimators=150, learning_rate=0.05, random_state=42))
])

# Validação cruzada estratificada para classes desbalanceadas
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(model_pipeline, X, y, cv=cv, scoring='roc_auc')
print(f"ROC-AUC Médio: {scores.mean():.4f} (+/- {scores.std():.4f})")
```

### Interpretabilidade com SHAP Values (SHapley Additive exPlanations)
- **TreeExplainer:** Otimizado em $O(TLD^2)$ para modelos baseados em árvores (XGBoost, LightGBM, Random Forest). Permite extração rápida de importância de features e dependências parciais.
- **KernelExplainer:** Explainer universal agnóstico a modelo baseado em amostragem e regressão local. Essencial para pipelines complexos ou modelos caixa-preta (ex: ensambles heterogêneos e SVMs).

```python
import shap

# Ajuste do preprocessor e modelo antes da explicação
X_train_transformed = preprocessor.fit_transform(X_train)
feature_names = preprocessor.get_feature_names_out()

# TreeExplainer para XGBoost
explainer = shap.TreeExplainer(model_pipeline.named_steps['classifier'])
shap_values = explainer.shap_values(X_train_transformed)

# Resumo global de impacto das features
# shap.summary_plot(shap_values, X_train_transformed, feature_names=feature_names)

# Explicação de predição individual (Force Plot / Waterfall)
# shap.waterfall_plot(shap.Explanation(values=shap_values[0], base_values=explainer.expected_value, data=X_train_transformed[0], feature_names=feature_names))
```
