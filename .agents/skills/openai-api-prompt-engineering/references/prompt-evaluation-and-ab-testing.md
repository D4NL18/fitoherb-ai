# Avaliação Quantitativa, Otimização Iterativa e A/B Testing de Prompts

## 1. Ciclo Iterativo e Teorema *No Free Lunch*
- **Ciclo de Otimização:** `Ideia -> Implementação -> Resultado Experimental -> Análise de Erros -> Ideia`.
- **Teorema *No Free Lunch* (Wolpert & Macready):** Nenhum prompt ou algoritmo é universalmente ótimo em todas as classes de problemas; compare versões de forma controlada sobre benchmarks do seu domínio.
- **Dimensões de um Prompt Efetivo:** Clareza, Persona, Público-alvo, Contexto, Instrução específica, Input delimitado, Formato de saída e Exemplos (zero-shot, one-shot ou few-shot).

---

## 2. Métricas Padrões de Avaliação (Precisão, Recall e F1-Score)

$$\text{Precisão} = \frac{VP}{VP + FP} \qquad \text{Recall} = \frac{VP}{VP + FN} \qquad \text{F1-Score} = 2 \times \frac{\text{Precisão} \times \text{Recall}}{\text{Precisão} + \text{Recall}}$$

**Exemplo Prático (Verificação Factual — Ácido Acético):**
- Fatos esperados (5): fórmula $\text{CH}_3\text{COOH}$, componente do vinagre, líquido incolor, odor pungente, ácido fraco.
- Resposta alucinada: *"Fórmula CH4, gás inflamável usado como combustível."*
- Resultado: $VP = 0$, $FP = 2$, $FN = 5 \implies \text{Precisão} = 0\%$, $\text{Recall} = 0\%$.

---

## 3. Métricas Específicas de Geração de Texto

### 3.1 Perplexidade (Perplexity)
Mede a incerteza de um modelo de linguagem ao prever a próxima palavra ($\text{PPL} = 2^{-\frac{1}{N}\sum_{i=1}^{N}\log_2 P(w_i)}$). Menor perplexidade = menor incerteza / prompt mais claro para o modelo.

```python
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")
model.eval()

def calcular_perplexidade(prompt: str) -> float:
    inputs = tokenizer(prompt, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs, labels=inputs["input_ids"])
    return torch.exp(outputs.loss).item()

p1 = "Descreva a estrutura e usos do ácido acético."  # ~228.68 (mais específico)
p2 = "Fale sobre o ácido acético."                    # ~440.09 (mais genérico)
print(f"Prompt 1: {calcular_perplexidade(p1):.2f} | Prompt 2: {calcular_perplexidade(p2):.2f}")
```

### 3.2 BLEU Score (Bilingual Evaluation Understudy)
Compara n-grams gerados contra referências humanas (0 a 1), penalizando respostas excessivamente curtas:

```python
from nltk.translate.bleu_score import SmoothingFunction, sentence_bleu

referencia = [
    "O ácido acético, com fórmula CH3COOH, é um líquido incolor e corrosivo. "
    "É utilizado na produção de acetato de vinila e como componente principal do vinagre.".split()
]
candidato = (
    "Ácido acético é um líquido incolor com fórmula CH3COOH. "
    "Usado na fabricação de acetato de vinila e encontrado no vinagre.".split()
)

smoothie = SmoothingFunction().method4
print(f"BLEU Score: {sentence_bleu(referencia, candidato, smoothing_function=smoothie):.4f}")
```

### 3.3 ROUGE Score (Sumarização e CoH — Chain of Hindsight)
Avalia sobreposição de unigrams (`ROUGE-1`), bigrams (`ROUGE-2`) e subsequência comum mais longa (`ROUGE-L`). Em otimização iterativa (ex.: *Chain of Hindsight*), evoluir o prompt de genérico para explícito em precisão e acurácia eleva consistentemente todas as métricas ROUGE.

---

## 4. A/B Testing e Feedback em Produção

### Protocolo de A/B Testing de Prompts
1. **Divisão aleatória** entre Prompt A (controle) e Prompt B (candidato).
2. **Métricas comparadas:**
   - **Eficiência:** Latência (ms) e tokens consumidos.
   - **Manutenção de Contexto:** Coerência ao longo de múltiplos turnos.
   - **Precisão:** Exatidão factual e taxa de aderência ao formato/JSON.
3. **Decisão baseada em evidências:** Promover a versão vencedora apenas com significância estatística e sem regressão de custo.

### Análise de Feedback (Qualitativo + Quantitativo)
- **Quantitativo:** Notas de satisfação (1–5), taxa de fallback, taxa de edição manual pelo usuário.
- **Qualitativo:** Comentários livres processados com **Análise de Sentimentos** e modelagem de tópicos via **LDA (Latent Dirichlet Allocation)** para agrupar falhas recorrentes e direcionar a próxima iteração do prompt.
