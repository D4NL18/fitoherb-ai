---
name: nlp-embeddings
description: Word Embeddings para NLP — Word2Vec (CBOW e Skip-gram), One-Hot Encoding, similaridade semântica cosseno, tratamento de OOV e alternativas GloVe/FastText.
pages: 379-396
---

# NLP — Word Embeddings

## Objetivo

Dominar a representação densa de palavras como vetores numéricos (embeddings), compreendendo Word2Vec (CBOW e Skip-gram), similaridade semântica via cosseno, tratamento de palavras fora do vocabulário (OOV) e alternativas como GloVe e FastText.

---

## Conceitos Fundamentais

### 1. Por que Embeddings?

Bag of Words e TF-IDF são vetores **esparsos** e **sem semântica**. Embeddings são vetores **densos** que capturam relações semânticas.

```
BoW:          "rei" → [1, 0, 0, ..., 0, 0]   # 50.000 dimensões, quase tudo zero
Embedding:    "rei" → [0.32, -0.15, 0.87, ...]  # 100-300 dimensões, valores densos

# Propriedade mágica dos embeddings:
rei - homem + mulher ≈ rainha
paris - france + italy ≈ rome
```

### 2. One-Hot Encoding — Limitações

```python
vocabulario = ["rei", "rainha", "homem", "mulher", "castelo"]
vocab_idx = {palavra: i for i, palavra in enumerate(vocabulario)}

def one_hot(palavra: str) -> list[int]:
    vetor = [0] * len(vocabulario)
    if palavra in vocab_idx:
        vetor[vocab_idx[palavra]] = 1
    return vetor

print("rei:    ", one_hot("rei"))     # [1, 0, 0, 0, 0]
print("rainha: ", one_hot("rainha"))  # [0, 1, 0, 0, 0]

# Cosine similarity entre "rei" e "rainha" = 0.0 (ortogonais!)
# Não há relação semântica capturada.
```

| Aspecto | One-Hot | Embedding |
|---|---|---|
| Dimensionalidade | = tamanho do vocabulário | 100-300 (fixo) |
| Valores | 0 ou 1 | Decimais |
| Semântica | Nenhuma | Capturada |
| Palavras similares | Vetores ortogonais | Vetores próximos |
| Analogias | Impossível | Possível (rei - homem + mulher = rainha) |

### 3. Word2Vec

Modelo neural que aprende embeddings percorrendo janelas de palavras em frases.

```python
from gensim.models import Word2Vec
import nltk

nltk.download('punkt', quiet=True)

# Corpus de treinamento (sentenças tokenizadas)
corpus_sentencas = [
    ["o", "rei", "governa", "o", "reino"],
    ["a", "rainha", "governa", "o", "castelo"],
    ["o", "homem", "trabalha", "na", "cidade"],
    ["a", "mulher", "trabalha", "na", "empresa"],
    ["o", "príncipe", "herda", "o", "trono"],
    ["a", "princesa", "herda", "o", "castelo"],
    ["python", "é", "uma", "linguagem", "de", "programação"],
    ["java", "é", "uma", "linguagem", "orientada", "a", "objetos"],
]

# Treinar Word2Vec
modelo = Word2Vec(
    sentences=corpus_sentencas,
    vector_size=100,    # Dimensão do vetor (embedding size)
    window=5,           # Janela de contexto (palavras ao redor)
    min_count=1,        # Mínimo de ocorrências para incluir no vocabulário
    workers=4,          # Threads de treinamento
    epochs=100,         # Épocas de treinamento
    sg=0,               # 0=CBOW, 1=Skip-gram
    seed=42
)

# Acessar vetor de uma palavra
vetor_rei = modelo.wv["rei"]
print(f"Vetor 'rei' (100 dims): {vetor_rei[:5]}...")  # Mostrar primeiros 5 valores

# Palavras similares
similares = modelo.wv.most_similar("rei", topn=5)
print("\nPalavras similares a 'rei':")
for palavra, score in similares:
    print(f"  {palavra}: {score:.4f}")
```

