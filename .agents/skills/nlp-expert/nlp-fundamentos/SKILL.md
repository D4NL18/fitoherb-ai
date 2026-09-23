---
name: nlp-fundamentos
description: Fundamentos de Processamento de Linguagem Natural (NLP) — definição, aplicações práticas, desafios, pipeline clássica e bibliotecas Python essenciais.
pages: 348-353
---

# NLP — Fundamentos

## Objetivo

Compreender os conceitos fundamentais de Processamento de Linguagem Natural (NLP): o que é, onde é aplicado no mundo real, quais são os principais desafios e como é estruturada a pipeline clássica de um projeto NLP, com as bibliotecas Python mais utilizadas na indústria.

---

## Conceitos Fundamentais

### 1. O que é NLP?

NLP (Natural Language Processing) é a área da IA que ensina máquinas a entender, interpretar e gerar linguagem humana. O objetivo é fazer com que computadores processem texto e fala com compreensão semântica real, não apenas correspondência de padrões.

```
Linguagem Humana → [Modelo NLP] → Compreensão/Ação
"Cancele meu pedido" → [Classificador] → intent: CANCEL_ORDER
```

### 2. Aplicações Práticas no Mundo Real

| Aplicação | Exemplos Reais | Técnica NLP |
|---|---|---|
| **Assistentes Virtuais** | Alexa, Siri, Google Assistant | Reconhecimento de intent + NER |
| **Buscadores** | Google, Bing, Elasticsearch | TF-IDF, BM25, embeddings semânticos |
| **Análise de Sentimento** | Monitoramento de redes sociais, reviews | Classificação de texto |
| **Tradução Automática** | Google Translate, DeepL | Seq2Seq com Transformers |
| **Sistemas de Recomendação** | Netflix (descrições), Amazon (reviews) | Similaridade textual |
| **Chatbots** | Suporte ao cliente automatizado | Intenção + extração de entidades |
| **Moderação de Conteúdo** | Redes sociais | Detecção de spam/hate speech |
| **Extração de Informação** | Parsing de contratos, currículos | NER, Relation Extraction |

### 3. Principais Desafios do NLP

```
Texto → Desafios → Solução
```

| Desafio | Exemplo | Por que é difícil |
|---|---|---|
| **Ambiguidade** | "Banco do Brasil" vs. "sentar no banco" | Mesma palavra, contextos distintos |
| **Gírias e Neologismos** | "essa bagulheira é top" | Vocabulário fora dos dados de treino |
| **Sarcasmo e Ironia** | "Que produto maravilhoso… não!" | Sentido oposto ao literal |
| **Múltiplos Idiomas** | Mistura de português/inglês/emoji | Modelos multilinguais necessários |
| **Contexto Longo** | Referências a parágrafos anteriores | Limitação de janela de contexto |
| **Negação** | "Não gostei do produto" | Inverter sentimento sem entender contexto |
| **Abreviações** | "vc n curte isso n é?" | Normalização complexa |

### 4. Pipeline Clássica de Projeto NLP

```
[1. Coleta de Dados]
      ↓
[2. Pré-processamento]
   - Tokenização
   - Remoção de stop words
   - Normalização (lowercase, acentos)
   - Stemming / Lematização
      ↓
[3. Vetorização]
   - Bag of Words
   - TF-IDF
   - Word Embeddings
      ↓
[4. Modelagem]
   - Classificação (Naive Bayes, SVM, BERT)
   - Clustering (K-Means)
   - Sequência (LSTM, Transformer)
      ↓
[5. Avaliação]
   - Accuracy, F1-Score, Precision, Recall
   - Matriz de Confusão
      ↓
[6. Deploy e Monitoramento]
```

### 5. Corpus Textual

Um **corpus** é o conjunto de textos que forma o banco de dados de treinamento de um modelo NLP.

```python
# Exemplo de corpus para análise de sentimento de reviews
corpus = [
    ("O produto chegou rápido e em perfeito estado!", "positivo"),
    ("Qualidade péssima, quebrou na primeira semana.", "negativo"),
    ("Produto mediano, nada de especial.", "neutro"),
    ("Superou minhas expectativas, excelente custo-benefício!", "positivo"),
    ("Não recomendo, atendimento horrível.", "negativo"),
]

textos = [item[0] for item in corpus]
rotulos = [item[1] for item in corpus]
```

