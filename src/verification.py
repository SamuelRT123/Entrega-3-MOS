# verification.py

import pandas as pd
from data_loader import MainConfig
from representation import CVRPSolution
from evaluation import get_representative_fuel_cost_per_km


def export_verification(solution: CVRPSolution, config: MainConfig, filename: str):
    """
    Genera el CSV de verificación con una fila por ruta.
    """
    depot_code = next(iter(config.depots.keys()))
    fuel_cost_per_km = get_representative_fuel_cost_per_km(config)

    data = []

    for i, route in enumerate(solution.routes):
        if len(route) <= 2:
            continue

        route_distance = 0.0
        route_time = 0.0
        load = 0.0
        demands = []

        for j in range(len(route) - 1):
            from_node = route[j]
            to_node = route[j + 1]

            d = config.distance_km[(from_node, to_node)]
            t = config.time_h[(from_node, to_node)]
            route_distance += d
            route_time += t

        for node in route[1:-1]:
            if node in config.clients:
                c = config.clients[node]
                load += c.demand
                demands.append(str(c.demand))

        fuel_cost = fuel_cost_per_km * route_distance
        total_cost = (
            config.C_dist * route_distance
            + config.C_time * route_time
            + fuel_cost
            + config.C_fixed  # asignamos costo fijo por vehículo usado
        )

        row = {
            "VehicleId": f"V{i+1:03}",
            "DepotId": depot_code,
            "InitialLoad": 0,
            "RouteSequence": "-".join(map(str, route)),
            "ClientsServed": len(route) - 2,
            "DemandsSatisfied": "-".join(demands),
            "TotalDistance": route_distance,
            "TotalTime": route_time,
            "FuelCost": fuel_cost,
            "TotalCost": total_cost,
        }
        data.append(row)

    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
