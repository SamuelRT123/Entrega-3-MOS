# evaluation.py

from data_loader import MainConfig
from representation import CVRPSolution


def get_representative_capacity(config: MainConfig) -> float:
    capacities = [v.capacity for v in config.vehicles.values()]
    return max(set(capacities), key=capacities.count)


def get_representative_fuel_cost_per_km(config: MainConfig) -> float:
    costs = [v.fuel_cost_per_km for v in config.vehicles.values()]
    return sum(costs) / len(costs)


def evaluate_solution(solution: CVRPSolution, config: MainConfig) -> float:
    """
    Evalúa una solución CVRP usando:
    - Costo fijo por vehículo usado
    - Costo por distancia
    - Costo por tiempo
    - Costo por combustible
    y penaliza violación de capacidad.
    """
    depot_code = next(iter(config.depots.keys()))

    Q = get_representative_capacity(config)
    fuel_cost_per_km = get_representative_fuel_cost_per_km(config)

    total_cost = 0.0
    solution.is_feasible = True

    used_vehicles = 0

    for route in solution.routes:
        normalized_route = [
            depot_code if node == 0 else node for node in route
        ]

        if len(normalized_route) <= 2:
            continue

        used_vehicles += 1

        route_distance = 0.0
        route_time = 0.0
        load = 0.0

        for i in range(len(normalized_route) - 1):
            from_node = normalized_route[i]
            to_node = normalized_route[i + 1]

            d = config.distance_km[(from_node, to_node)]
            t = config.time_h[(from_node, to_node)]
            route_distance += d
            route_time += t

        for node in normalized_route[1:-1]:
            if node in config.clients:
                client = config.clients[node]
                load += client.demand

        if load > Q:
            solution.is_feasible = False
            overflow = load - Q
            total_cost += config.big_m_veh * overflow

        variable_cost = (
            config.C_dist * route_distance
            + config.C_time * route_time
            + fuel_cost_per_km * route_distance
        )

        total_cost += variable_cost

    total_cost += used_vehicles * config.C_fixed

    solution.cost = total_cost
    return total_cost
