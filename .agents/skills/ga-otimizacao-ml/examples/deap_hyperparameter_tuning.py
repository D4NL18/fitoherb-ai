"""
Otimização de Hiperparâmetros de Machine Learning com Algoritmo Genético (DEAP).

Cobre:
- Codificação discreta de hiperparâmetros (RandomForestClassifier)
- Cache de fitness para evitar reavaliações custosas de cross-validation
- Seleção por torneio (`selTournament`)
- Crossover de dois pontos (`cxTwoPoint`)
- Mutação uniforme inteira (`mutUniformInt`)
- Elitismo explícito com `HallOfFame` preservando os melhores indivíduos a cada geração

Dependências:
    pip install deap numpy scikit-learn
"""

from __future__ import annotations

import random
from typing import Any

import numpy as np
from deap import base, creator, tools
from sklearn.datasets import load_wine
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score

SEARCH_SPACE: dict[str, list[Any]] = {
    "n_estimators": [30, 50, 100, 150, 200],
    "max_depth": [2, 4, 6, 8, 12, None],
    "min_samples_split": [2, 4, 6, 10],
    "min_samples_leaf": [1, 2, 4, 6],
    "max_features": ["sqrt", "log2", None],
}
PARAM_KEYS = list(SEARCH_SPACE.keys())
GENE_UPPER_BOUNDS = [len(SEARCH_SPACE[k]) - 1 for k in PARAM_KEYS]


def decodificar_cromossomo(individuo: list[int]) -> dict[str, Any]:
    """Converte vetor de índices inteiros em dicionário de hiperparâmetros."""
    return {
        chave: SEARCH_SPACE[chave][idx % len(SEARCH_SPACE[chave])]
        for chave, idx in zip(PARAM_KEYS, individuo)
    }


def executar_ga_hiperparametros(
    X: np.ndarray,
    y: np.ndarray,
    pop_size: int = 20,
    n_gen: int = 12,
    cxpb: float = 0.7,
    mutpb: float = 0.3,
    elitism_size: int = 2,
    seed: int = 42,
) -> tuple[dict[str, Any], float]:
    """Executa busca evolutiva de hiperparâmetros com elitismo e cache de fitness."""
    random.seed(seed)
    np.random.seed(seed)

    if not hasattr(creator, "FitnessMaxML"):
        creator.create("FitnessMaxML", base.Fitness, weights=(1.0,))
    if not hasattr(creator, "IndividualML"):
        creator.create("IndividualML", list, fitness=creator.FitnessMaxML)

    toolbox = base.Toolbox()
    toolbox.register(
        "attr_genome",
        lambda: [random.randint(0, ub) for ub in GENE_UPPER_BOUNDS],
    )
    toolbox.register(
        "individual",
        tools.initIterate,
        creator.IndividualML,
        toolbox.attr_genome,
    )
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    fitness_cache: dict[tuple[int, ...], float] = {}
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)

    def avaliar(individuo: list[int]) -> tuple[float]:
        chave = tuple(individuo)
        if chave not in fitness_cache:
            params = decodificar_cromossomo(individuo)
            modelo = RandomForestClassifier(
                **params,
                random_state=seed,
                class_weight="balanced",
            )
            scores = cross_val_score(modelo, X, y, cv=cv, scoring="f1_macro", n_jobs=-1)
            fitness_cache[chave] = float(scores.mean())
        return (fitness_cache[chave],)

    toolbox.register("evaluate", avaliar)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register(
        "mutate",
        tools.mutUniformInt,
        low=[0] * len(GENE_UPPER_BOUNDS),
        up=GENE_UPPER_BOUNDS,
        indpb=0.25,
    )
    toolbox.register("select", tools.selTournament, tournsize=3)

    populacao = toolbox.population(n=pop_size)
    hof = tools.HallOfFame(elitism_size)

    # Avaliação inicial
    for ind in populacao:
        ind.fitness.values = toolbox.evaluate(ind)
    hof.update(populacao)

    for gen in range(1, n_gen + 1):
        # Elitismo: preserva os melhores indivíduos intactos
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

        invalidos = [ind for ind in descendentes if not ind.fitness.valid]
        for ind in invalidos:
            ind.fitness.values = toolbox.evaluate(ind)

        populacao = elite + descendentes
        hof.update(populacao)

        melhor_gen = hof[0].fitness.values[0]
        media_gen = float(np.mean([ind.fitness.values[0] for ind in populacao]))
        print(
            f"Geração {gen:02d} | Melhor F1-macro: {melhor_gen:.4f} | "
            f"Média: {media_gen:.4f} | Avaliações únicas: {len(fitness_cache)}"
        )

    melhor = hof[0]
    return decodificar_cromossomo(melhor), float(melhor.fitness.values[0])


if __name__ == "__main__":
    dados = load_wine()
    melhores_params, melhor_f1 = executar_ga_hiperparametros(
        dados.data,
        dados.target,
        pop_size=16,
        n_gen=10,
    )
    print("\n=== Melhor Configuração Encontrada ===")
    for k, v in melhores_params.items():
        print(f"  {k}: {v}")
    print(f"  F1-macro (5-fold CV): {melhor_f1:.4f}")
