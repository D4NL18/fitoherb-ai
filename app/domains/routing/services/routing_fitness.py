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

    def _calculate_overshoot_penalty(
        self,
        curr_node: int,
        next_node: int,
        unvisited: set,
        curr_clock_min: Optional[float]
    ) -> float:
        if not self.coordinates or len(self.coordinates) <= max(curr_node, next_node):
            return 0.0

        p_curr = self.coordinates[curr_node]
        p_next = self.coordinates[next_node]
        v_x = p_next[0] - p_curr[0]
        v_y = p_next[1] - p_curr[1]
        v_len = math.hypot(v_x, v_y)
        if v_len <= 0.05:
            return 0.0

        overshoot = 0.0
        for cand_node in unvisited:
            if cand_node in self.fixed_positions.values():
                continue
            cand_deliv = self.deliveries[cand_node - 1] if (cand_node - 1) < len(self.deliveries) else {}
            cand_target_str = cand_deliv.get("target_arrival_time")
            if cand_target_str and curr_clock_min is not None:
                cand_target_min = TrafficPredictor.parse_time_str(cand_target_str)
                if cand_target_min is not None and cand_target_min > (curr_clock_min + 30.0):
                    continue

            p_cand = self.coordinates[cand_node]
            c_x = p_cand[0] - p_curr[0]
            c_y = p_cand[1] - p_curr[1]
            c_len = math.hypot(c_x, c_y)
            if 0.02 < c_len < v_len:
                dot = (v_x * c_x + v_y * c_y) / (v_len * c_len)
                if dot > 0.85:
                    overshoot += 3500.0

        return overshoot

    def _evaluate_arrival_window(
        self,
        target_time_str: Optional[str],
        curr_clock_min: Optional[float]
    ) -> tuple[float, float, Optional[float]]:
        """
        Calcula penalidades de atraso ou adiantamento excessivo conforme Regra P-106.
        Retorna (delay_penalty, early_penalty, updated_clock_min).
        """
        if curr_clock_min is None or not target_time_str:
            return 0.0, 0.0, curr_clock_min

        target_min = TrafficPredictor.parse_time_str(target_time_str)
        if target_min is None:
            return 0.0, 0.0, curr_clock_min

        if curr_clock_min > target_min:
            delay_min = curr_clock_min - target_min
            return 100000.0 + (delay_min * 20000.0), 0.0, curr_clock_min

        if curr_clock_min < target_min:
            early_min = target_min - curr_clock_min
            courtesy_margin = 15.0
            early_penalty = 0.0
            if early_min > courtesy_margin:
                excess_early = early_min - courtesy_margin
                early_penalty = 2000.0 + (excess_early * 400.0)
            return 0.0, early_penalty, float(target_min)

        return 0.0, 0.0, curr_clock_min

    @staticmethod
    def _evaluate_priority_penalties(priority: str, pos: int, total_transit_sec: float) -> float:
        if priority == "CRITICAL":
            return (total_transit_sec * 4.0) + (pos * 15000.0)
        elif priority == "HIGH":
            return (total_transit_sec * 1.5) + (pos * 4000.0)
        return 0.0

    def _calculate_leg_transit(
        self,
        curr_node: int,
        next_node: int,
        curr_clock_min: Optional[float]
    ) -> tuple[float, float]:
        leg_dist_m = self.distances[curr_node][next_node]
        leg_dist_km = leg_dist_m / 1000.0
        base_duration_sec = self.durations[curr_node][next_node]

        orig_city = self.points_cities[curr_node] if curr_node < len(self.points_cities) else self.base_city
        dest_city = self.points_cities[next_node] if next_node < len(self.points_cities) else self.base_city

        traffic_k, _ = TrafficPredictor.get_traffic_multiplier(
            time_minutes_from_midnight=curr_clock_min,
            distance_km=leg_dist_km,
            origin_city=orig_city,
            dest_city=dest_city,
            base_city=self.base_city
        )
        adjusted_leg_sec = base_duration_sec * traffic_k
        return adjusted_leg_sec, leg_dist_m

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
        early_arrival_penalties = 0.0

        # 1. Defesa em Profundidade: Posições fixadas manualmente
        for pos, expected_node in self.fixed_positions.items():
            if pos < n and seq[pos] != expected_node:
                penalties += 100000.0

        curr_node = 0
        curr_clock_min = self.departure_time_minutes
        total_transit_sec = 0.0
        total_distance_m = 0.0

        unvisited = set(seq)

        for pos, next_node in enumerate(seq):
            unvisited.discard(next_node)
            adjusted_leg_sec, leg_dist_m = self._calculate_leg_transit(curr_node, next_node, curr_clock_min)
            total_transit_sec += adjusted_leg_sec
            total_distance_m += leg_dist_m

            if curr_clock_min is not None:
                curr_clock_min += (adjusted_leg_sec / 60.0)

            # 2. Anti-Overshoot / Anti-Backtracking em Corredores
            overshoot_penalties += self._calculate_overshoot_penalty(
                curr_node, next_node, unvisited, curr_clock_min
            )

            # 3. Tempo de Atendimento e Horário Marcado (Regra P-106)
            delivery_idx = next_node - 1
            if 0 <= delivery_idx < len(self.deliveries):
                deliv = self.deliveries[delivery_idx]
                target_str = deliv.get("target_arrival_time")

                d_pen, e_pen, curr_clock_min = self._evaluate_arrival_window(target_str, curr_clock_min)
                penalties += d_pen
                early_arrival_penalties += e_pen

                service_min = deliv.get("service_duration_minutes") or self.default_service_minutes
                if curr_clock_min is not None:
                    curr_clock_min += service_min

                prio = deliv.get("priority", "REGULAR")
                priority_penalties += self._evaluate_priority_penalties(prio, pos, total_transit_sec)

            curr_node = next_node

        # 4. Retorno ao Depósito / Base
        if self.return_to_depot:
            adjusted_leg_sec, leg_dist_m = self._calculate_leg_transit(curr_node, 0, curr_clock_min)
            total_transit_sec += adjusted_leg_sec
            total_distance_m += leg_dist_m
            if curr_clock_min is not None:
                curr_clock_min += (adjusted_leg_sec / 60.0)

        # 5. Função Objetivo TDVRP Multiobjetivo
        fitness = (
            total_transit_sec +
            ((total_distance_m / 1000.0) * 0.15) +
            penalties +
            priority_penalties +
            overshoot_penalties +
            early_arrival_penalties
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
        if early_arrival_penalties > 0:
            chromosome.penalties["excessive_early_arrival"] = early_arrival_penalties

        return chromosome.fitness
