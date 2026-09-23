---
name: ga-aplicacoes
description: Aplicações práticas de Algoritmos Genéticos: Caixeiro Viajante (TSP), otimização de portfólios, scheduling, roteamento e evolução de arquiteturas de redes neurais.
pages: 397-470
---

# Algoritmos Genéticos: Aplicações Práticas (GA Applications) 🧬📈

## Objetivo
Capacitar o desenvolvimento e implementação de soluções práticas para problemas complexos de otimização combinatória e contínua do mundo real utilizando **Algoritmos Genéticos (AG)** e o framework **DEAP (Distributed Evolutionary Algorithms in Python)**. Abrange problemas clássicos NP-difíceis como o Caixeiro Viajante (TSP), alocação ótima de ativos financeiros (Portfólios de Markowitz / Sharpe Ratio), escalonamento de processos (Scheduling / Job Shop) e neuroevolução.

---

## Conceitos Fundamentais

### 1. Caixeiro Viajante (Travelling Salesperson Problem - TSP)
- **Problema:** Encontrar a rota de menor distância que visita um conjunto de $N$ cidades exatamente uma vez e retorna à cidade de origem.
- **Representação:** Permutação de inteiros `[cidade_0, cidade_3, cidade_1, ..., cidade_k]`.
- **Operadores específicos:**
  - Crossover: **OX (Order Crossover)** ou **PMX (Partially Mapped Crossover)** para evitar cidades duplicadas ou ausentes.
  - Mutação: **Swap**, **Inversion** ou **Shuffle Indexes** (troca de posição de índices preservando a unicidade).
- **Função Fitness:** Inverso da distância euclidiana total percorrida (ou valor negativo da distância para minimização).

### 2. Otimização de Portfólio de Ativos (Teoria Moderna de Markowitz)
- **Problema:** Alocar proporções de capital $w_i \in [0, 1]$ em $N$ ativos de modo a maximizar o Retorno Esperado e minimizar a Volatilidade (Risco), sujeito a $\sum w_i = 1$.
- **Representação:** Vetor contínuo de pesos normalizados (números reais).
- **Métrica de Fitness:** **Índice de Sharpe**:
  $$\text{Sharpe Ratio} = \frac{E[R_p] - R_f}{\sigma_p}$$
  Onde $E[R_p] = \mathbf{w}^T \boldsymbol{\mu}$ e $\sigma_p = \sqrt{\mathbf{w}^T \boldsymbol{\Sigma} \mathbf{w}}$.
- **Tratamento de Restrições:** Normalização dinâmica no cálculo do fitness (`w = w / sum(w)`) ou penalização para pesos negativos / alavancagem excessiva.

### 3. Escalonamento e Roteamento (Job Shop & VRP)
- **Scheduling (Job Shop / Flow Shop):** Ordenação de tarefas em máquinas respeitando precedências e tempos de setup para minimizar o *makespan* (tempo total de conclusão).
- **Vehicle Routing Problem (VRP):** Extensão do TSP com capacidade de carga de veículos, janelas de tempo de entrega e múltiplos depósitos.

### 4. Neuroevolução e Otimização de Hiperparâmetros (NAS / AutoML)
- Evolução de topologias de redes neurais artificiais (NEAT) ou seleção genética de hiperparâmetros (número de camadas, taxa de aprendizado, dropout, kernels de CNN).

---

## Padrões e Boas Práticas

| Domínio da Aplicação | Representação Cromossômica | Crossover Recomendado | Mutação Recomendada | Restrição Crítica |
|---|---|---|---|---|
| **TSP / Roteamento** | Permutação de Inteiros | Order Crossover (`cxOrdered`) | Inversão / Swap (`mutShuffleIndexes`) | Sem nós duplicados ou omitidos |
| **Portfólio de Investimentos** | Vetor Real ($\mathbb{R}^N$) | Blended Crossover (`cxBlend`) | Mutação Gaussiana (`mutGaussian`) | Soma dos pesos $= 1.0$ e $w_i \ge 0$ |
| **Job Shop Scheduling** | Lista com repetição de IDs | Precedence Preserving (PPX) | Insertion Mutation | Ordem de precedência temporal |
| **Seleção de Features** | Vetor Binário ($\{0, 1\}^N$) | Crossover de Dois Pontos (`cxTwoPoint`) | Bit Flip (`mutFlipBit`) | Pelo menos $K$ features ativas |

### Tratamento de Restrições (Penalty Functions)
1. **Pena de Morte (Death Penalty):** Indivíduos inviáveis recebem fitness $-\infty$ (ineficiente se o espaço viável for estreito).
2. **Penalização Suave (Soft Penalty):** Subtrair do fitness um valor proporcional à magnitude da violação da restrição:
   $$\text{Fitness}_{\text{ajustado}} = \text{Fitness}_{\text{original}} - \lambda \cdot \text{Violação}$$
3. **Reparo Genético:** Ajustar diretamente o cromossomo na função de decodificação/fitness (ex: normalizar vetor de pesos para que a soma seja 1).

---

## Exemplos de Código em Python

