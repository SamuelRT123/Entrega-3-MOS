# verification.py

import pandas as pd
from data_loader import MainConfig
from representation import CVRPSolution
from evaluation import get_representative_fuel_cost_per_km


def export_verification(solution: CVRPSolution, config: MainConfig, filename: str):
    """
    Genera el CSV de verificación en el formato exacto que espera
    base_case_verification.py (sin decimales en enteros).
    """

    # Tomamos el único depósito
    depot = config.depot
    depot_numeric_id = depot.numeric_id

    # El verificador asume que el depósito 1 es CDA
    if depot_numeric_id == 1:
        depot_label = "CDA"
    else:
        depot_label = str(depot_numeric_id)

    fuel_cost_per_km = get_representative_fuel_cost_per_km(config)

    data = []

    for i, route in enumerate(solution.routes):

        # Ignorar rutas triviales
        if len(route) <= 2:
            continue

        route_distance = 0.0
        route_time = 0.0
        demands = []
        seq_labels = []
        route_load = 0  # 🔹 carga total del vehículo en esta ruta

        # =========================
        # Construcción de secuencia
        # =========================
        for node in route:
            if node == depot.code:
                seq_labels.append(depot_label)
            else:
                client = config.clients[node]
                client_label = f"C{client.numeric_id:03d}"
                seq_labels.append(client_label)

                # demanda del cliente como entero
                d_int = int(round(float(client.demand)))
                demands.append(str(d_int))
                route_load += d_int  # acumulamos la carga

        # =========================
        # Distancia y tiempo
        # =========================
        for j in range(len(route) - 1):
            from_node = route[j]
            to_node = route[j + 1]

            d = config.distance_km[(from_node, to_node)]
            t = config.time_h[(from_node, to_node)]

            route_distance += d
            route_time += t

        fuel_cost = fuel_cost_per_km * route_distance

        total_cost = (
            config.C_dist * route_distance
            + config.C_time * route_time
            + fuel_cost
            + config.C_fixed
        )

        # =========================
        # SALIDA FINAL (ENTEROS LIMPIOS)
        # =========================
        row = {
            "VehicleId": f"V{i+1:03}",
            "DepotId": depot_label,
            # 🔹 ahora sí: carga total de la ruta, entero
            "InitialLoad": int(route_load),
            "RouteSequence": "-".join(seq_labels),
            "ClientsServed": int(len(route) - 2),
            "DemandsSatisfied": "-".join(demands),
            "TotalDistance": route_distance,
            "TotalTime": route_time,
            "FuelCost": fuel_cost,
            "TotalCost": total_cost,
        }

        data.append(row)

    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Archivo de verificación guardado en: {filename}")
