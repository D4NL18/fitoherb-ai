"""
Treinamento e avaliação de Word Embeddings em Português (PT-BR) com Gensim.

Cobre:
- Treinamento Word2Vec em modo CBOW (sg=0) e Skip-gram (sg=1)
- Similaridade semântica via cosseno entre palavras e documentos
- Analogias vetoriais (ex.: rei - homem + mulher ≈ rainha)
- Tratamento de OOV (Out-of-Vocabulary) com fallback seguro e FastText (subpalavras)

Dependências:
    pip install gensim numpy scikit-learn
"""

from __future__ import annotations

import numpy as np
from gensim.models import FastText, Word2Vec
from sklearn.metrics.pairwise import cosine_similarity

CORPUS_PTBR: list[list[str]] = [
    ["o", "rei", "governa", "o", "reino", "no", "castelo"],
    ["a", "rainha", "governa", "o", "reino", "no", "castelo"],
    ["o", "homem", "trabalha", "na", "cidade", "todos", "os", "dias"],
    ["a", "mulher", "trabalha", "na", "cidade", "todos", "os", "dias"],
    ["o", "principe", "herda", "o", "trono", "do", "rei"],
    ["a", "princesa", "herda", "o", "trono", "da", "rainha"],
    ["python", "e", "uma", "linguagem", "de", "programacao", "para", "dados"],
    ["java", "e", "uma", "linguagem", "de", "programacao", "orientada", "a", "objetos"],
    ["machine", "learning", "usa", "python", "e", "algoritmos", "estatisticos"],
    ["inteligencia", "artificial", "transforma", "sistemas", "com", "dados"],
]


def treinar_word2vec(
    sentencas: list[list[str]],
    sg: int = 0,
    vector_size: int = 64,
    window: int = 4,
    epochs: int = 120,
) -> Word2Vec:
    """Treina modelo Word2Vec (sg=0 para CBOW, sg=1 para Skip-gram)."""
    return Word2Vec(
        sentences=sentencas,
        vector_size=vector_size,
        window=window,
        min_count=1,
        workers=2,
        epochs=epochs,
        sg=sg,
        seed=42,
    )


def similaridade_palavras(p1: str, p2: str, modelo: Word2Vec) -> float:
    """Calcula similaridade cosseno entre duas palavras presentes no vocabulário."""
    if p1 not in modelo.wv or p2 not in modelo.wv:
        return 0.0
    v1 = modelo.wv[p1].reshape(1, -1)
    v2 = modelo.wv[p2].reshape(1, -1)
    return float(cosine_similarity(v1, v2)[0][0])


def vetor_documento_seguro(texto: str, modelo: Word2Vec) -> np.ndarray:
    """Gera vetor médio de um documento ignorando tokens OOV sem lançar KeyError."""
    tokens = texto.lower().split()
    vetores = [modelo.wv[t] for t in tokens if t in modelo.wv]
    if not vetores:
        return np.zeros(modelo.vector_size, dtype=np.float32)
    return np.mean(vetores, axis=0)


def executar_analogia(
    modelo: Word2Vec,
    positivo: list[str],
    negativo: list[str],
    topn: int = 3,
) -> list[tuple[str, float]]:
    """Executa analogia vetorial (ex.: positive=['rei', 'mulher'], negative=['homem'])."""
    return modelo.wv.most_similar(positive=positivo, negative=negativo, topn=topn)


def treinar_fasttext_oov(sentencas: list[list[str]], vector_size: int = 64) -> FastText:
    """Treina FastText com n-gramas de caracteres para suportar palavras OOV."""
    return FastText(
        sentences=sentencas,
        vector_size=vector_size,
        window=4,
        min_count=1,
        epochs=100,
        min_n=3,
        max_n=6,
        seed=42,
    )


if __name__ == "__main__":
    modelo_cbow = treinar_word2vec(CORPUS_PTBR, sg=0)
    modelo_sg = treinar_word2vec(CORPUS_PTBR, sg=1)

    print("=== Word2Vec CBOW vs Skip-gram ===")
    for nome, mod in (("CBOW", modelo_cbow), ("Skip-gram", modelo_sg)):
        sim_rr = similaridade_palavras("rei", "rainha", mod)
        sim_rp = similaridade_palavras("rei", "python", mod)
        print(f"[{nome}] sim(rei, rainha) = {sim_rr:.4f} | sim(rei, python) = {sim_rp:.4f}")

    print("\n=== Analogia: rei - homem + mulher ===")
    for palavra, score in executar_analogia(modelo_sg, ["rei", "mulher"], ["homem"]):
        print(f"  -> {palavra}: {score:.4f}")

    print("\n=== Similaridade entre Documentos (com fallback OOV) ===")
    d1 = vetor_documento_seguro("o rei governa o castelo", modelo_sg).reshape(1, -1)
    d2 = vetor_documento_seguro("a rainha governa o reino", modelo_sg).reshape(1, -1)
    d3 = vetor_documento_seguro("python para machine learning", modelo_sg).reshape(1, -1)
    print(f"Sim(realeza_1, realeza_2) = {cosine_similarity(d1, d2)[0][0]:.4f}")
    print(f"Sim(realeza_1, tech)      = {cosine_similarity(d1, d3)[0][0]:.4f}")

    print("\n=== Tratamento de OOV com FastText ===")
    modelo_ft = treinar_fasttext_oov(CORPUS_PTBR)
    palavra_oov = "programador"  # Não está no corpus original
    print(f"'{palavra_oov}' está no Word2Vec? {palavra_oov in modelo_sg.wv}")
    similares_ft = modelo_ft.wv.most_similar(palavra_oov, topn=3)
    print(f"FastText mais similares a '{palavra_oov}':")
    for palavra, score in similares_ft:
        print(f"  -> {palavra}: {score:.4f}")
