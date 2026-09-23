---
name: ga-fundamentos
description: Conceitos fundamentais de Algoritmos Genéticos inspirados na evolução de Darwin — indivíduos, genes, população, fitness e o pipeline completo de geração em geração até o critério de parada.
pages: 397-410
---

# Habilidade: Fundamentos dos Algoritmos Genéticos 🧬

## Objetivo
Compreender e aplicar os conceitos base dos **Algoritmos Genéticos (AG)**: a metaheurística de busca global inspirada na teoria da evolução natural de Darwin, estabelecendo a terminologia, o ciclo completo de execução e os critérios de parada antes de qualquer especialização em operadores ou aplicações.

---

## Conceitos Fundamentais

### Analogia Biológica → Computacional

| Conceito Biológico | Equivalente em AG | Descrição |
|---|---|---|
| Indivíduo / Cromossomo | Solução candidata | Um vetor de valores representando uma solução |
| Gene | Variável de decisão | Um elemento dentro do cromossomo |
| Alelo | Valor de um gene | O valor concreto assumido pelo gene |
| População | Conjunto de soluções | N soluções candidatas simultâneas |
| Fitness (Aptidão) | Função objetivo | Mede quão boa é a solução |
| Seleção Natural | Operador de seleção | Indivíduos mais aptos têm mais chance de reproduzir |
| Reprodução | Crossover | Combina genes de dois pais para gerar filhos |
| Mutação | Perturbação aleatória | Altera um ou mais genes para manter diversidade |
| Geração | Iteração do algoritmo | Uma rodada completa de avaliação → nova população |

### Pipeline Completo do Algoritmo Genético

```
┌─────────────────────────────────────────────────────────────┐
│  1. INICIALIZAÇÃO                                           │
│     Gerar N indivíduos aleatórios (população inicial)       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  2. AVALIAÇÃO                                               │
│     Calcular fitness(indivíduo) para cada um na população   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  3. SELEÇÃO                                                 │
│     Escolher pais com base no fitness                       │
│     (Torneio / Roleta / Rank-based)                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  4. CROSSOVER                                               │
│     Combinar genes de dois pais → gerar filhos              │
│     (1 ponto / 2 pontos / Uniforme)                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  5. MUTAÇÃO                                                 │
│     Alterar genes aleatoriamente com probabilidade p_mut    │
│     (Bit-flip / Gaussiana / Swap)                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  6. SUBSTITUIÇÃO + ELITISMO                                 │
│     Nova geração substitui a anterior                       │
│     Preservar os K melhores (elitismo)                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
              ┌────────────▼────────────┐
              │  7. CRITÉRIO DE PARADA? │
              └──────┬──────────┬───────┘
                     │ Não      │ Sim
                     │          ▼
                     │    Retornar melhor
                     │    indivíduo encontrado
                     └──→ Voltar ao passo 2
```

### Representações de Cromossomos

Escolha a representação conforme o tipo de problema:

| Representação | Tipo de Problema | Exemplo |
|---|---|---|
| **Binária** | Problemas com variáveis 0/1 | Feature selection, otimização combinatorial |
| **Inteira** | Parâmetros discretos | Hyperparameter tuning (n_estimators=100) |
| **Real (Float)** | Espaços contínuos | Otimização de pesos, calibração de sensores |
| **Permutação** | Ordenação de elementos | TSP, scheduling de tarefas |

### Função Fitness
A função fitness é o coração do AG. Ela define o que significa "ser melhor":

```python
# Exemplos de funções fitness

# Maximização de função matemática
def fitness_matematico(individual):
    x = individual  # vetor de floats
    return -sum(xi**2 for xi in x)  # Maximizar → minimizar soma dos quadrados

# Fitness para classificação ML (via cross-validation)
def fitness_ml(params, X, y):
    model = RandomForestClassifier(**decode_params(params))
    score = cross_val_score(model, X, y, cv=5, scoring="f1_macro").mean()
    return score  # Maximizar F1

# Fitness para TSP (minimizar distância total)
def fitness_tsp(route, distance_matrix):
    total = sum(
        distance_matrix[route[i]][route[(i+1) % len(route)]]
        for i in range(len(route))
    )
    return -total  # Negativo para transformar minimização em maximização
```

---

## Padrões e Boas Práticas