#### CBOW vs Skip-gram

| Aspecto | CBOW (sg=0) | Skip-gram (sg=1) |
|---|---|---|
| **Objetivo** | Prediz palavra central dado o contexto | Prediz contexto dado a palavra central |
| **Performance** | Mais rápido, corpus grande | Mais lento, mais preciso |
| **Palavras raras** | Piora (contexto pouco visto) | Melhor (foca em cada palavra) |
| **Corpus** | Ideal para corpus grande | Funciona bem em corpus pequeno |

### 4. Similaridade Semântica com Cosseno

```python
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def similaridade_coseno(palavra1: str, palavra2: str, modelo) -> float:
    """Calcula similaridade semântica entre duas palavras."""
    try:
        v1 = modelo.wv[palavra1].reshape(1, -1)
        v2 = modelo.wv[palavra2].reshape(1, -1)
        return cosine_similarity(v1, v2)[0][0]
    except KeyError as e:
        print(f"Palavra não encontrada no vocabulário: {e}")
        return 0.0


# Analogias: rei - homem + mulher = ?
def analogia(palavra1: str, palavra2: str, palavra3: str, modelo, topn: int = 5):
    """
    Calcula: palavra1 - palavra2 + palavra3 = ?
    Exemplo: rei - homem + mulher = rainha
    """
    resultado = modelo.wv.most_similar(
        positive=[palavra1, palavra3],
        negative=[palavra2],
        topn=topn
    )
    print(f"\n{palavra1} - {palavra2} + {palavra3} = ?")
    for palavra, score in resultado:
        print(f"  → {palavra} ({score:.4f})")


# Exemplos
print(f"Similaridade rei-rainha: {similaridade_coseno('rei', 'rainha', modelo):.4f}")
print(f"Similaridade rei-castelo: {similaridade_coseno('rei', 'castelo', modelo):.4f}")
analogia("rei", "homem", "mulher", modelo)
```

### 5. Tratamento de OOV (Out-Of-Vocabulary)

```python
def obter_vetor_seguro(palavra: str, modelo, fallback: np.ndarray = None) -> np.ndarray:
    """Retorna o vetor da palavra ou um fallback para palavras OOV."""
    try:
        return modelo.wv[palavra]
    except KeyError:
        if fallback is not None:
            return fallback
        # Estratégia: retornar vetor de zeros
        return np.zeros(modelo.vector_size)


def vetor_documento(texto: str, modelo) -> np.ndarray:
    """Representa um documento como a média dos vetores de suas palavras."""
    tokens = texto.lower().split()
    vetores = [obter_vetor_seguro(t, modelo) for t in tokens]
    vetores_validos = [v for v in vetores if v.any()]

    if not vetores_validos:
        return np.zeros(modelo.vector_size)

    return np.mean(vetores_validos, axis=0)


# Comparar documentos por similaridade
doc1 = "o rei governa o reino"
doc2 = "a rainha comanda o castelo"
doc3 = "python é uma linguagem de programação"

v1 = vetor_documento(doc1, modelo).reshape(1, -1)
v2 = vetor_documento(doc2, modelo).reshape(1, -1)
v3 = vetor_documento(doc3, modelo).reshape(1, -1)

print(f"Sim(doc1, doc2) = {cosine_similarity(v1, v2)[0][0]:.4f}")  # Alta (tema similar)
print(f"Sim(doc1, doc3) = {cosine_similarity(v1, v3)[0][0]:.4f}")  # Baixa (temas diferentes)
```

---

## Padrões e Boas Práticas

### Usando Embeddings Pré-treinados

