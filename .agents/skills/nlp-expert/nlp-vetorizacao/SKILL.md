---
name: nlp-vetorizacao
description: Vetorização de texto para NLP — Bag of Words, TF-IDF, N-grams, Word Cloud e seleção de features com scikit-learn.
pages: 354-378
---

# NLP — Vetorização de Texto

## Objetivo

Dominar as técnicas de representação numérica de textos para modelos de Machine Learning: Bag of Words, TF-IDF, N-grams e visualização com Word Cloud. Entender as limitações de cada abordagem e quando escolher cada uma.

---

## Conceitos Fundamentais

### 1. Por que Vetorizar?

Modelos de ML trabalham com números, não com texto. A vetorização converte strings em matrizes numéricas que os algoritmos conseguem processar.

```
"O produto é ótimo"  →  [0, 0, 1, 0, 1, 1, 0, 1]  (vetor esparso)
"Produto horrível"   →  [0, 1, 0, 0, 0, 0, 1, 0]
```

### 2. Bag of Words (BoW)

Conta a frequência de cada palavra no texto, ignorando ordem e gramática.

```python
from sklearn.feature_extraction.text import CountVectorizer

corpus = [
    "o produto é ótimo e barato",
    "o produto é péssimo e caro",
    "produto excelente qualidade ótima",
    "não recomendo este produto caro"
]

# Configuração básica
vectorizer = CountVectorizer(
    max_features=100,       # Manter apenas as 100 palavras mais frequentes
    min_df=1,               # Palavra deve aparecer em no mínimo 1 documento
    max_df=0.95,            # Ignorar palavras em mais de 95% dos documentos
    binary=False            # Contar frequência (True = apenas 0 ou 1)
)

X = vectorizer.fit_transform(corpus)

print("Vocabulário:", vectorizer.get_feature_names_out())
print("Shape da matriz:", X.shape)
print("Matriz densa:\n", X.toarray())
```

**Saída:**
```
Vocabulário: ['barato' 'caro' 'este' 'excelente' 'não' 'ótima' 'ótimo' 'péssimo' ...]
Shape da matriz: (4, 12)
```

#### Limitações do BoW

| Limitação | Descrição | Solução |
|---|---|---|
| Ignora ordem | "bom produto" = "produto bom" | N-grams |
| Ignora semântica | "ótimo" e "excelente" são independentes | Word Embeddings |
| Alta dimensionalidade | 1 coluna por palavra única | max_features, min_df |
| Palavras comuns dominam | "de", "o", "a" têm alta frequência | Stop words + TF-IDF |

### 3. Word Cloud — Visualização

```python
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter

def gerar_wordcloud(textos: list[str], titulo: str = "Word Cloud"):
    """Gera visualização das palavras mais frequentes."""
    texto_unificado = " ".join(textos)

    wc = WordCloud(
        width=800,
        height=400,
        background_color="white",
        max_words=100,
        colormap="viridis",
        stopwords={"o", "a", "de", "do", "da", "e", "é", "em", "um", "uma"}
    ).generate(texto_unificado)

    plt.figure(figsize=(12, 6))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.title(titulo, fontsize=18)
    plt.tight_layout()
    plt.savefig(f"wordcloud_{titulo.lower().replace(' ', '_')}.png", dpi=150)
    plt.show()


# Palavras mais frequentes sem Word Cloud
def top_palavras(textos: list[str], n: int = 20) -> list[tuple]:
    """Retorna as N palavras mais frequentes."""
    todas_palavras = " ".join(textos).lower().split()
    return Counter(todas_palavras).most_common(n)
```

### 4. TF-IDF (Term Frequency — Inverse Document Frequency)

Pondera a importância de cada palavra levando em conta sua raridade no corpus.

**Fórmulas:**

$$TF(t, d) = \frac{\text{frequência de } t \text{ em } d}{\text{total de termos em } d}$$

$$IDF(t) = \log\left(\frac{N + 1}{df(t) + 1}\right) + 1$$

$$TF\text{-}IDF(t, d) = TF(t, d) \times IDF(t)$$

> Palavras comuns em todos os documentos (ex: "de", "o") têm IDF baixo → peso baixo.
> Palavras raras e discriminativas têm IDF alto → peso alto.

```python
from sklearn.feature_extraction.text import TfidfVectorizer

corpus = [
    "o produto é ótimo e funciona bem",
    "o produto chegou rápido excelente qualidade",
    "produto péssimo não funciona como esperado",
    "não recomendo produto com defeito sério",
]

vectorizer_tfidf = TfidfVectorizer(
    max_features=500,
    min_df=1,
    max_df=0.9,
    sublinear_tf=True,      # Aplica log no TF para suavizar frequências altas
    norm="l2"               # Normalização L2 dos vetores
)

X_tfidf = vectorizer_tfidf.fit_transform(corpus)

# Ver peso de cada palavra
import pandas as pd

feature_names = vectorizer_tfidf.get_feature_names_out()
df_pesos = pd.DataFrame(
    X_tfidf.toarray(),
    columns=feature_names
)
print(df_pesos.T.sort_values(0, ascending=False).head(10))
```

#### BoW vs TF-IDF — Comparação

