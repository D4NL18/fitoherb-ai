import time
from typing import List, Dict, Any, Optional
from app.core.config import settings
from .routing_chromosome import RoutingChromosome
from .routing_operators import RoutingOperators
from .routing_fitness import RoutingFitnessEvaluator

class RoutingGeneticSolver:
    def __init__(
        self,
        durations_matrix_sec: List[List[float]],
        distances_matrix_m: List[List[float]],
        deliveries_data: List[Dict[str, Any]],
        return_to_depot: bool = True,
        population_size: int = settings.GA_POPULATION_SIZE,
        generations: int = settings.GA_GENERATIONS,
        mutation_rate: float = settings.GA_MUTATION_RATE,
        crossover_rate: float = settings.GA_CROSSOVER_RATE,
        elitism_count: int = settings.GA_ELITISM_COUNT
    ):
        self.num_stops = len(deliveries_data)
        self.deliveries = deliveries_data
        self.return_to_depot = return_to_depot
        
        # Mapeia travas manuais: fixed_order (1-indexed) -> posicao_0_indexed
        # Exemplo: parada com fixed_order = 1 vai na posicao 0 do cromossomo
        self.fixed_positions: Dict[int, int] = {}
        for idx_0, d in enumerate(deliveries_data):
            f_ord = d.get("fixed_order")
            if f_ord is not None and isinstance(f_ord, int) and 1 <= f_ord <= self.num_stops:
                target_pos = f_ord - 1
                stop_node = idx_0 + 1
                self.fixed_positions[target_pos] = stop_node

        self.evaluator = RoutingFitnessEvaluator(
            durations_matrix_sec=durations_matrix_sec,
            distances_matrix_m=distances_matrix_m,
            deliveries_data=deliveries_data,
            return_to_depot=return_to_depot,
            fixed_positions=self.fixed_positions
        )
        
        self.population_size = max(10, population_size)
        self.generations = max(5, generations)
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elitism_count = elitism_count

        self.history: List[float] = []
        self.best_chromosome: Optional[RoutingChromosome] = None

    def _generate_nearest_neighbor_hotstart(self) -> RoutingChromosome:
        """
        Hotstart Heurístico com Respeito a Posições Fixas:
        Constrói uma solução de alta qualidade respeitando os nós fixos
        e preenchendo as lacunas intermediárias com o vizinho mais próximo.
        """
        if self.num_stops <= 1:
            return RoutingChromosome(sequence=list(range(1, self.num_stops + 1)))

        all_stops = set(range(1, self.num_stops + 1))
        locked_stops = set(self.fixed_positions.values())
        free_stops = all_stops - locked_stops

        seq = [0] * self.num_stops
        for pos, stop_idx in self.fixed_positions.items():
            if 0 <= pos < self.num_stops:
                seq[pos] = stop_idx

        curr_loc = 0
        for i in range(self.num_stops):
            if seq[i] != 0:
                curr_loc = seq[i]
            else:
                if free_stops:
                    nxt = min(free_stops, key=lambda s_idx: self.evaluator.durations[curr_loc][s_idx])
                    seq[i] = nxt
                    free_stops.remove(nxt)
                    curr_loc = nxt

        return RoutingChromosome(sequence=seq)

    def solve(self) -> Dict[str, Any]:
        start_time = time.time()

        if self.num_stops == 0:
            return {
                "elapsed_seconds": 0.0,
                "best_fitness": 0.0,
                "total_time_minutes": 0.0,
                "total_distance_km": 0.0,
                "ordered_sequence": [],
                "fitness_history": []
            }

        # 1. População Inicial
        population: List[RoutingChromosome] = []

        hotstart_ind = self._generate_nearest_neighbor_hotstart()
        self.evaluator.evaluate(hotstart_ind)
        population.append(hotstart_ind)

        while len(population) < self.population_size:
            ind = RoutingChromosome.random_with_locks(self.num_stops, self.fixed_positions)
            self.evaluator.evaluate(ind)
            population.append(ind)

        population.sort(key=lambda ind: ind.fitness)
        self.best_chromosome = population[0].copy()

        # 2. Ciclo Evolutivo
        for gen in range(1, self.generations + 1):
            if population[0].fitness < self.best_chromosome.fitness:
                self.best_chromosome = population[0].copy()

            self.history.append(self.best_chromosome.fitness)

            if gen == self.generations:
                break

            # Elitismo: preserva os melhores indivíduos
            new_population: List[RoutingChromosome] = []
            for i in range(min(self.elitism_count, len(population))):
                new_population.append(population[i].copy())

            # Reprodução e Mutação
            while len(new_population) < self.population_size:
                p1 = RoutingOperators.tournament_selection(population, k=3)
                p2 = RoutingOperators.tournament_selection(population, k=3)

                c1, c2 = RoutingOperators.locked_order_crossover(
                    p1, p2, self.fixed_positions, pc=self.crossover_rate
                )
                c1 = RoutingOperators.locked_mutate(c1, self.fixed_positions, pm=self.mutation_rate)
                c2 = RoutingOperators.locked_mutate(c2, self.fixed_positions, pm=self.mutation_rate)

                self.evaluator.evaluate(c1)
                new_population.append(c1)

                if len(new_population) < self.population_size:
                    self.evaluator.evaluate(c2)
                    new_population.append(c2)

            population = sorted(new_population, key=lambda ind: ind.fitness)

        self.evaluator.evaluate(self.best_chromosome)
        elapsed = round(time.time() - start_time, 3)

        return {
            "elapsed_seconds": elapsed,
            "best_fitness": self.best_chromosome.fitness,
            "total_time_minutes": self.best_chromosome.total_time_minutes,
            "total_distance_km": self.best_chromosome.total_distance_km,
            "ordered_sequence": self.best_chromosome.sequence,
            "penalties": self.best_chromosome.penalties,
            "fitness_history": self.history
        }
