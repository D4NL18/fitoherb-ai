---
name: ga-crossover-mutacao
description: Operadores genéticos de cruzamento (crossover de 1 ponto, 2 pontos, uniforme, PMX para permutação) e mutação (bit-flip para binário, Gaussiana para contínuo, swap para permutação), com taxas ideais e implementação de elitismo.
pages: 426-445
---

# Habilidade: Crossover, Mutação e Elitismo em Algoritmos Genéticos ✂️🔀

## Objetivo
Implementar e selecionar os operadores genéticos corretos de **crossover** (recombinação) e **mutação** para cada tipo de representação de cromossomo, calibrando as taxas ideais (`p_crossover` ∈ [0.7, 0.9], `p_mutation` ∈ [0.01, 0.1]) e combinando com **elitismo** para garantir que o melhor indivíduo nunca seja perdido entre gerações.

---

## Conceitos Fundamentais

### O Papel do Crossover (Recombinação)
O crossover é o operador primário de **exploração**: combina material genético de dois pais para criar filhos potencialmente melhores. Uma taxa alta de crossover (`p_crossover = 0.8-0.9`) é preferível pois é o principal mecanismo de evolução dirigida.

### O Papel da Mutação
A mutação é o operador primário de **diversidade**: pertuba aleatoriamente um ou mais genes, evitando que toda a população convirja para o mesmo ponto. Uma taxa muito alta de mutação transforma o AG em busca aleatória pura.

### Taxas Ideais por Operador

| Operador | Taxa Recomendada | Efeito se Muito Alto | Efeito se Muito Baixo |
|---|---|---|---|
| Crossover | 0.7 – 0.9 | Instabilidade | Pouca recombinação |
| Mutação (binário) | 0.01 – 0.05 | Busca aleatória | Convergência prematura |
| Mutação (contínuo) | 0.05 – 0.15 | Destruição de boas soluções | Estagnação |

---

## Padrões e Boas Práticas

### Crossover de 1 Ponto
```python
import random

def crossover_1pt(parent1, parent2, p_cross=0.8):
    """
    Seleciona um ponto de corte aleatório e troca os segmentos.
    Simples e eficaz para representações binárias e inteiras.
    """
    if random.random() < p_cross:
        point = random.randint(1, len(parent1) - 1)
        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]
        return child1, child2
    return parent1[:], parent2[:]  # Sem crossover: cópia direta
```

### Crossover de 2 Pontos
```python
def crossover_2pt(parent1, parent2, p_cross=0.8):
    """
    Dois pontos de corte: o segmento central é trocado entre os pais.
    Melhor que 1 ponto pois evita viés posicional dos genes.
    """
    if random.random() < p_cross:
        pts = sorted(random.sample(range(1, len(parent1)), 2))
        child1 = parent1[:pts[0]] + parent2[pts[0]:pts[1]] + parent1[pts[1]:]
        child2 = parent2[:pts[0]] + parent1[pts[0]:pts[1]] + parent2[pts[1]:]
        return child1, child2
    return parent1[:], parent2[:]
```

### Crossover Uniforme
```python
def crossover_uniform(parent1, parent2, p_cross=0.8, p_gene=0.5):
    """
    Para cada gene, escolhe aleatoriamente de qual pai herdar.
    Maior diversidade — melhor para cromossomos com genes independentes.
    """
    if random.random() < p_cross:
        child1 = [g1 if random.random() < p_gene else g2 for g1, g2 in zip(parent1, parent2)]
        child2 = [g2 if random.random() < p_gene else g1 for g1, g2 in zip(parent1, parent2)]
        return child1, child2
    return parent1[:], parent2[:]
```

### Crossover PMX — Partially Mapped (para Permutação — TSP)
```python
def crossover_pmx(parent1, parent2, p_cross=0.8):
    """
    Partially Mapped Crossover: preserva a validade da permutação.
    OBRIGATÓRIO para problemas como TSP onde o cromossomo é uma permutação.
    """
    if random.random() >= p_cross:
        return parent1[:], parent2[:]
    
    size = len(parent1)
    pt1, pt2 = sorted(random.sample(range(size), 2))
    
    child1 = [-1] * size
    child1[pt1:pt2] = parent1[pt1:pt2]
    
    # Mapeamento: preencher posições restantes mantendo permutação válida
    for i in range(pt1, pt2):
        gene = parent2[i]
        if gene not in child1:
            pos = i
            while pt1 <= pos < pt2:
                pos = parent2.index(parent1[pos])
            child1[pos] = gene
    
    # Preencher restante com parent2
    for i in range(size):
        if child1[i] == -1:
            child1[i] = parent2[i]
    
    # Filho 2 (simétrico)
    child2 = [-1] * size
    child2[pt1:pt2] = parent2[pt1:pt2]
    for i in range(pt1, pt2):
        gene = parent1[i]
        if gene not in child2:
            pos = i
            while pt1 <= pos < pt2:
                pos = parent1.index(parent2[pos])
            child2[pos] = gene
    for i in range(size):
        if child2[i] == -1:
            child2[i] = parent1[i]
    
    return child1, child2
```

---

### Mutação Bit-Flip (Representação Binária)
```python
def mutate_bitflip(individual, p_mut=0.05):
    """
    Para cada gene binário (0 ou 1), inverte com probabilidade p_mut.
    Regra: p_mut = 1/n_genes é um ponto de partida clássico.
    """
    return [1 - gene if random.random() < p_mut else gene for gene in individual]
```