| Aspecto | Bag of Words | TF-IDF |
|---|---|---|
| **Método** | Conta frequência bruta | Frequência ponderada por raridade |
| **Palavras comuns** | Recebem peso alto | Recebem peso baixo (IDF penaliza) |
| **Palavras raras** | Baixo peso por frequência | Alto peso por ser discriminativa |
| **Performance** | Baseline razoável | Geralmente melhor para classificação |
| **Custo computacional** | Baixo | Ligeiramente maior |
| **Uso recomendado** | Exploração inicial | Modelos de produção NLP clássico |

### 5. N-grams — Capturando Contexto

N-grams consideram sequências de N palavras consecutivas, capturando frases e contexto.

```python
# Unigrams (N=1): "muito", "bom", "produto"
# Bigrams (N=2): "muito bom", "bom produto"
# Trigrams (N=3): "produto muito bom"

vectorizer_ngram = TfidfVectorizer(
    ngram_range=(1, 2),     # Unigrams + Bigrams
    max_features=1000,
    min_df=2
)

corpus_ex = [
    "produto muito bom qualidade excelente",
    "não gostei do produto qualidade ruim",
    "muito bom atendimento rápido entrega",
    "entrega muito atrasada não recomendo"
]

X_ngram = vectorizer_ngram.fit_transform(corpus_ex)
features = vectorizer_ngram.get_feature_names_out()

# Ver bigrams capturados
bigrams = [f for f in features if " " in f]
print(f"Bigrams capturados: {bigrams}")
```

| N-gram | Exemplo | Vantagem |
|---|---|---|
| **Unigram** (N=1) | "não", "bom" | Baseline, baixa dimensionalidade |
| **Bigram** (N=2) | "não bom", "muito bom" | Captura negações e modificadores |
| **Trigram** (N=3) | "produto muito bom" | Contexto mais rico |
| **N=(1,2)** | Unigrams + Bigrams | Melhor equilíbrio na prática |

---

## Padrões e Boas Práticas

### Pipeline Completa de Classificação

```python
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import classification_report
import numpy as np

textos = [
    "produto ótimo chegou rápido perfeito",
    "péssima qualidade quebrou semana",
    "excelente custo benefício recomendo",
    "horrível não funciona devolvi",
    "muito bom satisfeito compra",
    "lixo produto ruim arrependido"
]
rotulos = ["pos", "neg", "pos", "neg", "pos", "neg"]

X_train, X_test, y_train, y_test = train_test_split(
    textos, rotulos, test_size=0.33, random_state=42, stratify=rotulos
)

# Comparar diferentes vetorizações
configs = {
    "BoW": CountVectorizer(max_features=500),
    "TF-IDF": TfidfVectorizer(max_features=500, sublinear_tf=True),
    "TF-IDF + Bigrams": TfidfVectorizer(ngram_range=(1,2), max_features=1000),
}

for nome, vectorizer in configs.items():
    pipeline = Pipeline([
        ("vec", vectorizer),
        ("clf", LogisticRegression(max_iter=1000))
    ])
    scores = cross_val_score(
        pipeline, textos, rotulos,
        cv=min(3, len(textos)//2), scoring="f1_macro"
    )
    print(f"{nome}: F1 = {scores.mean():.3f} ± {scores.std():.3f}")
```

### Salvando e Carregando o Vectorizer

```python
import joblib

# Salvar (após fit_transform)
joblib.dump(vectorizer_tfidf, "models/tfidf_vectorizer.joblib")

# Carregar em produção
vectorizer_prod = joblib.load("models/tfidf_vectorizer.joblib")

# IMPORTANTE: usar apenas transform() em produção, nunca fit_transform()
X_novo = vectorizer_prod.transform(["novo texto para classificar"])
```

---

## Exemplos de Uso

### Análise de Reviews de E-commerce

```python
def analisar_reviews(reviews: list[dict]) -> dict:
    """Analisa reviews e identifica palavras mais discriminativas por sentimento."""
    textos_pos = [r['texto'] for r in reviews if r['sentimento'] == 'positivo']
    textos_neg = [r['texto'] for r in reviews if r['sentimento'] == 'negativo']

    vec = TfidfVectorizer(ngram_range=(1, 2), max_features=200)
    vec.fit([r['texto'] for r in reviews])

    def top_features(textos_grupo):
        if not textos_grupo:
            return []
        X = vec.transform(textos_grupo)
        scores = X.mean(axis=0).A1
        features = vec.get_feature_names_out()
        top_idx = scores.argsort()[-10:][::-1]
        return [(features[i], scores[i]) for i in top_idx]

    return {
        "palavras_positivas": top_features(textos_pos),
        "palavras_negativas": top_features(textos_neg)
    }
```

---

## Checklist de Qualidade

- [ ] `CountVectorizer`/`TfidfVectorizer` dentro de `Pipeline` para evitar data leakage
- [ ] `max_features` definido para limitar dimensionalidade
- [ ] `min_df` ≥ 2 para ignorar palavras que aparecem em apenas 1 documento
- [ ] `max_df` ≤ 0.95 para ignorar palavras em quase todos os documentos
- [ ] N-grams testados com `ngram_range=(1,2)` como default
- [ ] TF-IDF preferido sobre BoW puro para classificação
- [ ] `sublinear_tf=True` para suavizar frequências altas
- [ ] Vectorizer salvo com `joblib` após treinamento
- [ ] Em produção, usar apenas `.transform()` (nunca `.fit_transform()`)
- [ ] Word Cloud gerada durante análise exploratória do corpus
- [ ] Comparação explícita entre BoW, TF-IDF e N-grams via cross-validation
