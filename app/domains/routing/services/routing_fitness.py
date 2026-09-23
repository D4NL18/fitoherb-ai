from typing import List, Dict, Any
from .routing_chromosome import RoutingChromosome

class RoutingFitnessEvaluator:
    def __init__(
        self,
        durations_matrix_sec: List[List[float]],
        distances_matrix_m: List[List[float]],
        deliveries_data: List[Dict[str, Any]],
        return_to_depot: bool = True,
        fixed_positions: Dict[int, int] = None
    ):
        """
        Avaliador de Fitness para Roteirização de Vendedor Único (Regras P-103, P-104).
        Nó 0 é sempre o Ponto de Partida / Base.
        Nós 1 a N correspondem a deliveries_data[0] a deliveries_data[N-1].
        """
        self.durations = durations_matrix_sec
        self.distances = distances_matrix_m
        self.deliveries = deliveries_data
        self.return_to_depot = return_to_depot
        self.fixed_positions = fixed_positions or {}

    def evaluate(self, chromosome: RoutingChromosome) -> float:
        total_time_sec = 0.0
        total_distance_m = 0.0
        penalties = 0.0

        seq = chromosome.sequence
        n = len(seq)

        if n == 0:
            chromosome.fitness = 0.0
            chromosome.total_time_minutes = 0.0
            chromosome.total_distance_km = 0.0
            return 0.0

        # 1. Defesa em Profundidade: Penalidade severa se violar posição fixa
        for pos, expected_node in self.fixed_positions.items():
            if pos < n and seq[pos] != expected_node:
                penalties += 100000.0

        # 2. Partida do Depósito (0) para o primeiro ponto e percurso das paradas
        curr_node = 0
        accum_time_sec = 0.0
        priority_penalties = 0.0

        for pos, next_node in enumerate(seq):
            leg_time = self.durations[curr_node][next_node]
            total_time_sec += leg_time
            accum_time_sec += leg_time
            total_distance_m += self.distances[curr_node][next_node]
            curr_node = next_node

            # Priorização de Atendimento: Nós 1 a N correspondem a deliveries_data[0..N-1]
            delivery_idx = next_node - 1
            if 0 <= delivery_idx < len(self.deliveries):
                prio = self.deliveries[delivery_idx].get("priority", "REGULAR")
                if prio == "CRITICAL":  # Urgente: prioridade máxima para atendimento imediato
                    priority_penalties += (accum_time_sec * 4.0) + (pos * 10000.0)
                elif prio == "HIGH":    # Alta
                    priority_penalties += (accum_time_sec * 1.5) + (pos * 3000.0)

        # 3. Retorno ao Depósito (se habilitado)
        if self.return_to_depot:
            total_time_sec += self.durations[curr_node][0]
            total_distance_m += self.distances[curr_node][0]

        # 4. Função Custo Multiobjetivo: Tempo viário (peso 1.0) + Distância (peso 0.1) + Travas + Prioridades
        fitness = total_time_sec + ((total_distance_m / 1000.0) * 0.1) + penalties + priority_penalties

        chromosome.fitness = round(fitness, 2)
        chromosome.total_time_minutes = round(total_time_sec / 60.0, 1)
        chromosome.total_distance_km = round(total_distance_m / 1000.0, 1)
        if penalties > 0:
            chromosome.penalties["fixed_order_violation"] = penalties
        if priority_penalties > 0:
            chromosome.penalties["priority_delay"] = priority_penalties

        return chromosome.fitness
