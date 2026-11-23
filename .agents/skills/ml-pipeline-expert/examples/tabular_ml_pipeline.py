"""
Exemplo Completo: Pipeline ML End-to-End (Anti Data Leakage)
Cobre: Feature Scaling, PCA opcional, Poda de Árvores (max_depth),
       StratifiedKFold, Comparação de Modelos, Calibração e DBSCAN para Outliers.
"""

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report, f1_score, roc_auc_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier


def build_preprocessor(num_cols: list[str], cat_cols: list[str], use_pca: bool = False) -> ColumnTransformer:
    num_steps = [
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ]
    if use_pca:
        # Preserva 95% da variância sem eliminar colunas arbitrariamente
        num_steps.append(("pca", PCA(n_components=0.95, random_state=42)))

    cat_steps = [
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ]
    return ColumnTransformer(
        transformers=[
            ("num", Pipeline(num_steps), num_cols),
            ("cat", Pipeline(cat_steps), cat_cols),
        ]
    )


def train_and_evaluate(df: pd.DataFrame, target_col: str, num_cols: list[str], cat_cols: list[str]):
    X = df[num_cols + cat_cols]
    y = df[target_col]

    # Split ANTES de qualquer fit (zero data leakage)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    preprocessor = build_preprocessor(num_cols, cat_cols)

    # 1. Baseline com árvore podada (evita overfitting via max_depth / min_samples_leaf)
    dt_pipe = Pipeline([
        ("prep", preprocessor),
        ("clf", DecisionTreeClassifier(max_depth=5, min_samples_leaf=10, random_state=42)),
    ])

    # 2. Random Forest com GridSearchCV estratificado
    rf_pipe = Pipeline([
        ("prep", preprocessor),
        ("clf", RandomForestClassifier(random_state=42, n_jobs=-1)),
    ])
    param_grid = {
        "clf__n_estimators": [100, 200],
        "clf__max_depth": [5, 10, None],
        "clf__min_samples_leaf": [2, 5],
    }
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    search = GridSearchCV(rf_pipe, param_grid, cv=cv, scoring="roc_auc", n_jobs=-1)
    search.fit(X_train, y_train)

    best_model = search.best_estimator_
    probs = best_model.predict_proba(X_test)[:, 1]
    preds = (probs >= 0.5).astype(int)

    print("Melhores hiperparâmetros:", search.best_params_)
    print(f"ROC-AUC (teste): {roc_auc_score(y_test, probs):.4f} | F1: {f1_score(y_test, preds):.4f}")
    print(classification_report(y_test, preds))

    joblib.dump(best_model, "weights/model_pipeline.joblib")
    return best_model


def detect_outliers_dbscan(X_numeric: np.ndarray, eps: float = 0.5, min_samples: int = 5) -> np.ndarray:
    """Identifica outliers (rótulo -1) em dados numéricos padronizados usando DBSCAN."""
    X_scaled = StandardScaler().fit_transform(X_numeric)
    labels = DBSCAN(eps=eps, min_samples=min_samples).fit_predict(X_scaled)
    return labels == -1
