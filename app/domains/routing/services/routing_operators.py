import random
from typing import List, Tuple, Dict, Set
from .routing_chromosome import RoutingChromosome

class RoutingOperators:

    @staticmethod
    def tournament_selection(population: List[RoutingChromosome], k: int = 3) -> RoutingChromosome:
        """
        Torneio para minimização de custo: seleciona k indivíduos e retorna o de menor fitness.
        """
        candidates = random.sample(population, min(k, len(population)))
        return min(candidates, key=lambda ind: ind.fitness)

    @staticmethod
    def locked_order_crossover(
        p1: RoutingChromosome, 
        p2: RoutingChromosome, 
        fixed_positions: Dict[int, int],
        pc: float = 0.85
    ) -> Tuple[RoutingChromosome, RoutingChromosome]:
        """
        Locked Order Crossover (Locked-OX - Regra P-104):
        Preserva as posições fixadas intactas e executa Order Crossover (OX)
        estritamente sobre a subsequência de posições desbloqueadas.
        """
        n = len(p1.sequence)
        unlocked_indices = [i for i in range(n) if i not in fixed_positions]

        # Se houver menos de 2 posições livres para recombinar ou sorteio falhar, retorna clones
        if len(unlocked_indices) < 2 or random.random() > pc:
            return p1.copy(), p2.copy()

        # Extrai os nós livres na ordem de cada progenitor
        s1 = [p1.sequence[i] for i in unlocked_indices]
        s2 = [p2.sequence[i] for i in unlocked_indices]
        m = len(s1)

        if m <= 2:
            cut1, cut2 = 0, 1
        else:
            cut1, cut2 = sorted(random.sample(range(m), 2))

        def _ox_sub(parent_a: List[int], parent_b: List[int]) -> List[int]:
            child = [None] * m
            # Copia o bloco central
            child[cut1:cut2+1] = parent_a[cut1:cut2+1]
            copied = set(child[cut1:cut2+1])

            # Preenche o restante circularmente a partir de parent_b
            b_order = parent_b[cut2+1:] + parent_b[:cut2+1]
            remaining = [val for val in b_order if val not in copied]

            idx = (cut2 + 1) % m
            for val in remaining:
                child[idx] = val
                idx = (idx + 1) % m
            return child

        c1_sub = _ox_sub(s1, s2)
        c2_sub = _ox_sub(s2, s1)

        # Reconstrói os cromossomos filhos reinserindo os nós fixos intactos
        def _reconstruct(sub: List[int]) -> RoutingChromosome:
            seq = [0] * n
            for pos, stop_idx in fixed_positions.items():
                seq[pos] = stop_idx
            for pos, val in zip(unlocked_indices, sub):
                seq[pos] = val
            return RoutingChromosome(sequence=seq)

        return _reconstruct(c1_sub), _reconstruct(c2_sub)

    @staticmethod
    def locked_mutate(
        chromosome: RoutingChromosome, 
        fixed_positions: Dict[int, int],
        pm: float = 0.20
    ) -> RoutingChromosome:
        """
        Mutação com Trava de Ordem (Locked Mutation - Regra P-104):
        Aplica Inversão (2-opt) ou Troca (Swap) sorteando índices
        exclusivamente dentre as posições livres (desbloqueadas).
        """
        n = len(chromosome.sequence)
        unlocked_indices = [i for i in range(n) if i not in fixed_positions]

        if len(unlocked_indices) < 2 or random.random() > pm:
            return chromosome

        seq = list(chromosome.sequence)

        if random.random() < 0.6:
            # 2-opt Inversion sobre posições livres
            idx_a, idx_b = sorted(random.sample(range(len(unlocked_indices)), 2))
            sub_positions = unlocked_indices[idx_a:idx_b+1]
            sub_values = [seq[p] for p in sub_positions]
            sub_values.reverse()
            for p, v in zip(sub_positions, sub_values):
                seq[p] = v
        else:
            # Swap entre duas posições livres
            pos1, pos2 = random.sample(unlocked_indices, 2)
            seq[pos1], seq[pos2] = seq[pos2], seq[pos1]

        return RoutingChromosome(sequence=seq)
