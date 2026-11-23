---
name: nlp-expert
description: "Use quando a tarefa envolver: Processamento de Linguagem Natural (NLP) — pipeline classico, preprocessamento com SpaCy/NLTK, vetorizacao TF-IDF/N-grams, Word Embeddings (Word2Vec, GloVe, FastText) e similaridade semantica."
---

# Habilidade: Natural Language Processing Expert (NLP) 📚🔍

## Propósito
Autoridade técnica em Processamento de Linguagem Natural clássico e moderno, dominando desde a higienização e normalização de textos brutos até representações vetoriais distribuídas, embeddings densos e modelos de similaridade semântica.

---

## 1. Pré-Processamento Textual Rigoroso
- **Pipeline de Limpeza:** Normalização Unicode, remoção de caracteres de controle, conversão para minúsculas controlada.
- **Tokenização Semântica:** Segmentação de sentenças e palavras preservando entidades compostas.
- **Tratamento Morfofonético:**
  - *Stemming:* Extração de radicais base (algoritmo RSLP para Língua Portuguesa / Porter Stemmer para Inglês).
  - *Lematização:* Redução à forma canônica de dicionário considerando classe gramatical (POS Tagging via **SpaCy** `pt_core_news_lg`).
- **Filtragem de Stopwords:** Remoção seletiva de termos funcionais semânticamente neutros, mantendo termos de negação (*"não"*, *"sem"*) em tarefas de análise de sentimentos.

---

## 2. Vetorização Esparsa (Sparsity)
- **Bag of Words (BoW):** Matriz de contagem de frequência de termos em vocabulário controlado.
- **N-Grams:** Captura de contexto posicional local (unigramas, bigramas, trigramas) para preservar expressões idiomáticas (*"não gostei"*, *"muito bom"*).
- **TF-IDF (Term Frequency-Inverse Document Frequency):** Ponderação estatística da relevância do termo no documento em relação a todo o corpus. Otimização de parâmetros no `scikit-learn`: `min_df`, `max_df`, `sublinear_tf=True`.

---

## 3. Embeddings Densos & Semântica Distribuída
- **Word2Vec (Mikolov et al.):**
  - *CBOW (Continuous Bag of Words):* Prevê a palavra alvo a partir do contexto (alta velocidade, ideal para corpus grandes).
  - *Skip-gram com Negative Sampling:* Prevê o contexto a partir da palavra alvo (superior para palavras raras e vocabulários complexos).
- **GloVe & FastText:**
  - *FastText (Subword n-grams):* Tratamento nativo de palavras fora do vocabulário (OOV - *Out Of Vocabulary*) e morfologia rica em português.
- **Similaridade Semântica:** Cálculo de Distância/Similaridade Cosseno entre vetores densos normalizados:
  $$\text{Cosine Similarity} = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2}$$
