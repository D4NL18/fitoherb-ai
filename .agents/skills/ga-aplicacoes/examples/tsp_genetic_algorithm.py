"""
Resolução do Problema do Caixeiro Viajante (TSP) com Algoritmo Genético (DEAP).

Cobre:
- Representação permutacional de cidades (sem duplicatas ou omissões)
- Crossover Ordenado OX (`tools.cxOrdered`)
- Mutação por troca de duas posições (Swap Mutation)
- Elitismo com `HallOfFame`
- Critério de parada por estagnação (early stopping) + limite de gerações

Dependências:
    pip install deap numpy
"""

from __future__ import annotations

import random

import numpy as np
from deap import base, creator, tools


def gerar_matriz_distancias(num_cidades: int, seed: int = 42) -> tuple[np.ndarray, np.ndarray]:
    """Gera coordenadas 2D aleatórias e sua matriz simétrica de distâncias euclidianas."""
    rng = np.random.default_rng(seed)
    coords = rng.uniform(0.0, 100.0, size=(num_cidades, 2))
    diff = coords[:, np.newaxis, :] - coords[np.newaxis, :, :]
    dist_matrix = np.linalg.norm(diff, axis=-1)
    return coords, dist_matrix


def mutacao_swap(individuo: list[int]) -> tuple[list[int]]:
    """Troca duas cidades de posição preservando a validade da permutação."""
    i, j = random.sample(range(len(individuo)), 2)
    individuo[i], individuo[j] = individuo[j], individuo[i]
    return (individuo,)


def resolver_tsp(
    num_cidades: int = 20,
    pop_size: int = 120,
    max_gen: int = 300,
    paciencia: int = 40,
    cxpb: float = 0.85,
    mutpb: float = 0.20,
    elitism_size: int = 2,
    seed: int = 42,
) -> tuple[list[int], float]:
    """Executa AG para TSP com crossover OX, mutação swap e parada por estagnação."""
    random.seed(seed)
    _, dist_matrix = gerar_matriz_distancias(num_cidades, seed=seed)

    if not hasattr(creator, "FitnessMinTSP"):
        creator.create("FitnessMinTSP", base.Fitness, weights=(-1.0,))
    if not hasattr(creator, "IndividualTSP"):
        creator.create("IndividualTSP", list, fitness=creator.FitnessMinTSP)

    toolbox = base.Toolbox()
    toolbox.register("indices", random.sample, range(num_cidades), num_cidades)
    toolbox.register("individual", tools.initIterate, creator.IndividualTSP, toolbox.indices)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    def avaliar_rota(individuo: list[int]) -> tuple[float]:
        distancia = 0.0
        n = len(individuo)
        for i in range(n):
            distancia += float(dist_matrix[individuo[i], individuo[(i + 1) % n]])
        return (distancia,)

    toolbox.register("evaluate", avaliar_rota)
    toolbox.register("mate", tools.cxOrdered)  # Order Crossover (OX)
    toolbox.register("mutate", mutacao_swap)
    toolbox.register("select", tools.selTournament, tournsize=3)

    populacao = toolbox.population(n=pop_size)
    hof = tools.HallOfFame(elitism_size)

    for ind in populacao:
        ind.fitness.values = toolbox.evaluate(ind)
    hof.update(populacao)

    melhor_distancia = hof[0].fitness.values[0]
    sem_melhoria = 0

    for gen in range(1, max_gen + 1):
        elite = [toolbox.clone(ind) for ind in hof]
        selecionados = toolbox.select(populacao, len(populacao) - elitism_size)
        descendentes = [toolbox.clone(ind) for ind in selecionados]

        for c1, c2 in zip(descendentes[::2], descendentes[1::2]):
            if random.random() < cxpb:
                toolbox.mate(c1, c2)
                del c1.fitness.values
                del c2.fitness.values

        for mutante in descendentes:
            if random.random() < mutpb:
                toolbox.mutate(mutante)
                del mutante.fitness.values

        for ind in descendentes:
            if not ind.fitness.valid:
                ind.fitness.values = toolbox.evaluate(ind)

        populacao = elite + descendentes
        hof.update(populacao)

        atual = hof[0].fitness.values[0]
        if atual < melhor_distancia - 1e-6:
            melhor_distancia = atual
            sem_melhoria = 0
        else:
            sem_melhoria += 1

        if gen % 25 == 0 or sem_melhoria == 0:
            media = float(np.mean([ind.fitness.values[0] for ind in populacao]))
            print(f"Geração {gen:03d} | Melhor distância: {atual:.2f} | Média: {media:.2f}")

        if sem_melhoria >= paciencia:
            print(f"Critério de parada atingido na geração {gen} ({paciencia} gerações sem melhoria).")
            break

    melhor_rota = list(hof[0])
    assert len(set(melhor_rota)) == num_cidades, "Permutação inválida detectada!"
    return melhor_rota, float(hof[0].fitness.values[0])


if __name__ == "__main__":
    rota, distancia = resolver_tsp(num_cidades=20, pop_size=120, max_gen=300, paciencia=40)
    print("\n=== Resultado Final (TSP) ===")
    print(f"Melhor distância total: {distancia:.2f}")
    print(f"Rota encontrada:        {rota + [rota[0]]}")
