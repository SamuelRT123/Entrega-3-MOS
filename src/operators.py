# operators.py

import random
from typing import List
from representation import CVRPSolution
from data_loader import MainConfig
from evaluation import get_representative_capacity, evaluate_solution


def _flatten_clients(solution: CVRPSolution, config: MainConfig) -> List[str]:
    """
    Devuelve la secuencia plana de clientes en la solución (sin depósito).
    """
    clients = []
    for route in solution.routes:
        for node in route:
            if node in config.clients:
                clients.append(node)
    return clients


def _build_routes_from_sequence(
    seq: List[str],
    config: MainConfig,
    depot_code: str
) -> CVRPSolution:
    """
    Construye rutas [depot, ..., depot] desde una permutación de clientes,
    respetando capacidad representativa Q.
    """
    Q = get_representative_capacity(config)

    routes = []
    current_route = [depot_code]
    current_load = 0.0

    for client_code in seq:
        demand = config.clients[client_code].demand

        if current_load + demand <= Q or len(current_route) == 1:
            current_route.append(client_code)
            current_load += demand
        else:
            current_route.append(depot_code)
            routes.append(current_route)

            current_route = [depot_code, client_code]
            current_load = demand

    current_route.append(depot_code)
    routes.append(current_route)

    return CVRPSolution(routes)


def crossover(
    p1: CVRPSolution,
    p2: CVRPSolution,
    config: MainConfig,
    depot_code: str
) -> CVRPSolution:
    """
    Cruce tipo OX en la secuencia plana de clientes.
    """
    seq1 = _flatten_clients(p1, config)
    seq2 = _flatten_clients(p2, config)

    n = len(seq1)
    if n < 2:
        return p1.copy()

    a, b = sorted(random.sample(range(n), 2))

    child_seq = [None] * n
    child_seq[a:b + 1] = seq1[a:b + 1]
    used = set(seq1[a:b + 1])

    pos = (b + 1) % n
    for c in seq2:
        if c in used:
            continue
        while child_seq[pos] is not None:
            pos = (pos + 1) % n
        child_seq[pos] = c

    return _build_routes_from_sequence(child_seq, config, depot_code)


def mutate(
    solution: CVRPSolution,
    config: MainConfig,
    depot_code: str,
    mutation_rate: float = 0.2
) -> CVRPSolution:
    """
    Mutación por swap de dos clientes.
    """
    seq = _flatten_clients(solution, config)
    n = len(seq)

    if n >= 2 and random.random() < mutation_rate:
        i, j = random.sample(range(n), 2)
        seq[i], seq[j] = seq[j], seq[i]

    return _build_routes_from_sequence(seq, config, depot_code)


def repair(
    solution: CVRPSolution,
    config: MainConfig,
    depot_code: str
) -> CVRPSolution:
    """
    La reconstrucción ya respeta capacidad, aquí solo re-evaluamos.
    """
    evaluate_solution(solution, config)
    return solution
