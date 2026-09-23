---
name: ga-otimizacao-ml
description: Aplicações de Algoritmos Genéticos em Machine Learning — hyperparameter tuning sem gradiente, NeuroEvolution/NEAT para evolução de arquiteturas de redes neurais, e comparação com Optuna/Bayesian Optimization. Implementação com biblioteca DEAP.
pages: 446-460
---

# Habilidade: AG para Otimização de ML e NeuroEvolution 🤖🧬

## Objetivo
Aplicar **Algoritmos Genéticos** como motor de otimização de hiperparâmetros de modelos de Machine Learning e evolução de arquiteturas de redes neurais (**NeuroEvolution/NEAT**), em problemas onde o gradiente não está disponível ou o espaço de busca é discreto e combinatorial. Inclui implementação com a biblioteca **DEAP** e comparação com alternativas como Optuna e Bayesian Optimization.

---

## Conceitos Fundamentais

### Por que AG para Hyperparameter Tuning?

| Situação | AG | Optuna (Bayesian) | Grid/Random Search |
|---|---|---|---|
| Espaço **discreto** (arquitetura de NN) | ✅ Ótimo | ✅ Bom | ❌ Inviável |
| Espaço **contínuo** (learning rate) | ✅ Bom | ✅ Melhor | ✅ Razoável |
| Avaliação **cara** (treino full model) | ✅ Eficiente | ✅ Muito eficiente | ❌ Wasteful |
| **Sem gradiente** (black-box) | ✅ Nativo | ✅ Nativo | ✅ Nativo |
| Múltiplos **objetivos** (accuracy + speed) | ✅ NSGA-II | ⚠️ Limitado | ❌ Não suporta |
| **Paralelização** natural | ✅ Alta | ✅ Média | ✅ Alta |

**Regra:** Prefira Optuna/Bayesian para espaços contínuos menores (< 15 hiperparâmetros). Use AG para espaços combinatoriais, multi-objetivo ou muito grandes.

---

## Padrões e Boas Práticas

### Hyperparameter Tuning com AG (NumPy — sem DEAP)
```python
import numpy as np
import random
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import cross_val_score

# ─── Espaço de Busca Discreto ────────────────────────────────────────────────
SEARCH_SPACE = {
    "model_type": ["random_forest", "gradient_boosting"],
    "n_estimators": [50, 100, 200, 300, 500],
    "max_depth": [3, 5, 8, 10, 15, 20],
    "min_samples_split": [2, 5, 10, 20],
    "learning_rate": [0.01, 0.05, 0.1, 0.2, 0.3]  # apenas para GB
}
# Cromossomo: [idx_model, idx_n_est, idx_max_depth, idx_min_split, idx_lr]
GENE_RANGES = [len(v) for v in SEARCH_SPACE.values()]

def decode_individual(individual):
    """Converte índices do cromossomo em hiperparâmetros reais."""
    keys = list(SEARCH_SPACE.keys())
    params = {}
    for i, (key, idx) in enumerate(zip(keys, individual)):
        params[key] = SEARCH_SPACE[key][idx % GENE_RANGES[i]]
    return params

def fitness_ml(individual, X_train, y_train, cv=5):
    """
    Fitness = F1-macro em cross-validation de 5 folds.
    ATENÇÃO: Esta é a operação mais cara do AG — cada avaliação = 1 treino completo.
    Use cache para evitar reavaliações de indivíduos idênticos.
    """
    params = decode_individual(individual)
    model_type = params.pop("model_type")
    
    if model_type == "random_forest":
        params.pop("learning_rate", None)
        model = RandomForestClassifier(**params, random_state=42, class_weight="balanced")
    else:
        model = GradientBoostingClassifier(**params, random_state=42)
    
    try:
        scores = cross_val_score(model, X_train, y_train, cv=cv, scoring="f1_macro", n_jobs=-1)
        return scores.mean()
    except Exception:
        return 0.0  # Penalidade para configurações inválidas

# Cache para evitar reavaliações
fitness_cache = {}

def cached_fitness(individual, X_train, y_train):
    key = tuple(individual)
    if key not in fitness_cache:
        fitness_cache[key] = fitness_ml(individual, X_train, y_train)
    return fitness_cache[key]
```

