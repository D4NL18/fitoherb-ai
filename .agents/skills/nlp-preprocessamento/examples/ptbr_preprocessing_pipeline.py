"""
Pipeline completo de pré-processamento de texto em Português (PT-BR).

Cobre:
- Normalização (minúsculas, URLs, e-mails, pontuação e remoção opcional de acentos)
- Tokenização (NLTK e SpaCy)
- Remoção de stop words (PT-BR + lista customizada)
- Stemming com RSLP (NLTK)
- Lematização com SpaCy (`pt_core_news_sm`)
- Integração com scikit-learn Pipeline (evitando data leakage)

Dependências:
    pip install nltk spacy scikit-learn
    python -m spacy download pt_core_news_sm
"""

from __future__ import annotations

import re
import unicodedata
from typing import Iterable

import nltk
import spacy
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer
from nltk.tokenize import word_tokenize
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


def garantir_recursos_nltk() -> None:
    """Baixa recursos mínimos do NLTK sob demanda (idempotente)."""
    for recurso in ("punkt", "punkt_tab", "stopwords", "rslp"):
        nltk.download(recurso, quiet=True)


def normalizar_texto(texto: str, remover_acentos: bool = False) -> str:
    """Normaliza texto bruto removendo ruídos comuns antes da tokenização."""
    texto = texto.lower()
    texto = re.sub(r"http\S+|www\S+", " ", texto)
    texto = re.sub(r"\S+@\S+", " ", texto)
    if remover_acentos:
        texto = unicodedata.normalize("NFD", texto)
        texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    texto = re.sub(r"[^\w\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


class PipelinePreprocessamentoPTBR:
    """Pipeline configurável de pré-processamento para textos em PT-BR."""

    def __init__(
        self,
        modo: str = "lematizacao",
        remover_stops: bool = True,
        remover_acentos: bool = False,
        stop_words_extras: Iterable[str] | None = None,
        min_len: int = 2,
    ) -> None:
        if modo not in {"lematizacao", "stemming"}:
            raise ValueError("`modo` deve ser 'lematizacao' ou 'stemming'.")

        garantir_recursos_nltk()
        self.modo = modo
        self.remover_stops = remover_stops
        self.remover_acentos = remover_acentos
        self.min_len = min_len

        self.stop_words = set(stopwords.words("portuguese"))
        if stop_words_extras:
            self.stop_words |= {w.lower() for w in stop_words_extras}

        self._stemmer = RSLPStemmer() if modo == "stemming" else None
        self._nlp = spacy.load("pt_core_news_sm") if modo == "lematizacao" else None

    def processar(self, texto: str) -> list[str]:
        """Aplica normalização, tokenização, stemming/lematização e remoção de stop words."""
        texto_limpo = normalizar_texto(texto, remover_acentos=self.remover_acentos)

        if self.modo == "lematizacao":
            assert self._nlp is not None
            doc = self._nlp(texto_limpo)
            tokens = [
                token.lemma_.lower()
                for token in doc
                if not token.is_punct and not token.is_space and token.is_alpha
            ]
        else:
            assert self._stemmer is not None
            brutos = word_tokenize(texto_limpo, language="portuguese")
            tokens = [self._stemmer.stem(t) for t in brutos if t.isalpha()]

        if self.remover_stops:
            tokens = [t for t in tokens if t not in self.stop_words]

        return [t for t in tokens if len(t) >= self.min_len]


class PreprocessadorSklearnPTBR(BaseEstimator, TransformerMixin):
    """Transformador scikit-learn compatível com Pipeline e GridSearchCV."""

    def __init__(
        self,
        modo: str = "lematizacao",
        remover_stops: bool = True,
        remover_acentos: bool = False,
    ) -> None:
        self.modo = modo
        self.remover_stops = remover_stops
        self.remover_acentos = remover_acentos
        self._pipeline: PipelinePreprocessamentoPTBR | None = None

    def fit(self, X: Iterable[str], y=None) -> "PreprocessadorSklearnPTBR":
        self._pipeline = PipelinePreprocessamentoPTBR(
            modo=self.modo,
            remover_stops=self.remover_stops,
            remover_acentos=self.remover_acentos,
        )
        return self

    def transform(self, X: Iterable[str]) -> list[str]:
        if self._pipeline is None:
            raise RuntimeError("Chame `fit` antes de `transform`.")
        return [" ".join(self._pipeline.processar(texto)) for texto in X]


if __name__ == "__main__":
    exemplos = [
        "O produto É ÓTIMO!!! Chegou RÁPIDO em 2 dias. Visite https://loja.exemplo.com",
        "Os produtos foram vendidos rapidamente, mas o atendimento foi péssimo!",
        "Contato: suporte@exemplo.com — não recomendo, veio com defeito.",
        "Excelente custo-benefício, compraria novamente sem pensar duas vezes!",
    ]
    rotulos = ["pos", "neg", "neg", "pos"]

    print("=== Comparação: Stemming (RSLP) vs Lematização (SpaCy) ===")
    pipe_stem = PipelinePreprocessamentoPTBR(modo="stemming")
    pipe_lemma = PipelinePreprocessamentoPTBR(modo="lematizacao")

    for texto in exemplos:
        print(f"\nOriginal:    {texto}")
        print(f"Stemming:    {pipe_stem.processar(texto)}")
        print(f"Lematização: {pipe_lemma.processar(texto)}")

    print("\n=== Pipeline scikit-learn (Pré-processamento + TF-IDF + Regressão Logística) ===")
    clf = Pipeline(
        [
            ("prep", PreprocessadorSklearnPTBR(modo="lematizacao")),
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
            ("model", LogisticRegression(max_iter=500)),
        ]
    )
    clf.fit(exemplos, rotulos)
    novos_textos = [
        "Chegou super rápido e a qualidade é excelente!",
        "Produto horrível com defeito no primeiro dia.",
    ]
    print("Predições:", list(zip(novos_textos, clf.predict(novos_textos))))