### Inicialização da População
```python
import numpy as np
import random

def init_population_real(pop_size, n_genes, low=-5.0, high=5.0):
    """Inicialização aleatória uniforme para espaço contínuo."""
    return [list(np.random.uniform(low, high, n_genes)) for _ in range(pop_size)]

def init_population_binary(pop_size, n_genes):
    """Inicialização aleatória para cromossomo binário."""
    return [[random.randint(0, 1) for _ in range(n_genes)] for _ in range(pop_size)]

def init_population_permutation(pop_size, n_elements):
    """Inicialização aleatória para problema de permutação (TSP)."""
    return [random.sample(range(n_elements), n_elements) for _ in range(pop_size)]
```

### Elitismo — Preservar os Melhores
```python
def apply_elitism(population, fitnesses, elite_size=5):
    """Seleciona os elite_size melhores indivíduos para passar direto à próxima geração."""
    elite_idxs = sorted(range(len(fitnesses)), key=lambda i: fitnesses[i], reverse=True)[:elite_size]
    return [population[i][:] for i in elite_idxs]
```

### Critérios de Parada
```python
def should_stop(generation, n_generations, fitness_history, patience=20, threshold=1e-6):
    """
    Dois critérios combinados:
    1. Número máximo de gerações atingido
    2. Estagnação do fitness por 'patience' gerações consecutivas
    """
    if generation >= n_generations:
        return True, "Máximo de gerações atingido"
    
    if len(fitness_history) >= patience:
        recent = fitness_history[-patience:]
        if max(recent) - min(recent) < threshold:
            return True, f"Fitness estagnado por {patience} gerações"
    
    return False, None
```

### Loop Principal Completo
```python
def genetic_algorithm(
    fitness_func,
    init_func,
    selection_func,
    crossover_func,
    mutation_func,
    pop_size=100,
    n_genes=10,
    n_generations=200,
    elite_size=5,
    p_crossover=0.8,
    p_mutation=0.05
):
    # Inicialização
    population = init_func(pop_size, n_genes)
    best_fitness_history = []
    best_individual = None
    best_fitness = float("-inf")

    for gen in range(n_generations):
        # Avaliação
        fitnesses = [fitness_func(ind) for ind in population]
        
        # Rastrear melhor global
        gen_best_idx = max(range(len(fitnesses)), key=lambda i: fitnesses[i])
        if fitnesses[gen_best_idx] > best_fitness:
            best_fitness = fitnesses[gen_best_idx]
            best_individual = population[gen_best_idx][:]
        best_fitness_history.append(best_fitness)

        # Elitismo
        new_population = apply_elitism(population, fitnesses, elite_size)

        # Gerar filhos até completar a nova geração
        while len(new_population) < pop_size:
            p1 = selection_func(population, fitnesses)
            p2 = selection_func(population, fitnesses)
            c1, c2 = crossover_func(p1, p2, p_crossover)
            new_population.append(mutation_func(c1, p_mutation))
            if len(new_population) < pop_size:
                new_population.append(mutation_func(c2, p_mutation))

        population = new_population

        # Log periódico
        if gen % 50 == 0 or gen == n_generations - 1:
            print(f"Geração {gen:4d} | Melhor Fitness: {best_fitness:.6f}")

        # Critério de parada antecipada
        stop, reason = should_stop(gen, n_generations, best_fitness_history)
        if stop:
            print(f"Parado: {reason}")
            break

    return best_individual, best_fitness, best_fitness_history
```

---

## Exemplos de Uso

### Execução Completa — Otimização de Função Simples
```python
# Usando o loop genérico acima
from ga_selecao import tournament_selection
from ga_crossover_mutacao import crossover_1pt, mutate_gaussian

best_sol, best_fit, history = genetic_algorithm(
    fitness_func=lambda ind: -sum(x**2 for x in ind),
    init_func=init_population_real,
    selection_func=lambda pop, fits: tournament_selection(pop, fits, k=3),
    crossover_func=crossover_1pt,
    mutation_func=lambda ind, pm: mutate_gaussian(ind, pm, sigma=0.3),
    pop_size=100,
    n_genes=10,
    n_generations=300,
    elite_size=5
)
print(f"Melhor solução: {[f'{g:.4f}' for g in best_sol]}")
print(f"Fitness: {best_fit:.6f}")
```

---

## Checklist de Qualidade
- [ ] Representação do cromossomo definida antes de escolher os operadores (binário / inteiro / real / permutação).
- [ ] Função fitness claramente definida, retornando um único valor numérico comparável.
- [ ] Elitismo ativo (pelo menos 1-5% da população) para garantir que o melhor não seja perdido.
- [ ] Critério de parada duplo: máximo de gerações E detecção de estagnação.
- [ ] Log de progresso a cada N gerações para monitorar convergência.
- [ ] Semente aleatória fixada (`random.seed(42)`, `np.random.seed(42)`) para reprodutibilidade.