### 1. Caixeiro Viajante (TSP) com DEAP
```python
import array
import random
import numpy as np
from deap import base, creator, tools, algorithms

# 1. Definição do Problema (Cidades em coordenadas 2D)
NUM_CITIES = 20
np.random.seed(42)
city_coords = {i: (np.random.uniform(0, 100), np.random.uniform(0, 100)) for i in range(NUM_CITIES)}

def calculate_distance_matrix(coords):
    n = len(coords)
    matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            matrix[i][j] = np.linalg.norm(np.array(coords[i]) - np.array(coords[j]))
    return matrix

dist_matrix = calculate_distance_matrix(city_coords)

# 2. Configuração do DEAP
# Fitness: Minimizar a distância total (peso negativo)
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
# Gerar permutação sem repetições
toolbox.register("indices", random.sample, range(NUM_CITIES), NUM_CITIES)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.indices)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# Função Fitness: Distância do ciclo completo
def eval_tsp(individual):
    dist = 0.0
    for i in range(len(individual)):
        u = individual[i]
        v = individual[(i + 1) % len(individual)]
        dist += dist_matrix[u][v]
    return (dist,)

# Registro dos Operadores
toolbox.register("evaluate", eval_tsp)
toolbox.register("mate", tools.cxOrdered)  # Crossover de Ordem (preserva permutação)
toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)  # Mutação por swap/embaralhamento
toolbox.register("select", tools.selTournament, tournsize=3)

# 3. Execução do Algoritmo Genético
def run_tsp():
    random.seed(42)
    pop = toolbox.population(n=150)
    hof = tools.HallOfFame(1)  # Preserva o melhor absoluto (elitismo)
    stats = tools.Statistics(lambda ind: ind.fitness.values[0])
    stats.register("min", np.min)
    stats.register("avg", np.mean)

    pop, logbook = algorithms.eaSimple(
        pop, toolbox, cxpb=0.8, mutpb=0.2, ngen=200, stats=stats, halloffame=hof, verbose=False
    )

    best = hof[0]
    print(f"[TSP] Melhor distância encontrada: {best.fitness.values[0]:.2f}")
    print(f"[TSP] Sequência da Rota: {best}")
    return best, logbook

if __name__ == "__main__":
    run_tsp()
```

---

### 2. Otimização de Portfólio de Ações (Sharpe Ratio) com NumPy e DEAP
```python
import random
import numpy as np
from deap import base, creator, tools, algorithms

# 1. Simulação de Dados de Mercado (5 Ativos)
NUM_ASSETS = 5
RISK_FREE_RATE = 0.02  # Taxa livre de risco (2% a.a.)

np.random.seed(101)
# Retornos anuais médios esperados
expected_returns = np.array([0.15, 0.12, 0.18, 0.10, 0.14])
# Matriz de covariância simulada
A = np.random.randn(NUM_ASSETS, NUM_ASSETS)
cov_matrix = np.dot(A, A.T) * 0.005

# 2. Configuração do DEAP
# Fitness: Maximizar Sharpe Ratio (peso positivo)
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
# Pesos contínuos entre 0 e 1
toolbox.register("attr_float", random.uniform, 0.0, 1.0)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float, n=NUM_ASSETS)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# Avaliação do Portfólio com Normalização dos Pesos
def eval_portfolio(individual):
    weights = np.array(individual)
    sum_w = np.sum(weights)
    if sum_w == 0:
        return (-100.0,)
    weights = weights / sum_w  # Restrição: soma dos pesos = 100%

    port_return = np.dot(weights, expected_returns)
    port_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    
    if port_volatility == 0:
        sharpe = -100.0
    else:
        sharpe = (port_return - RISK_FREE_RATE) / port_volatility

    return (sharpe,)

toolbox.register("evaluate", eval_portfolio)
toolbox.register("mate", tools.cxBlend, alpha=0.5)
toolbox.register("mutate", tools.mutGaussian, mu=0.0, sigma=0.1, indpb=0.2)
toolbox.register("select", tools.selTournament, tournsize=3)

# 3. Execução
def run_portfolio():
    random.seed(42)
    pop = toolbox.population(n=100)
    hof = tools.HallOfFame(1)

    pop, _ = algorithms.eaSimple(
        pop, toolbox, cxpb=0.7, mutpb=0.3, ngen=100, halloffame=hof, verbose=False
    )

    best_weights = np.array(hof[0])
    best_weights = np.maximum(0, best_weights)  # Não permitir posições vendidas (no short)
    best_weights /= np.sum(best_weights)

    print(f"[Portfólio] Melhor Sharpe Ratio: {hof[0].fitness.values[0]:.4f}")
    for i, w in enumerate(best_weights):
        print(f"  Ativo {i+1}: {w*100:.2f}%")

if __name__ == "__main__":
    run_portfolio()
```

---

## Checklist de Qualidade e Governança

- [ ] **Representação Correta:** Problemas permutacionais (TSP/Job Shop) utilizam operadores específicos (`cxOrdered`, `cxPartialyMatched`) para não corromper o conjunto de índices.
- [ ] **Tratamento de Restrições:** Em alocações percentuais (Portfólios), a soma unitária $\sum w_i = 1$ é tratada via normalização na avaliação ou restrições de penalidade.
- [ ] **Elitismo Habilitado:** Utilização de `HallOfFame` ou elitismo manual para preservar o melhor cromossomo entre gerações sucessivas.
- [ ] **Métricas Claras:** Otimizações financeiras monitoram simultaneamente retorno, volatilidade e Sharpe Ratio; roteamentos monitoram comprimento euclidiano e tempo de trânsito.
- [ ] **Reprodutibilidade:** Sementes de aleatoriedade fixadas tanto no `random` da biblioteca padrão quanto no `numpy.random`.
