---
name: ga-selecao
description: Operadores de seleção em Algoritmos Genéticos — Torneio (escolher o melhor de K aleatórios), Roleta (probabilidade proporcional ao fitness) e Rank-based. Trade-offs entre pressão seletiva e diversidade genética.
pages: 411-425
---

# Habilidade: Operadores de Seleção em Algoritmos Genéticos 🏆

## Objetivo
Dominar e selecionar o operador de seleção correto para cada tipo de problema em Algoritmos Genéticos, entendendo o trade-off fundamental entre **pressão seletiva** (favorece os mais aptos, converge mais rápido) e **diversidade genética** (mantém exploração do espaço, evita ótimos locais).

---

## Conceitos Fundamentais

### O Papel da Seleção
A seleção é o mecanismo que decide **quais indivíduos têm permissão para reproduzir** e passar seus genes à próxima geração. Um operador de seleção forte (alta pressão seletiva) converge rápido, mas pode prender o algoritmo em um ótimo local. Um operador fraco mantém diversidade, mas pode ser lento.

### Comparação dos Operadores

| Operador | Pressão Seletiva | Diversidade | Custo Computacional | Melhor Para |
|---|---|---|---|---|
| **Torneio (K=2)** | Baixa | Alta | O(K) | Geral, início da busca |
| **Torneio (K=5)** | Média | Média | O(K) | Equilíbrio recomendado |
| **Torneio (K=10+)** | Alta | Baixa | O(K) | Convergência rápida |
| **Roleta** | Proporcional | Média | O(N) | Fitness sempre positivo |
| **Rank-based** | Controlável | Alta | O(N log N) | Fitness com escala muito variada |
| **Estocástico Universal** | Proporcional | Alta | O(N) | Alternativa robusta à Roleta |

---

## Padrões e Boas Práticas

### 1. Seleção por Torneio (Recomendado)
O torneio é o operador mais utilizado na prática por ser simples, eficiente e com pressão seletiva ajustável via `tournament_size`:

```python
import random

def tournament_selection(population, fitnesses, tournament_size=3):
    """
    Seleciona um indivíduo via torneio:
    1. Sorteia 'tournament_size' candidatos aleatoriamente.
    2. Retorna o candidato com maior fitness (o "vencedor do torneio").
    
    Ajuste da pressão seletiva:
    - tournament_size=2: baixa pressão (mais diversidade)
    - tournament_size=3-5: equilíbrio recomendado
    - tournament_size=7+: alta pressão (converge mais rápido, risco de ótimo local)
    """
    candidates = random.sample(range(len(population)), tournament_size)
    winner_idx = max(candidates, key=lambda i: fitnesses[i])
    return population[winner_idx][:]  # Retorna cópia do vencedor

# Uso:
# parent1 = tournament_selection(population, fitnesses, tournament_size=3)
# parent2 = tournament_selection(population, fitnesses, tournament_size=3)
```

### 2. Seleção por Roleta (Roulette Wheel)
Cada indivíduo recebe uma fatia da "roleta" proporcional ao seu fitness. A probabilidade de ser selecionado é diretamente proporcional à aptidão:

```python
import random

def roulette_wheel_selection(population, fitnesses):
    """
    Seleção por roleta: probabilidade proporcional ao fitness.
    
    ATENÇÃO: Requer que todos os fitness sejam positivos.
    Se houver fitness negativo, aplique deslocamento (shift) antes.
    
    Riscos:
    - Super-indivíduo: um indivíduo com fitness muito alto domina a roleta,
      causando convergência prematura.
    """
    # Deslocamento para garantir valores positivos
    min_fit = min(fitnesses)
    shifted = [f - min_fit + 1e-8 for f in fitnesses]  # todos positivos
    total = sum(shifted)
    
    # Geração de número aleatório e seleção proporcional
    r = random.uniform(0, total)
    cumulative = 0.0
    for individual, fit in zip(population, shifted):
        cumulative += fit
        if cumulative >= r:
            return individual[:]
    
    return population[-1][:]  # fallback

# Versão vetorizada com NumPy (mais eficiente para populações grandes)
import numpy as np

def roulette_wheel_selection_np(population, fitnesses):
    fitnesses_arr = np.array(fitnesses)
    shifted = fitnesses_arr - fitnesses_arr.min() + 1e-8
    probabilities = shifted / shifted.sum()
    idx = np.random.choice(len(population), p=probabilities)
    return population[idx][:]
```

### 3. Seleção por Rank
Em vez de usar os valores absolutos do fitness (que podem variar em ordens de magnitude), ordena os indivíduos e atribui probabilidades com base no rank. Isso elimina o problema de super-dominância da Roleta:

