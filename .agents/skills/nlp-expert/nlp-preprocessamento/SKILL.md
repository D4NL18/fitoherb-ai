---
name: nlp-preprocessamento
description: Pré-processamento de texto para NLP — tokenização, remoção de stop words, normalização, stemming (RSLP) e lematização com SpaCy para português.
pages: 364-396
---

# NLP — Pré-processamento de Texto

## Objetivo

Dominar todas as etapas de limpeza e normalização de texto antes de vetorização e modelagem: tokenização com NLTK e SpaCy, remoção de stop words, normalização de maiúsculas/acentos, stemming com RSLP (português) e lematização avançada com SpaCy.

---

## Conceitos Fundamentais

### 1. Tokenização

Tokenização divide o texto em unidades menores chamadas **tokens** (palavras, subpalavras, pontuações).

```python
import nltk
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

from nltk.tokenize import word_tokenize, sent_tokenize

texto = "O produto chegou rápido! Funciona perfeitamente, mas o preço é alto."

# Tokenização de palavras (NLTK)
tokens_palavras = word_tokenize(texto, language="portuguese")
print("Tokens NLTK:", tokens_palavras)
# ['O', 'produto', 'chegou', 'rápido', '!', 'Funciona', 'perfeitamente', ',', 'mas', 'o', 'preço', 'é', 'alto', '.']

# Tokenização de sentenças
tokens_sentencas = sent_tokenize(texto, language="portuguese")
print("\nSentenças:", tokens_sentencas)
# ['O produto chegou rápido!', 'Funciona perfeitamente, mas o preço é alto.']
```

```python
# Tokenização com SpaCy (mais robusta)
import spacy

nlp = spacy.load("pt_core_news_sm")
doc = nlp("O produto chegou rápido! Funciona perfeitamente.")

print("Tokens SpaCy:")
for token in doc:
    print(f"  '{token.text}' | POS: {token.pos_} | Pontuação: {token.is_punct}")
```

#### Comparação de Tokenizadores

| Tokenizador | Idioma PT | Pontuação | POS Tags | Velocidade |
|---|---|---|---|---|
| `str.split()` | Sim | Não separa | Não | Muito rápida |
| `nltk.word_tokenize` | Sim | Separa | Não | Rápida |
| `SpaCy` | Sim (modelo pt) | Separa | Sim | Média |
| `HuggingFace Tokenizer` | Depende do modelo | Subpalavras | Não | Rápida |

### 2. Stop Words

Stop words são palavras muito frequentes que geralmente não contribuem para o significado discriminativo do texto.

```python
from nltk.corpus import stopwords
nltk.download('stopwords', quiet=True)

stop_words_pt = set(stopwords.words('portuguese'))
print(f"Total de stop words PT: {len(stop_words_pt)}")
print("Exemplos:", list(stop_words_pt)[:15])
# {'de', 'o', 'que', 'e', 'do', 'da', 'em', 'um', 'para', 'com', 'uma', 'os', 'no', 'se', 'na'}

def remover_stop_words(tokens: list[str], stop_words: set = None) -> list[str]:
    """Remove stop words da lista de tokens."""
    if stop_words is None:
        stop_words = set(stopwords.words('portuguese'))
    return [token for token in tokens if token.lower() not in stop_words]


texto = "O produto é muito bom e chegou rapidamente"
tokens = word_tokenize(texto.lower(), language="portuguese")
tokens_limpos = remover_stop_words(tokens)
print("\nAntes:", tokens)
print("Depois:", tokens_limpos)
```

#### ⚠️ Armadilhas das Stop Words

```python
# PROBLEMA 1: Maiúsculas não removidas
tokens_maiusculas = ["O", "produto", "É", "bom"]
# "O" e "É" NÃO são removidos se a stop word list usa minúsculas!
# Solução: sempre converter para minúsculas ANTES

# PROBLEMA 2: Acentos criam variações
tokens_acentos = ["nao", "não", "Não"]
# "nao" pode não estar na lista se o texto não foi normalizado
# Solução: normalizar acentos antes

# PROBLEMA 3: Pontuação grudada
tokens_pontuacao = ["bom,", "rápido!"]
# "bom," não é removido como stop word "bom"
# Solução: tokenizar corretamente antes de remover stop words

# Stop words customizadas
stop_words_custom = stop_words_pt | {
    "produto", "compra", "entrega",  # Palavras muito comuns no corpus específico
    "é", "foi", "ser"
}
```

### 3. Normalização de Texto