### 6. Métricas de Avaliação

```python
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np

y_real = ["positivo", "negativo", "neutro", "positivo", "negativo"]
y_pred = ["positivo", "negativo", "positivo", "positivo", "negativo"]

print(classification_report(y_real, y_pred))
```

| Métrica | Fórmula | Quando usar |
|---|---|---|
| **Accuracy** | acertos / total | Classes balanceadas |
| **Precision** | VP / (VP + FP) | Custo alto de falsos positivos |
| **Recall** | VP / (VP + FN) | Custo alto de falsos negativos |
| **F1-Score** | 2 × (P × R) / (P + R) | Classes desbalanceadas |

---

## Padrões e Boas Práticas

### Instalação do Ambiente NLP

```bash
pip install nltk spacy scikit-learn transformers torch
python -m spacy download pt_core_news_sm
python -m spacy download en_core_web_sm
```

```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('rslp')  # Stemmer para português
```

### Estrutura Básica de Projeto NLP

```python
# Estrutura recomendada
"""
projeto-nlp/
├── data/
│   ├── raw/           # Dados brutos originais
│   └── processed/     # Dados após pré-processamento
├── src/
│   ├── preprocessamento.py
│   ├── vetorizacao.py
│   ├── modelo.py
│   └── avaliacao.py
├── notebooks/
│   └── exploracao.ipynb
├── tests/
└── requirements.txt
"""
```

### Divisão Treino/Teste

```python
from sklearn.model_selection import train_test_split

textos = ["texto 1", "texto 2", "texto 3", "texto 4", "texto 5"]
rotulos = ["pos", "neg", "pos", "neg", "pos"]

X_train, X_test, y_train, y_test = train_test_split(
    textos, rotulos,
    test_size=0.2,         # 20% para teste
    random_state=42,       # Reprodutibilidade
    stratify=rotulos       # Manter proporção de classes
)
```

---

## Exemplos de Uso

### Pipeline Completa Simples

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Dataset de exemplo
textos = [
    "produto ótimo chegou rápido", "péssimo qualidade horrível",
    "bom custo benefício", "não recomendo atendimento ruim",
    "superou expectativas excelente", "defeito na entrega problemático"
]
rotulos = ["pos", "neg", "pos", "neg", "pos", "neg"]

X_train, X_test, y_train, y_test = train_test_split(
    textos, rotulos, test_size=0.33, random_state=42
)

# Pipeline de NLP
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=500)),
    ('clf', MultinomialNB())
])

pipeline.fit(X_train, y_train)
y_pred = pipeline.predict(X_test)
print(classification_report(y_test, y_pred))
```

### Bibliotecas e Seus Casos de Uso

| Biblioteca | Uso Principal | Quando Usar |
|---|---|---|
| **NLTK** | Tokenização, stopwords, stemming | Prototipagem e aprendizado |
| **SpaCy** | NER, POS tagging, lematização | Produção com múltiplos idiomas |
| **scikit-learn** | Vetorização, classificação, pipelines | ML clássico com texto |
| **HuggingFace** | BERT, GPT, modelos pré-treinados | Tarefas complexas, state-of-the-art |
| **Gensim** | Word2Vec, LDA, similaridade | Embeddings e topic modeling |

---

## Checklist de Qualidade

- [ ] Corpus limpo e representativo das classes do problema
- [ ] Divisão treino/teste com `stratify` para classes desbalanceadas
- [ ] Pré-processamento consistente entre treino e produção
- [ ] Baseline simples (Naive Bayes + TF-IDF) antes de modelos complexos
- [ ] F1-Score usado quando as classes são desbalanceadas
- [ ] Matriz de confusão analisada para entender tipos de erro
- [ ] `random_state` fixado para reprodutibilidade
- [ ] Pipeline do scikit-learn usada para evitar data leakage
- [ ] Modelo avaliado em dados reais (não apenas no teste)
- [ ] Documentação do corpus: fonte, data de coleta, critérios de rotulagem
