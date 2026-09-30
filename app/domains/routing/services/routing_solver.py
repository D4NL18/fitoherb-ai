import time
from typing import List, Dict, Any, Optional, Tuple
from app.core.config import settings
from .routing_chromosome import RoutingChromosome
from .routing_operators import RoutingOperators
from .routing_fitness import RoutingFitnessEvaluator
from app.domains.routing.traffic_model import TrafficPredictor

class RoutingGeneticSolver:
    def __init__(
        self,
        durations_matrix_sec: List[List[float]],
        distances_matrix_m: List[List[float]],
        deliveries_data: List[Dict[str, Any]],
        return_to_depot: bool = True,
        departure_time_minutes: Optional[float] = None,
        default_service_minutes: int = 20,
        base_city: Optional[str] = None,
        points_cities: List[str] = None,
        coordinates: List[Tuple[float, float]] = None,
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
            fixed_positions=self.fixed_positions,
            departure_time_minutes=departure_time_minutes,
            default_service_minutes=default_service_minutes,
            base_city=base_city,
            points_cities=points_cities,
            coordinates=coordinates
        )
        
        self.population_size = max(10, population_size)
        self.generations = max(5, generations)
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elitism_count = elitism_count

        self.history: List[float] = []
        self.best_chromosome: Optional[RoutingChromosome] = None

    def _advance_clock_for_stop(self, from_loc: int, to_loc: int, curr_clock: Optional[float]) -> Optional[float]:
        """Avança o relógio acumulado considerando tempo de viagem, espera pontual e duração do serviço."""
        if curr_clock is None:
            return None

        travel_min = (self.evaluator.durations[from_loc][to_loc] / 60.0)
        clock = curr_clock + travel_min
        target_time_str = self.deliveries[to_loc - 1].get("target_arrival_time")
        if target_time_str:
            t_min = TrafficPredictor.parse_time_str(target_time_str)
            if t_min and clock < t_min:
                clock = float(t_min)
        srv = self.deliveries[to_loc - 1].get("service_duration_minutes") or self.evaluator.default_service_minutes
        return clock + srv

    def _select_candidate_by_priority_or_distance(self, candidates: list[int], curr_loc: int) -> int:
        """Seleciona o próximo ponto priorizando urgência (CRITICAL > HIGH) e menor distância."""
        critical_stops = [s for s in candidates if self.deliveries[s - 1].get("priority") == "CRITICAL"]
        if critical_stops:
            return min(critical_stops, key=lambda s_idx, loc=curr_loc: self.evaluator.durations[loc][s_idx])

        high_stops = [s for s in candidates if self.deliveries[s - 1].get("priority") == "HIGH"]
        if high_stops:
            return min(high_stops, key=lambda s_idx, loc=curr_loc: self.evaluator.durations[loc][s_idx])

        return min(candidates, key=lambda s_idx, loc=curr_loc: self.evaluator.durations[loc][s_idx])

    def _find_feasible_stops_before_timed(
        self,
        curr_loc: int,
        curr_clock: float,
        free_stops: set[int],
        earliest_timed: int,
        earliest_target: float
    ) -> list[int]:
        """Filtra paradas livres que cabem na rota antes do horário marcado sem atrasar o compromisso."""
        feasible = []
        for cand in free_stops:
            if self.deliveries[cand - 1].get("target_arrival_time"):
                continue
            t_to_cand = self.evaluator.durations[curr_loc][cand] / 60.0
            srv_cand = self.deliveries[cand - 1].get("service_duration_minutes") or self.evaluator.default_service_minutes
            t_cand_to_timed = self.evaluator.durations[cand][earliest_timed] / 60.0
            arrival_after_cand = curr_clock + t_to_cand + srv_cand + t_cand_to_timed
            if arrival_after_cand <= earliest_target + 5.0:
                feasible.append(cand)
        return feasible

    def _pick_best_timed_candidate(
        self,
        curr_loc: int,
        curr_clock: Optional[float],
        free_stops: set[int],
        timed_stops: list[int]
    ) -> Optional[int]:
        """Escolhe o próximo ponto considerando compromissos com horário marcado e folga temporal."""
        if not timed_stops:
            return None

        timed_stops.sort(
            key=lambda s_idx: TrafficPredictor.parse_time_str(self.deliveries[s_idx - 1].get("target_arrival_time")) or 9999
        )
        if curr_clock is None:
            return timed_stops[0]

        earliest_timed = timed_stops[0]
        earliest_target = TrafficPredictor.parse_time_str(self.deliveries[earliest_timed - 1].get("target_arrival_time"))
        if earliest_target is None:
            return earliest_timed

        direct_travel = self.evaluator.durations[curr_loc][earliest_timed] / 60.0
        slack = earliest_target - (curr_clock + direct_travel)
        if slack <= 25.0:
            return earliest_timed

        feasible_before = self._find_feasible_stops_before_timed(
            curr_loc, curr_clock, free_stops, earliest_timed, earliest_target
        )
        if feasible_before:
            return self._select_candidate_by_priority_or_distance(feasible_before, curr_loc)

        return earliest_timed

    def _pick_next_hotstart_stop(
        self,
        curr_loc: int,
        curr_clock: Optional[float],
        free_stops: set[int]
    ) -> int:
        """Determina a próxima parada do hotstart com base em horários marcados ou guloso por prioridade."""
        timed_stops = [s for s in free_stops if self.deliveries[s - 1].get("target_arrival_time")]
        selected = self._pick_best_timed_candidate(curr_loc, curr_clock, free_stops, timed_stops)
        if selected is not None:
            return selected
        return self._select_candidate_by_priority_or_distance(list(free_stops), curr_loc)

    def _generate_nearest_neighbor_hotstart(self) -> RoutingChromosome:
        """
        Hotstart Heurístico com Respeito a Posições Fixas e Varredura Progressiva:
        Constrói uma solução inicial gulosa priorizando nós urgentes e paradas no caminho.
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
        curr_clock = float(self.evaluator.departure_time_minutes) if self.evaluator.departure_time_minutes is not None else None

        for i in range(self.num_stops):
            if seq[i] != 0:
                nxt = seq[i]
            else:
                if not free_stops:
                    break
                nxt = self._pick_next_hotstart_stop(curr_loc, curr_clock, free_stops)
                seq[i] = nxt
                free_stops.remove(nxt)

            curr_clock = self._advance_clock_for_stop(curr_loc, nxt, curr_clock)
            curr_loc = nxt

        return RoutingChromosome(sequence=seq)

    def _apply_2opt(self, chromosome: RoutingChromosome) -> RoutingChromosome:
        """
        Refinamento Local 2-Opt pós-genético:
        Desata laços cruzados e elimina idas e voltas desnecessárias no mesmo corredor,
        respeitando rigorosamente posições fixadas manualmente.
        """
        best_seq = list(chromosome.sequence)
        n = len(best_seq)
        if n < 4:
            return chromosome

        improved = True
        iterations = 0
        max_iterations = 40

        while improved and iterations < max_iterations:
            improved = False
            iterations += 1

            for i in range(n - 1):
                if i in self.fixed_positions:
                    continue

                for j in range(i + 1, n):
                    has_lock = any(pos in self.fixed_positions for pos in range(i, j + 1))
                    if has_lock:
                        continue

                    # Testa inversão do segmento [i:j+1]
                    new_seq = best_seq[:i] + best_seq[i:j+1][::-1] + best_seq[j+1:]
                    candidate = RoutingChromosome(sequence=new_seq)
                    self.evaluator.evaluate(candidate)

                    if candidate.fitness < chromosome.fitness - 0.01:
                        chromosome = candidate
                        best_seq = new_seq
                        improved = True
                        break
                if improved:
                    break

        return chromosome

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

        # 3. Refinamento Local 2-Opt
        self.best_chromosome = self._apply_2opt(self.best_chromosome)
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