```python
# Usando modelo Word2Vec pré-treinado (português)
# Baixe de: https://nilc.icmc.usp.br/embeddings
import gensim

# Carregar modelo pré-treinado (mais recomendado que treinar do zero)
# modelo_pt = gensim.models.KeyedVectors.load_word2vec_format(
#     "cbow_s100.txt", binary=False
# )

# GloVe — alternativa ao Word2Vec
# pip install gensim
# Baixe de: https://nlp.stanford.edu/projects/glove/

# FastText — lida melhor com morfologia e palavras desconhecidas
from gensim.models import FastText

modelo_ft = FastText(
    sentences=corpus_sentencas,
    vector_size=100,
    window=5,
    min_count=1,
    epochs=50,
    min_n=3,    # Mínimo de caracteres por subpalavra
    max_n=6     # Máximo de caracteres por subpalavra
)

# FastText lida com OOV via subpalavras!
# "programacao" → ["pro", "prog", "rogr", "ogra", ...] → embedding aproximado
vetor_oov = modelo_ft.wv["programacao"]  # Funciona mesmo sem estar no vocabulário!
```

### Comparação: Word2Vec vs GloVe vs FastText

| Aspecto | Word2Vec | GloVe | FastText |
|---|---|---|---|
| **Abordagem** | Predição local | Co-ocorrência global | Subpalavras |
| **OOV** | Não suporta | Não suporta | Suporta (via subpalavras) |
| **Morfologia** | Não captura | Não captura | Captura ("jogar", "jogando") |
| **Velocidade** | Rápido | Médio | Lento (mais parâmetros) |
| **Recomendado** | Corpus grande | Corpus muito grande | Línguas morfológicas (PT, AR) |

### Salvando e Carregando Modelo

```python
# Salvar modelo completo
modelo.save("models/word2vec_pt.model")

# Salvar apenas os vetores (mais leve)
modelo.wv.save("models/word2vec_pt.kv")

# Carregar
from gensim.models import Word2Vec, KeyedVectors
modelo_carregado = Word2Vec.load("models/word2vec_pt.model")
vetores = KeyedVectors.load("models/word2vec_pt.kv")
```

---

## Exemplos de Uso

### Busca Semântica por Similaridade

```python
def buscar_similar(query: str, documentos: list[str], modelo, top_k: int = 3) -> list[tuple]:
    """Retorna os documentos mais similares semanticamente à query."""
    v_query = vetor_documento(query, modelo).reshape(1, -1)

    scores = []
    for i, doc in enumerate(documentos):
        v_doc = vetor_documento(doc, modelo).reshape(1, -1)
        sim = cosine_similarity(v_query, v_doc)[0][0]
        scores.append((i, doc, sim))

    return sorted(scores, key=lambda x: x[2], reverse=True)[:top_k]


docs = [
    "Python é excelente para ciência de dados",
    "O rei e a rainha governam o castelo",
    "Machine learning usa algoritmos estatísticos",
    "A inteligência artificial transforma o mundo",
    "Programação funcional é um paradigma de desenvolvimento"
]

resultados = buscar_similar("linguagem de programação para IA", docs, modelo)
print("\nResultados de busca semântica:")
for idx, doc, score in resultados:
    print(f"  Score: {score:.4f} | {doc}")
```

---

## Checklist de Qualidade

- [ ] Word2Vec treinado com `min_count=2` ou maior para corpus grande
- [ ] `vector_size` entre 100-300 para equilíbrio qualidade/memória
- [ ] `window` entre 5-10 para capturar contexto adequado
- [ ] FastText preferido para português (morfologia rica)
- [ ] Embeddings pré-treinados usados quando corpus próprio é pequeno
- [ ] Função `vetor_documento` usando média dos vetores das palavras
- [ ] Tratamento de OOV implementado (vetor de zeros ou fallback)
- [ ] Similaridade coseno para comparar documentos (não distância euclidiana)
- [ ] Modelo salvo em arquivo após treinamento (não re-treinar sempre)
- [ ] Tamanho do vocabulário verificado com `len(modelo.wv.key_to_index)`
- [ ] Analogias testadas para validar qualidade do embedding treinado
