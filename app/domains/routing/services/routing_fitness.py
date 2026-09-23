import math
from typing import List, Dict, Any, Optional, Tuple
from .routing_chromosome import RoutingChromosome
from app.domains.routing.traffic_model import TrafficPredictor

class RoutingFitnessEvaluator:
    def __init__(
        self,
        durations_matrix_sec: List[List[float]],
        distances_matrix_m: List[List[float]],
        deliveries_data: List[Dict[str, Any]],
        return_to_depot: bool = True,
        fixed_positions: Dict[int, int] = None,
        departure_time_minutes: Optional[float] = None,
        default_service_minutes: int = 20,
        base_city: Optional[str] = None,
        points_cities: List[str] = None,
        coordinates: List[Tuple[float, float]] = None
    ):
        """
        Avaliador de Fitness TDVRP (Time-Dependent Vehicle Routing Problem)
        com Previsão de Trânsito Dinâmica por Porte de Cidade, Dwell Time e Anti-Backtracking.
        """
        self.durations = durations_matrix_sec
        self.distances = distances_matrix_m
        self.deliveries = deliveries_data
        self.return_to_depot = return_to_depot
        self.fixed_positions = fixed_positions or {}
        self.departure_time_minutes = departure_time_minutes
        self.default_service_minutes = default_service_minutes
        self.base_city = base_city
        self.points_cities = points_cities or ([""] * len(durations_matrix_sec))
        self.coordinates = coordinates or []

    def evaluate(self, chromosome: RoutingChromosome) -> float:
        seq = chromosome.sequence
        n = len(seq)

        if n == 0:
            chromosome.fitness = 0.0
            chromosome.total_time_minutes = 0.0
            chromosome.total_distance_km = 0.0
            return 0.0

        penalties = 0.0
        priority_penalties = 0.0
        overshoot_penalties = 0.0

        # 1. Defesa em Profundidade: Posições fixadas manualmente
        for pos, expected_node in self.fixed_positions.items():
            if pos < n and seq[pos] != expected_node:
                penalties += 100000.0

        curr_node = 0
        curr_clock_min = self.departure_time_minutes
        total_transit_sec = 0.0
        total_service_min = 0.0
        total_distance_m = 0.0
        peak_legs = 0

        # Conjunto de nós ainda não visitados para cálculo de anti-overshoot
        unvisited = set(seq)

        for pos, next_node in enumerate(seq):
            unvisited.discard(next_node)
            leg_dist_m = self.distances[curr_node][next_node]
            leg_dist_km = leg_dist_m / 1000.0
            base_duration_sec = self.durations[curr_node][next_node]

            # Cidades de origem e destino
            orig_city = self.points_cities[curr_node] if curr_node < len(self.points_cities) else self.base_city
            dest_city = self.points_cities[next_node] if next_node < len(self.points_cities) else self.base_city

            # Previsão de Trânsito Dinâmica baseada no relógio atual e tamanho da cidade
            traffic_k, traffic_cond = TrafficPredictor.get_traffic_multiplier(
                time_minutes_from_midnight=curr_clock_min,
                distance_km=leg_dist_km,
                origin_city=orig_city,
                dest_city=dest_city,
                base_city=self.base_city
            )

            if "PICO" in traffic_cond:
                peak_legs += 1

            adjusted_leg_sec = base_duration_sec * traffic_k
            total_transit_sec += adjusted_leg_sec
            total_distance_m += leg_dist_m

            # Avança o relógio com o tempo de deslocamento (se agendamento ativo)
            if curr_clock_min is not None:
                curr_clock_min += (adjusted_leg_sec / 60.0)

            # 2. Anti-Overshoot / Anti-Backtracking em Corredores:
            # Verifica se o salto de curr_node -> next_node 'passou direto' por algum nó não visitado
            # que estava no mesmo corredor e mais próximo
            if self.coordinates and len(self.coordinates) > max(curr_node, next_node):
                p_curr = self.coordinates[curr_node]
                p_next = self.coordinates[next_node]
                v_x = p_next[0] - p_curr[0]
                v_y = p_next[1] - p_curr[1]
                v_len = math.hypot(v_x, v_y)

                if v_len > 0.05: # acima de ~5 km
                    for cand_node in unvisited:
                        # Se cand_node não tem trava de ordem específica posterior
                        if cand_node not in self.fixed_positions.values():
                            p_cand = self.coordinates[cand_node]
                            c_x = p_cand[0] - p_curr[0]
                            c_y = p_cand[1] - p_curr[1]
                            c_len = math.hypot(c_x, c_y)

                            if 0.02 < c_len < v_len:
                                dot = (v_x * c_x + v_y * c_y) / (v_len * c_len)
                                # Se o ponto candidato está praticamente alinhado no caminho à frente (cos > 0.85)
                                if dot > 0.85:
                                    # Penalidade por passar direto e ter que voltar depois
                                    overshoot_penalties += 3500.0

            # 3. Tempo de Atendimento (Dwell Time)
            delivery_idx = next_node - 1
            if 0 <= delivery_idx < len(self.deliveries):
                deliv = self.deliveries[delivery_idx]
                service_min = deliv.get("service_duration_minutes") or self.default_service_minutes
                total_service_min += service_min
                if curr_clock_min is not None:
                    curr_clock_min += service_min

                # Priorização de Atendimento
                prio = deliv.get("priority", "REGULAR")
                if prio == "CRITICAL":
                    # Penalidade pesada por postergar clientes urgentes
                    priority_penalties += (total_transit_sec * 4.0) + (pos * 15000.0)
                elif prio == "HIGH":
                    priority_penalties += (total_transit_sec * 1.5) + (pos * 4000.0)

            curr_node = next_node

        # 4. Retorno ao Depósito / Base
        if self.return_to_depot:
            leg_dist_m = self.distances[curr_node][0]
            leg_dist_km = leg_dist_m / 1000.0
            base_duration_sec = self.durations[curr_node][0]

            orig_city = self.points_cities[curr_node] if curr_node < len(self.points_cities) else self.base_city
            dest_city = self.base_city

            traffic_k, traffic_cond = TrafficPredictor.get_traffic_multiplier(
                time_minutes_from_midnight=curr_clock_min,
                distance_km=leg_dist_km,
                origin_city=orig_city,
                dest_city=dest_city,
                base_city=self.base_city
            )
            adjusted_leg_sec = base_duration_sec * traffic_k
            total_transit_sec += adjusted_leg_sec
            total_distance_m += leg_dist_m
            if curr_clock_min is not None:
                curr_clock_min += (adjusted_leg_sec / 60.0)

        # 5. Função Objetivo TDVRP Multiobjetivo:
        # Tempo viário com trânsito real + Distância ponderada + Penalidades + Anti-Overshoot
        fitness = (
            total_transit_sec +
            ((total_distance_m / 1000.0) * 0.15) +
            penalties +
            priority_penalties +
            overshoot_penalties
        )

        chromosome.fitness = round(fitness, 2)
        chromosome.total_time_minutes = round(total_transit_sec / 60.0, 1)
        chromosome.total_distance_km = round(total_distance_m / 1000.0, 1)
        chromosome.penalties = {}
        if penalties > 0:
            chromosome.penalties["fixed_order_violation"] = penalties
        if priority_penalties > 0:
            chromosome.penalties["priority_delay"] = priority_penalties
        if overshoot_penalties > 0:
            chromosome.penalties["corridor_overshoot"] = overshoot_penalties

        return chromosome.fitness
