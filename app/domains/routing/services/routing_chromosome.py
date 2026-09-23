import random
from typing import List, Dict, Any, Optional

class RoutingChromosome:
    def __init__(self, sequence: List[int], fitness: float = float('inf')):
        # sequence é a permutação de índices de entrega [1, 2, ..., N] (onde 0 é o ponto de partida/depósito)
        self.sequence = sequence
        self.fitness = fitness
        self.total_time_minutes: float = 0.0
        self.total_distance_km: float = 0.0
        self.penalties: Dict[str, float] = {}

    @classmethod
    def random_with_locks(cls, num_stops: int, fixed_positions: Dict[int, int]) -> 'RoutingChromosome':
        """
        Gera uma permutação aleatória dos índices 1 a num_stops,
        preservando estritamente os nós fixados em suas respectivas posições.
        
        Args:
            num_stops: Total de paradas (N)
            fixed_positions: Dicionário {posicao_0_indexed: stop_idx_1_to_N}
        """
        all_stops = set(range(1, num_stops + 1))
        locked_stops = set(fixed_positions.values())
        free_stops = list(all_stops - locked_stops)
        random.shuffle(free_stops)

        seq = [0] * num_stops
        # 1. Aloca os nós travados
        for pos, stop_idx in fixed_positions.items():
            if 0 <= pos < num_stops:
                seq[pos] = stop_idx

        # 2. Preenche os espaços livres com os nós sorteados
        free_iter = iter(free_stops)
        for i in range(num_stops):
            if seq[i] == 0:
                seq[i] = next(free_iter)

        return cls(sequence=seq)

    def copy(self) -> 'RoutingChromosome':
        c = RoutingChromosome(sequence=list(self.sequence), fitness=self.fitness)
        c.total_time_minutes = self.total_time_minutes
        c.total_distance_km = self.total_distance_km
        c.penalties = dict(self.penalties)
        return c