```python
import unicodedata
import re

def normalizar_texto(texto: str) -> str:
    """Pipeline completa de normalização de texto."""
    # 1. Converter para minúsculas
    texto = texto.lower()

    # 2. Remover acentos (opcional - depende do caso de uso)
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')

    # 3. Remover URLs
    texto = re.sub(r'http\S+|www\S+', '', texto)

    # 4. Remover e-mails
    texto = re.sub(r'\S+@\S+', '', texto)

    # 5. Remover números (opcional)
    # texto = re.sub(r'\d+', '', texto)

    # 6. Remover pontuação (exceto apóstrofos)
    texto = re.sub(r"[^\w\s']", ' ', texto)

    # 7. Remover espaços extras
    texto = re.sub(r'\s+', ' ', texto).strip()

    return texto


# Teste
textos_brutos = [
    "O produto É ÓTIMO!!! Chegou RÁPIDO!!! 😊",
    "Visita: www.produto.com.br para mais info",
    "Contato: joao@email.com com dúvidas",
    "Recebi em 3 dias, EXCELENTE entrega!!!"
]

for texto in textos_brutos:
    print(f"Original:    {texto}")
    print(f"Normalizado: {normalizar_texto(texto)}\n")
```

### 4. Stemming com RSLP (Português)

Stemming reduz palavras ao seu radical (stem), cortando sufixos morfológicos.

```python
from nltk.stem import RSLPStemmer
nltk.download('rslp', quiet=True)

stemmer = RSLPStemmer()

palavras = [
    "correndo", "correu", "correr", "corrida",
    "produto", "produtos", "produzindo", "produção",
    "programação", "programar", "programador", "programas"
]

print("Stemming RSLP:")
for palavra in palavras:
    stem = stemmer.stem(palavra)
    print(f"  {palavra:20} → {stem}")

# Saída esperada:
# correndo             → corr
# produtos             → produt
# programação          → program
```

#### ⚠️ Limitação do Stemming

```python
# Stemming pode criar radicais sem sentido
exemplos_problematicos = [
    ("melhor", stemmer.stem("melhor")),       # "melh" — sem sentido
    ("bom", stemmer.stem("bom")),             # "b" — sem sentido
    ("nacional", stemmer.stem("nacional")),   # "nac" — sem sentido
]

for palavra, stem in exemplos_problematicos:
    print(f"  {palavra} → {stem} ⚠️")

# Quando NÃO usar stemming:
# - Quando a forma exata da palavra importa para o negócio
# - Em modelos de linguagem modernos (BERT, GPT) que já entendem morfologia
# - Quando o corpus é muito pequeno (pode perder informação)
```

### 5. Lematização com SpaCy

Lematização retorna a forma canônica (lema) da palavra — palavra real, não radical.

```python
import spacy

nlp = spacy.load("pt_core_news_sm")

def lematizar(texto: str) -> list[str]:
    """Lematiza o texto retornando a forma base das palavras."""
    doc = nlp(texto)
    return [
        token.lemma_
        for token in doc
        if not token.is_punct and not token.is_space
    ]


exemplos = [
    "Estou correndo para chegar a tempo",
    "Os produtos foram vendidos rapidamente",
    "As crianças estavam brincando no parque",
    "Ele programou uma solução inovadora",
]

print("Lematização SpaCy:")
for texto in exemplos:
    lemas = lematizar(texto)
    print(f"  Original: {texto}")
    print(f"  Lemas:    {lemas}\n")
```

#### Stemming vs Lematização

| Aspecto | Stemming (RSLP) | Lematização (SpaCy) |
|---|---|---|
| **Saída** | Radical (pode não ser palavra real) | Forma canônica (palavra real) |
| **Qualidade** | Menor | Maior |
| **Velocidade** | Muito rápido | Médio |
| **Língua** | RSLP apenas português | Depende do modelo carregado |
| **Contexto** | Ignora contexto | Considera contexto gramatical |
| **Exemplo** | "correndo" → "corr" | "correndo" → "correr" |
| **Uso** | Corpus muito grande, velocidade | Qualidade de análise |

---

## Padrões e Boas Práticas

### Pipeline Completa de Pré-processamento

