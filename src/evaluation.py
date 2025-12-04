# Función objetivo y métricas de evaluación para CVRP
from data_loader import MainConfig
from representation import CVRPSolution


def get_representative_capacity(config: MainConfig) -> float:
    """
    Capacidad 'Q' usada en el GA.
    Para respetar las restricciones del problema y del verificador,
    usamos la capacidad mínima entre todos los vehículos disponibles.
    """
    capacities = [v.capacity for v in config.vehicles.values()]
    return min(capacities)


def get_representative_fuel_cost_per_km(config: MainConfig) -> float:
    costs = [v.fuel_cost_per_km for v in config.vehicles.values()]
    return sum(costs) / len(costs)


def get_representative_max_range_km(config: MainConfig) -> float:
    """
    Rango máximo representativo de la flota (km por vehículo).
    """
    ranges = [v.max_range_km for v in config.vehicles.values()]
    return max(set(ranges), key=ranges.count)


def evaluate_solution(solution: CVRPSolution, config: MainConfig) -> float:
    """
    Z = sum_v( C_fixed * y_v ) + sum_v( C_dist * d_v )
        + sum_v( C_time * t_v ) + C_fuel
    + penalizaciones (capacidad y rango).
    """

    depot_code = config.depot.code

    Q = get_representative_capacity(config)
    fuel_cost_per_km = get_representative_fuel_cost_per_km(config)
    R = get_representative_max_range_km(config)   # 🔹 nuevo: rango máximo

    total_fixed_cost = 0.0
    total_dist_cost = 0.0
    total_time_cost = 0.0
    total_fuel_cost = 0.0
    penalty_cost = 0.0

    solution.is_feasible = True

    for route in solution.routes:
        normalized_route = [
            depot_code if node == 0 else node for node in route
        ]

        if len(normalized_route) <= 2:
            continue

        # y_v = 1 → vehículo usado
        total_fixed_cost += config.C_fixed

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

        # Carga total
        for node in normalized_route[1:-1]:
            if node in config.clients:
                client = config.clients[node]
                load += client.demand

        # 🔹 Restricción de capacidad
        if load > Q:
            solution.is_feasible = False
            overflow = load - Q
            penalty_cost += config.big_m_veh * overflow

        # 🔹 Restricción de rango (distancia total de la ruta no puede pasar R)
        if route_distance > R:
            solution.is_feasible = False
            overflow_d = route_distance - R
            penalty_cost += config.big_m_veh * overflow_d

        # Costos variables de la ruta
        total_dist_cost += config.C_dist * route_distance
        total_time_cost += config.C_time * route_time
        total_fuel_cost += fuel_cost_per_km * route_distance

    total_cost = (
        total_fixed_cost
        + total_dist_cost
        + total_time_cost
        + total_fuel_cost
        + penalty_cost
    )

    solution.cost = total_cost
    return total_cost
