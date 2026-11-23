---
name: genetic-algorithms-expert
description: "Use quando a tarefa envolver: Algoritmos Geneticos completos — fundamentos, cromossomos, operadores de selecao (Torneio, Roleta), crossover, mutacao adaptativa, otimizacao de hiperparametros em ML e NeuroEvolution com DEAP."
---

# Habilidade: Genetic Algorithms Expert (AG) 🧬⚡

## Propósito
Autoridade técnica em metaheurísticas de busca global e otimização inspiradas na evolução natural de Darwin. Abrange desde a codificação de cromossomos e funções de fitness até operadores de reprodução, seleção estocástica, sintonia de hiperparâmetros de Machine Learning e NeuroEvolution com a biblioteca **DEAP**.

---

## 1. Fundamentos e Ciclo Evolutivo
- **Indivíduo / Cromossomo:** Solução candidata representada como vetor (binário, inteiro ou ponto flutuante).
- **Gene / Alelo:** Variável de decisão e seu valor específico.
- **População:** Conjunto de $N$ indivíduos avaliados concorrentemente.
- **Fitness (Aptidão):** Função objetivo escalar ou multiobjetivo (NSGA-II) calculada a cada geração.
- **Ciclo:** Inicialização $\to$ Avaliação $\to$ Seleção $\to$ Crossover $\to$ Mutação $\to$ Elitismo $\to$ Critério de Parada (gerações, estagnação ou convergência).

---

## 2. Operadores Genéticos Avançados
- **Seleção:**
  - *Torneio:* Seleciona o melhor entre $k$ indivíduos aleatórios (controle fino da pressão seletiva via $k$).
  - *Roleta (Roulette Wheel):* Probabilidade proporcional ao fitness normalizado (cuidado com super-indivíduos prematuros).
  - *Rank-based:* Ordenação ordinal de aptidão para mitigar convergência precoce.
- **Crossover (Recombinação):**
  - *One-Point / Two-Point Crossover:* Para representações discretas e binárias.
  - *Uniform Crossover:* Troca probabilística gene a gene.
  - *SBX (Simulated Binary Crossover) / Blend Crossover (BLX-$\alpha$):* Para cromossomos contínuos/reais.
- **Mutação:**
  - *Bit-Flip:* Inversão aleatória em genótipos binários.
  - *Gaussiana:* Perturbação $\mathcal{N}(0, \sigma)$ em valores contínuos.
  - *Swap / Scramble / Inversion:* Para problemas permutacionais (ex: Caixeiro Viajante - TSP).
- **Elitismo:** Preserva intactos os $E$ melhores indivíduos diretamente para a próxima geração.

---

## 3. Otimização de Hiperparâmetros em ML & NeuroEvolution
- **Sintonia com DEAP:**
  - Codificação de hiperparâmetros (árvores, learning rates, regularização, camadas).
  - Paralelização de fitness via `multiprocessing` ou Ray.
  - *Caching de Fitness:* Hash do genótipo para evitar reavaliação de indivíduos repetidos.
- **NeuroEvolution:**
  - Evolução direta de pesos sinápticos e topologias (NEAT) em ambientes não-diferenciáveis (jogos, robótica, reforço sem gradiente).