### Hyperparameter Tuning com DEAP (Recomendado para Produção)
```python
import random
import numpy as np
from deap import base, creator, tools, algorithms
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

# Configuração do DEAP para maximização
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

# Espaço de busca
GENE_RANGES = [5, 6, 4]  # n_estimators, max_depth, min_samples_split

toolbox = base.Toolbox()
toolbox.register("attr_idx", lambda ranges: [random.randint(0, r - 1) for r in ranges], GENE_RANGES)
toolbox.register("individual", tools.initIterate, creator.Individual,
                 lambda: toolbox.attr_idx(GENE_RANGES))
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

N_ESTIMATORS_OPTIONS = [50, 100, 200, 300, 500]
MAX_DEPTH_OPTIONS = [3, 5, 8, 10, 15, 20]
MIN_SPLIT_OPTIONS = [2, 5, 10, 20]

def eval_hyperparams(individual, X, y):
    n_est = N_ESTIMATORS_OPTIONS[individual[0] % len(N_ESTIMATORS_OPTIONS)]
    max_d = MAX_DEPTH_OPTIONS[individual[1] % len(MAX_DEPTH_OPTIONS)]
    min_s = MIN_SPLIT_OPTIONS[individual[2] % len(MIN_SPLIT_OPTIONS)]
    
    model = RandomForestClassifier(
        n_estimators=n_est, max_depth=max_d, min_samples_split=min_s,
        random_state=42, class_weight="balanced"
    )
    scores = cross_val_score(model, X, y, cv=5, scoring="f1_macro", n_jobs=-1)
    return (scores.mean(),)  # Tuple obrigatório no DEAP

toolbox.register("evaluate", eval_hyperparams, X=None, y=None)  # X, y injetados depois
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutUniformInt, 
                 low=[0]*3, up=[r-1 for r in GENE_RANGES], indpb=0.3)
toolbox.register("select", tools.selTournament, tournsize=3)

def run_ga_hyperparameter_tuning(X_train, y_train, pop_size=30, n_gen=20):
    """
    Executa busca de hiperparâmetros via AG.
    pop_size=30, n_gen=20 → 600 avaliações máximas (com cache reduz drasticamente).
    """
    toolbox.register("evaluate", eval_hyperparams, X=X_train, y=y_train)
    
    population = toolbox.population(n=pop_size)
    hof = tools.HallOfFame(3)  # Preservar top-3 configurações
    
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("max", np.max)
    stats.register("avg", np.mean)
    
    final_pop, logbook = algorithms.eaSimple(
        population, toolbox,
        cxpb=0.7, mutpb=0.3, ngen=n_gen,
        stats=stats, halloffame=hof, verbose=True
    )
    
    # Melhor configuração encontrada
    best = hof[0]
    print(f"\nMelhor configuração encontrada:")
    print(f"  n_estimators = {N_ESTIMATORS_OPTIONS[best[0] % len(N_ESTIMATORS_OPTIONS)]}")
    print(f"  max_depth = {MAX_DEPTH_OPTIONS[best[1] % len(MAX_DEPTH_OPTIONS)]}")
    print(f"  min_samples_split = {MIN_SPLIT_OPTIONS[best[2] % len(MIN_SPLIT_OPTIONS)]}")
    print(f"  F1-macro (CV): {best.fitness.values[0]:.4f}")
    
    return hof
```

---

## NeuroEvolution / NEAT

### NeuroEvolution: Evoluir Pesos de Redes Neurais
Em vez de backpropagation, o AG evolui diretamente os pesos da rede. Útil quando:
- O ambiente não é diferenciável (jogos, robótica).
- A função de loss não é calculável por gradiente.
- O espaço de arquiteturas precisa ser explorado simultaneamente.

