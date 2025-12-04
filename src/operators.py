# operators.py

import random
from typing import List
from representation import CVRPSolution
from data_loader import MainConfig
from evaluation import (
    get_representative_capacity,
    get_representative_max_range_km,
    evaluate_solution,
)

# ============================================================
# Extraer solo clientes (sin depósito)
# ============================================================

def _flatten_clients(solution: CVRPSolution, config: MainConfig) -> List[str]:
    clients = []
    for route in solution.routes:
        for node in route:
            if node in config.clients:
                clients.append(node)
    return clients


# ============================================================
# Construcción de rutas respetando CAPACIDAD y RANGO
# ============================================================

def _build_routes_from_sequence(
    seq: List[str],
    config: MainConfig,
    depot_code: str
) -> CVRPSolution:

    Q = get_representative_capacity(config)
    R = get_representative_max_range_km(config)

    routes = []
    current_route = [depot_code]
    current_load = 0.0
    current_distance = 0.0

    for client_code in seq:
        demand = config.clients[client_code].demand
        last_node = current_route[-1]

        d_last_depot = config.distance_km[(last_node, depot_code)]
        d_last_client = config.distance_km[(last_node, client_code)]
        d_client_depot = config.distance_km[(client_code, depot_code)]

        extra_distance = d_last_client + d_client_depot - d_last_depot

        can_add_by_capacity = (current_load + demand <= Q) or (len(current_route) == 1)
        can_add_by_range = (current_distance + extra_distance <= R) or (len(current_route) == 1)

        if can_add_by_capacity and can_add_by_range:
            current_route.append(client_code)
            current_load += demand
            current_distance += extra_distance
        else:
            # cierro ruta actual
            current_route.append(depot_code)
            routes.append(current_route)

            # abro nueva ruta con ese cliente
            current_route = [depot_code, client_code]
            current_load = demand
            current_distance = (
                config.distance_km[(depot_code, client_code)]
                + config.distance_km[(client_code, depot_code)]
            )

    # cierro última ruta
    current_route.append(depot_code)
    routes.append(current_route)

    return CVRPSolution(routes)


# ============================================================
# CRUCE (OX)
# ============================================================

def crossover(
    p1: CVRPSolution,
    p2: CVRPSolution,
    config: MainConfig,
    depot_code: str
) -> CVRPSolution:

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


# ============================================================
# MUTACIÓN (swap)
# ============================================================

def mutate(
    solution: CVRPSolution,
    config: MainConfig,
    depot_code: str,
    mutation_rate: float = 0.2
) -> CVRPSolution:

    seq = _flatten_clients(solution, config)
    n = len(seq)

    if n >= 2 and random.random() < mutation_rate:
        i, j = random.sample(range(n), 2)
        seq[i], seq[j] = seq[j], seq[i]

    return _build_routes_from_sequence(seq, config, depot_code)


# ============================================================
# REPARACIÓN
# ============================================================

def repair(
    solution: CVRPSolution,
    config: MainConfig,
    depot_code: str,
) -> CVRPSolution:
    """
    Repara/evalúa la solución. En este diseño, la factibilidad de capacidad
    y rango se controla al construir rutas; aquí nos aseguramos de que
    la solución tenga su costo actualizado.
    """
    evaluate_solution(solution, config)
    return solution