```python
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer
import spacy

nlp_spacy = spacy.load("pt_core_news_sm")
stemmer = RSLPStemmer()
STOP_WORDS_PT = set(stopwords.words('portuguese'))


def preprocessar_texto(
    texto: str,
    usar_lematizacao: bool = True,
    remover_stops: bool = True,
    normalizar: bool = True
) -> list[str]:
    """
    Pipeline completa de pré-processamento.
    Retorna lista de tokens processados.
    """
    if normalizar:
        texto = normalizar_texto(texto)

    if usar_lematizacao:
        doc = nlp_spacy(texto)
        tokens = [
            token.lemma_
            for token in doc
            if not token.is_punct and not token.is_space and len(token.text) > 1
        ]
    else:
        tokens = word_tokenize(texto, language="portuguese")
        tokens = [t for t in tokens if t.isalpha() and len(t) > 1]
        tokens = [stemmer.stem(t) for t in tokens]

    if remover_stops:
        tokens = [t for t in tokens if t not in STOP_WORDS_PT]

    return tokens


def preprocessar_corpus(
    textos: list[str],
    **kwargs
) -> list[list[str]]:
    """Pré-processa um corpus completo."""
    return [preprocessar_texto(texto, **kwargs) for texto in textos]


# Teste completo
exemplos = [
    "Os produtos foram VENDIDOS rapidamente! Qualidade excelente.",
    "Não gostei do produto, estava com defeito e retornei.",
    "Entrega em 2 dias, ótimo custo-benefício para comprar!"
]

corpus_processado = preprocessar_corpus(exemplos, usar_lematizacao=True, remover_stops=True)
for original, processado in zip(exemplos, corpus_processado):
    print(f"Original:   {original}")
    print(f"Processado: {processado}\n")
```

### Integração com Pipeline scikit-learn

```python
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

class PreprocessadorNLP(BaseEstimator, TransformerMixin):
    """Transformador customizado para integrar pré-processamento ao sklearn Pipeline."""

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return [" ".join(preprocessar_texto(texto)) for texto in X]


# Pipeline completa: Pré-processamento + Vetorização + Classificação
pipeline_nlp = Pipeline([
    ("preprocessador", PreprocessadorNLP()),
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=1000)),
    ("classificador", LogisticRegression(max_iter=500))
])

# Treinar
textos_treino = [
    "produto ótimo chegou rápido", "péssimo qualidade quebrou",
    "excelente custo benefício", "não recomendo defeito"
]
rotulos_treino = ["pos", "neg", "pos", "neg"]

pipeline_nlp.fit(textos_treino, rotulos_treino)

# Predizer
novos = ["chegou muito rápido excelente", "veio com defeito horrível"]
print(pipeline_nlp.predict(novos))
```

---

## Exemplos de Uso

### Análise de Sentimento com Pré-processamento Completo

```python
def criar_dataset_processado(reviews: list[dict]) -> tuple:
    """Cria dataset pré-processado para treinamento."""
    textos_raw = [r['texto'] for r in reviews]
    rotulos = [r['sentimento'] for r in reviews]

    textos_processados = [
        " ".join(preprocessar_texto(t, usar_lematizacao=True))
        for t in textos_raw
    ]

    return textos_processados, rotulos


reviews = [
    {"texto": "Produto EXCELENTE! Chegou em 2 dias!", "sentimento": "pos"},
    {"texto": "Horrível, quebrou na primeira semana.", "sentimento": "neg"},
    {"texto": "Qualidade boa, entrega demorou um pouco.", "sentimento": "pos"},
    {"texto": "Não recomendo, atendimento péssimo!", "sentimento": "neg"},
]

X, y = criar_dataset_processado(reviews)
for texto, rotulo in zip(X, y):
    print(f"[{rotulo}] {texto}")
```

---

## Checklist de Qualidade

- [ ] Texto convertido para minúsculas antes de qualquer comparação
- [ ] Tokenização adequada ao idioma (NLTK `language="portuguese"` ou SpaCy `pt_core_news_sm`)
- [ ] Stop words removidas após tokenização (não antes!)
- [ ] Acentos normalizados consistentemente entre treino e produção
- [ ] URLs, e-mails e emojis tratados antes da tokenização
- [ ] Lematização preferida sobre stemming para português (morfologia rica)
- [ ] `PreprocessadorNLP` customizado integrado ao Pipeline sklearn para evitar data leakage
- [ ] Mesmo pipeline de pré-processamento aplicado em treino e inferência
- [ ] Tokens com menos de 2 caracteres removidos (lixo morfológico)
- [ ] Resultado do pré-processamento inspecionado manualmente antes de treinar
- [ ] SpaCy modelo `pt_core_news_sm` instalado: `python -m spacy download pt_core_news_sm`
- [ ] Versões de NLTK e SpaCy fixadas no `requirements.txt`