```python
import numpy as np
import random

class SimpleNeuralNet:
    """Rede neural feedforward com pesos evoluídos por AG."""
    
    def __init__(self, layer_sizes):
        self.layer_sizes = layer_sizes
        self.n_weights = sum(
            layer_sizes[i] * layer_sizes[i+1] + layer_sizes[i+1]
            for i in range(len(layer_sizes) - 1)
        )
    
    def set_weights(self, weights_flat):
        """Decodifica vetor plano de pesos em matrizes de cada camada."""
        self.layers = []
        idx = 0
        for i in range(len(self.layer_sizes) - 1):
            in_size = self.layer_sizes[i]
            out_size = self.layer_sizes[i+1]
            W = np.array(weights_flat[idx:idx + in_size * out_size]).reshape(in_size, out_size)
            b = np.array(weights_flat[idx + in_size * out_size:idx + in_size * out_size + out_size])
            self.layers.append((W, b))
            idx += in_size * out_size + out_size
    
    def predict(self, x):
        """Inferência forward pass."""
        h = np.array(x)
        for W, b in self.layers[:-1]:
            h = np.tanh(h @ W + b)  # Ativação tanh nas camadas ocultas
        W, b = self.layers[-1]
        return h @ W + b  # Saída linear

def neuroevolution_fitness(weights, net, X, y):
    """Fitness = acurácia da rede com os pesos evoluídos."""
    net.set_weights(weights)
    predictions = np.array([np.argmax(net.predict(x)) for x in X])
    return np.mean(predictions == y)

# Uso: evolui rede [4→8→3] para Iris dataset
net = SimpleNeuralNet([4, 8, 3])
n_weights = net.n_weights  # Tamanho do cromossomo = número de pesos
print(f"Cromossomo de NeuroEvolution: {n_weights} genes (pesos)")
```

### NEAT Simplificado com DEAP
```python
from deap import base, creator, tools, algorithms
import numpy as np
import random

def setup_neuroevolution_deap(n_weights, X_train, y_train):
    """Configura DEAP para NeuroEvolution de pesos reais."""
    creator.create("FitnessMaxNE", base.Fitness, weights=(1.0,))
    creator.create("IndividualNE", list, fitness=creator.FitnessMaxNE)
    
    toolbox = base.Toolbox()
    toolbox.register("attr_float", random.uniform, -2.0, 2.0)
    toolbox.register("individual", tools.initRepeat, creator.IndividualNE, 
                     toolbox.attr_float, n=n_weights)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    
    net = SimpleNeuralNet([X_train.shape[1], 16, len(np.unique(y_train))])
    
    def eval_net(individual):
        acc = neuroevolution_fitness(individual, net, X_train, y_train)
        return (acc,)
    
    toolbox.register("evaluate", eval_net)
    toolbox.register("mate", tools.cxBlend, alpha=0.3)
    toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=0.1, indpb=0.05)
    toolbox.register("select", tools.selTournament, tournsize=5)
    
    return toolbox

# NEAT real: usar biblioteca neat-python para evolução de topologia
# pip install neat-python
```

---

## Comparação: AG vs Optuna vs Grid Search

```python
# Optuna (Bayesian) — alternativa eficiente para espaços contínuos
import optuna

def optuna_objective(trial):
    n_est = trial.suggest_categorical("n_estimators", [50, 100, 200, 300, 500])
    max_d = trial.suggest_int("max_depth", 3, 20)
    min_s = trial.suggest_categorical("min_samples_split", [2, 5, 10, 20])
    
    model = RandomForestClassifier(
        n_estimators=n_est, max_depth=max_d, min_samples_split=min_s,
        random_state=42
    )
    return cross_val_score(model, X_train, y_train, cv=5, scoring="f1_macro").mean()

# study = optuna.create_study(direction="maximize")
# study.optimize(optuna_objective, n_trials=100)
# Melhor para: espaços contínuos, < 10-15 hiperparâmetros

# AG com DEAP — melhor para: espaços discretos grandes, multi-objetivo, arquiteturas
# hof = run_ga_hyperparameter_tuning(X_train, y_train, pop_size=30, n_gen=20)
```

---

## Checklist de Qualidade
- [ ] Cache de fitness implementado para evitar reavaliações de cromossomos idênticos.
- [ ] Cromossomo codificado como índices inteiros para espaços discretos (não floats diretamente).
- [ ] DEAP utilizado para produção (paralelização, Hall of Fama, logbook automático).
- [ ] `n_gen * pop_size` estimado antes de executar para prever tempo total de execução.
- [ ] Para NeuroEvolution: pesos inicializados em [-2, 2] com mutação Gaussiana sigma=0.1.
- [ ] Optuna/Bayesian avaliado como alternativa quando o espaço é principalmente contínuo.
- [ ] NSGA-II considerado quando há múltiplos objetivos conflitantes (accuracy vs latência).