```python
import numpy as np

def rank_selection(population, fitnesses, pressure=1.5):
    """
    Seleção por Rank: converte fitness em ranks e seleciona proporcionalmente.
    
    Parâmetro 'pressure' (1.0 a 2.0):
    - 1.0: todos com probabilidade igual (seleção aleatória pura)
    - 2.0: pressão máxima (o melhor tem 2x a probabilidade do pior)
    """
    n = len(population)
    # Rank: 1 (pior) até N (melhor)
    sorted_indices = sorted(range(n), key=lambda i: fitnesses[i])
    ranks = np.zeros(n)
    for rank_val, idx in enumerate(sorted_indices, 1):
        ranks[idx] = rank_val
    
    # Probabilidade linear baseada no rank
    probabilities = (2 - pressure) / n + 2 * ranks * (pressure - 1) / (n * (n - 1))
    probabilities = np.clip(probabilities, 0, None)
    probabilities /= probabilities.sum()
    
    idx = np.random.choice(n, p=probabilities)
    return population[idx][:]
```

### 4. Seleção Estocástica Universal (SUS)
Uma versão mais robusta da Roleta que garante representação uniforme de todos os segmentos:

```python
import numpy as np

def stochastic_universal_sampling(population, fitnesses, n_select):
    """
    Seleciona n_select indivíduos de forma que todas as faixas da roleta
    sejam amostradas uniformemente. Evita o problema de super-dominância.
    """
    fitnesses_arr = np.array(fitnesses)
    shifted = fitnesses_arr - fitnesses_arr.min() + 1e-8
    total = shifted.sum()
    
    step = total / n_select
    start = np.random.uniform(0, step)
    pointers = [start + i * step for i in range(n_select)]
    
    selected = []
    cumulative = 0
    i = 0
    for ptr in pointers:
        while cumulative + shifted[i] < ptr:
            cumulative += shifted[i]
            i += 1
        selected.append(population[i][:])
    
    return selected
```

---

## Trade-offs e Decisão de Qual Usar

```
Problema                          → Operador Recomendado
─────────────────────────────────────────────────────────
Uso geral / primeira tentativa    → Torneio (K=3)
Fitness pode ser negativo         → Torneio (qualquer K)
Fitness muito variado (outliers)  → Rank-based
Exploração máxima no início       → Torneio (K=2)
Convergência rápida necessária    → Torneio (K=5-7)
Fitness sempre positivo e linear  → Roleta ou SUS
Grande diversidade requerida      → SUS
```

### Estratégia Adaptativa de Pressão Seletiva
Aumentar o `tournament_size` progressivamente ao longo das gerações permite explorar amplamente no início e convergir no final:

```python
def adaptive_tournament_size(generation, max_generations, min_k=2, max_k=7):
    """
    Aumenta o tamanho do torneio ao longo das gerações:
    - Início (gen=0):        k = min_k (exploração)
    - Fim (gen=max_gen):     k = max_k (explotação)
    """
    progress = generation / max_generations
    return max(min_k, int(min_k + (max_k - min_k) * progress))
```

---

## Exemplos de Uso

### Comparação de Operadores no Mesmo Problema
```python
import numpy as np
import random

def run_with_selection(selection_fn, generations=100, pop_size=50, n_genes=5):
    """Executa AG com operador de seleção configurável e retorna histórico de fitness."""
    population = [list(np.random.uniform(-5, 5, n_genes)) for _ in range(pop_size)]
    history = []
    
    for gen in range(generations):
        fitnesses = [-sum(x**2 for x in ind) for ind in population]
        history.append(max(fitnesses))
        
        new_pop = []
        while len(new_pop) < pop_size:
            p1 = selection_fn(population, fitnesses)
            p2 = selection_fn(population, fitnesses)
            # Crossover simples de 1 ponto
            pt = random.randint(1, n_genes - 1)
            c1 = p1[:pt] + p2[pt:]
            new_pop.append(c1)
        
        population = new_pop
    
    return history

# Comparação
hist_torneio = run_with_selection(lambda p, f: tournament_selection(p, f, k=3))
hist_roleta  = run_with_selection(roulette_wheel_selection_np)
hist_rank    = run_with_selection(lambda p, f: rank_selection(p, f, pressure=1.5))

print(f"Torneio K=3 — Melhor: {max(hist_torneio):.6f}")
print(f"Roleta     — Melhor: {max(hist_roleta):.6f}")
print(f"Rank 1.5   — Melhor: {max(hist_rank):.6f}")
```

---

## Checklist de Qualidade
- [ ] Operador escolhido com base no tipo de fitness (positivo/negativo) e pressão necessária.
- [ ] Torneio com K=3 como ponto de partida padrão para qualquer problema.
- [ ] Roleta somente usada quando fitness garantidamente positivo (aplicar shift se necessário).
- [ ] Rank-based utilizado quando fitness tem escala muito variada ou outliers extremos.
- [ ] Pressão seletiva monitorada: se convergência prematura, reduzir K ou usar Rank.
- [ ] Para experimentos comparativos, manter operador de seleção como variável isolada.