### Mutação Gaussiana (Representação Contínua/Real)
```python
import numpy as np

def mutate_gaussian(individual, p_mut=0.1, sigma=0.3, low=-5.0, high=5.0):
    """
    Perturba cada gene com ruído Gaussiano N(0, sigma) com probabilidade p_mut.
    Clip garante que o gene permaneça nos limites válidos.
    
    sigma pequeno: perturbação local (explotação)
    sigma grande: perturbação ampla (exploração)
    """
    return [
        float(np.clip(gene + np.random.normal(0, sigma), low, high))
        if random.random() < p_mut else gene
        for gene in individual
    ]

# Versão com sigma adaptativo (diminui com o progresso)
def mutate_gaussian_adaptive(individual, generation, max_gen, 
                              p_mut=0.1, sigma_init=1.0, sigma_final=0.05,
                              low=-5.0, high=5.0):
    """Reduz sigma ao longo das gerações: exploração inicial → explotação final."""
    progress = generation / max_gen
    sigma = sigma_init * (1 - progress) + sigma_final * progress
    return mutate_gaussian(individual, p_mut, sigma, low, high)
```

### Mutação Swap (Representação de Permutação)
```python
def mutate_swap(individual, p_mut=0.1):
    """
    Troca dois genes aleatórios de posição.
    Mantém a validade da permutação — essencial para TSP e scheduling.
    """
    individual = individual[:]
    if random.random() < p_mut:
        i, j = random.sample(range(len(individual)), 2)
        individual[i], individual[j] = individual[j], individual[i]
    return individual

# Mutação Inversão (Inversion Mutation) — mais exploratória para TSP
def mutate_inversion(individual, p_mut=0.1):
    """Inverte o segmento entre dois pontos aleatórios."""
    individual = individual[:]
    if random.random() < p_mut:
        i, j = sorted(random.sample(range(len(individual)), 2))
        individual[i:j+1] = individual[i:j+1][::-1]
    return individual
```

---

## Elitismo

O elitismo garante que os melhores indivíduos **nunca sejam perdidos** entre gerações, prevenindo que operadores de crossover/mutação destruam boas soluções:

```python
def apply_elitism(population, fitnesses, elite_size=5):
    """
    Copia os 'elite_size' melhores indivíduos diretamente para a próxima geração.
    
    Regra: elite_size = max(1, int(0.05 * pop_size))
    Ou seja: manter os 5% melhores é um baseline sólido.
    """
    n = len(population)
    elite_size = min(elite_size, n)
    elite_indices = sorted(range(n), key=lambda i: fitnesses[i], reverse=True)[:elite_size]
    return [population[i][:] for i in elite_indices]

# Integração no loop principal
def next_generation(population, fitnesses, selection_fn, crossover_fn, mutation_fn,
                    pop_size, elite_size=5):
    """Gera a próxima geração com elitismo + crossover + mutação."""
    new_pop = apply_elitism(population, fitnesses, elite_size)
    
    while len(new_pop) < pop_size:
        p1 = selection_fn(population, fitnesses)
        p2 = selection_fn(population, fitnesses)
        c1, c2 = crossover_fn(p1, p2)
        new_pop.append(mutation_fn(c1))
        if len(new_pop) < pop_size:
            new_pop.append(mutation_fn(c2))
    
    return new_pop[:pop_size]
```

---

## Guia de Seleção de Operadores por Representação

```
Representação    │ Crossover          │ Mutação
─────────────────┼────────────────────┼─────────────────────
Binária          │ 1-pt, 2-pt, Unifor │ Bit-flip (p=1/n)
Inteira          │ 1-pt, 2-pt         │ Aleatório inteiro
Real (Float)     │ Uniforme, BLX-α    │ Gaussiana (sigma adaptativo)
Permutação (TSP) │ PMX, OX, CX        │ Swap, Inversion
```

---

## Exemplos de Uso

### Validação do PMX (Permutação sempre válida)
```python
import random
random.seed(42)

p1 = [1, 2, 3, 4, 5, 6, 7, 8]
p2 = [3, 7, 5, 1, 6, 8, 2, 4]

c1, c2 = crossover_pmx(p1, p2, p_cross=1.0)

# Verificar que são permutações válidas
assert sorted(c1) == list(range(1, 9)), "c1 não é permutação válida!"
assert sorted(c2) == list(range(1, 9)), "c2 não é permutação válida!"
print(f"Pai 1: {p1}")
print(f"Pai 2: {p2}")
print(f"Filho 1: {c1}")
print(f"Filho 2: {c2}")
print("Crossover PMX validado!")
```

---

## Checklist de Qualidade
- [ ] Operador de crossover compatível com a representação (PMX para permutação, 1-pt/uniforme para outros).
- [ ] `p_crossover` ∈ [0.7, 0.9] — nunca abaixo de 0.5.
- [ ] `p_mutation` ∈ [0.01, 0.1] — nunca abaixo de 1/n_genes (regra clássica).
- [ ] Elitismo ativo: pelo menos 1 indivíduo elite passando diretamente à próxima geração.
- [ ] Sigma da mutação Gaussiana calibrado ao domínio do problema (não uniforme para todos).
- [ ] Para TSP/scheduling, crossover PMX ou OX usado (nunca 1-pt simples, que gera permutações inválidas).
- [ ] Taxas de crossover e mutação registradas nos metadados do experimento para reprodutibilidade.
