from dataclasses import dataclass
from typing import Dict, Tuple
import os
import math

import pandas as pd


# Ruta al caso base (ajusta el nombre de la carpeta si es distinto)
BASE_DEPOT_FOLDER = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "Proyecto_Caso_Base")
)


# =========================
# Dataclasses del problema
# =========================

@dataclass
class Depot:
    numeric_id: int
    code: str
    lon: float
    lat: float
    capacity: float


@dataclass
class Vehicle:
    numeric_id: int
    code: str
    vehicle_type: str
    capacity: float
    max_range_km: float
    fuel_cost_per_km: float


@dataclass
class Client:
    numeric_id: int
    code: str
    lat: float
    lon: float
    demand: float
    max_vehicle_type: str


@dataclass
class MainConfig:
    C_fixed: float
    C_dist: float
    C_time: float
    fuel_price: float

    vehicles: Dict[str, Vehicle] = None
    clients: Dict[str, Client] = None
    depots: Dict[str, Depot] = None

    distance_km: Dict[Tuple[str, str], float] = None
    time_h: Dict[Tuple[str, str], float] = None

    big_m_veh: float = 1e5
    big_m_mtz: float = 1e5


# =========================
# Parámetros
# =========================

def load_parameters_urban(path: str):
    df = pd.read_csv(path)

    # Normalizar nombres de columnas
    df.columns = [c.strip().lower() for c in df.columns]

    param_col_candidates = ["parameter", "param", "nombre", "name"]
    value_col_candidates = ["value", "valor", "val"]

    param_col = None
    value_col = None

    for c in param_col_candidates:
        if c in df.columns:
            param_col = c
            break

    for c in value_col_candidates:
        if c in df.columns:
            value_col = c
            break

    if param_col is None or value_col is None:
        raise ValueError(
            f"No se encontraron columnas de parámetro/valor reconocibles en {path}. "
            f"Columnas disponibles: {list(df.columns)}"
        )

    df[param_col] = df[param_col].astype(str).str.strip()

    def get_val(param_name: str) -> float:
        mask = df[param_col].str.lower() == param_name.strip().lower()
        if not mask.any():
            available = df[param_col].unique().tolist()
            raise ValueError(
                f"No se encontró el parámetro '{param_name}' en {path}.\n"
                f"Parámetros disponibles: {available}"
            )
        return float(df.loc[mask, value_col].iloc[0])

    C_fixed = get_val("C_fixed")
    C_dist = get_val("C_dist")
    C_time = get_val("C_time")
    fuel_price = get_val("fuel_price")

    eff_small_min = get_val("fuel_efficiency_van_small_min")
    eff_small_max = get_val("fuel_efficiency_van_small_max")
    eff_med_min = get_val("fuel_efficiency_van_medium_min")
    eff_med_max = get_val("fuel_efficiency_van_medium_max")
    eff_truck_min = get_val("fuel_efficiency_truck_light_min")
    eff_truck_max = get_val("fuel_efficiency_truck_light_max")

    eff_type = {
        "small van": 0.5 * (eff_small_min + eff_small_max),
        "medium van": 0.5 * (eff_med_min + eff_med_max),
        "light truck": 0.5 * (eff_truck_min + eff_truck_max),
    }

    return C_fixed, C_dist, C_time, fuel_price, eff_type


# =========================
# Vehículos
# =========================

def load_vehicles(path: str, eff_type: Dict[str, float], fuel_price: float) -> Dict[str, Vehicle]:
    df = pd.read_csv(path)

    if "StandardizedID" not in df.columns:
        raise ValueError(f"El archivo {path} no tiene columna 'StandardizedID'. Columnas: {list(df.columns)}")

    df["StandardizedID"] = df["StandardizedID"].astype(str).str.strip()

    if eff_type and len(eff_type) > 0:
        default_eff_km_per_gal = sum(eff_type.values()) / len(eff_type)
    else:
        default_eff_km_per_gal = 10.0  # fallback

    fuel_cost_per_km_default = fuel_price / default_eff_km_per_gal

    vehicles: Dict[str, Vehicle] = {}

    for _, row in df.iterrows():
        numeric_id = int(row["VehicleID"])
        code = str(row["StandardizedID"])

        capacity = float(row["Capacity"])
        max_range_km = float(row["Range"])

        vehicles[code] = Vehicle(
            numeric_id=numeric_id,
            code=code,
            vehicle_type="generic",
            capacity=capacity,
            max_range_km=max_range_km,
            fuel_cost_per_km=fuel_cost_per_km_default,
        )

    return vehicles


# =========================
# Clientes
# =========================

def load_clients(path: str) -> Dict[str, Client]:
    df = pd.read_csv(path)

    if "StandardizedID" not in df.columns:
        raise ValueError(
            f"El archivo {path} no tiene columna 'StandardizedID'. "
            f"Columnas disponibles: {list(df.columns)}"
        )

    df["StandardizedID"] = df["StandardizedID"].astype(str).str.strip().str.lower()

    has_vehicle_restr = "VehicleSizeRestriction" in df.columns
    if has_vehicle_restr:
        df["VehicleSizeRestriction"] = (
            df["VehicleSizeRestriction"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

    clients: Dict[str, Client] = {}
    for _, row in df.iterrows():
        numeric_id = int(row["ClientID"])
        code = str(row["StandardizedID"])
        lat = float(row["Latitude"])
        lon = float(row["Longitude"])
        demand = float(row["Demand"])

        if has_vehicle_restr:
            max_vehicle_type = str(row["VehicleSizeRestriction"])
        else:
            max_vehicle_type = "any"

        clients[code] = Client(
            numeric_id=numeric_id,
            code=code,
            lat=lat,
            lon=lon,
            demand=demand,
            max_vehicle_type=max_vehicle_type,
        )

    return clients


# =========================
# Depósitos (solo caso base)
# =========================

def load_depots(path: str) -> Dict[str, Depot]:
    df = pd.read_csv(path)

    df.columns = [c.strip() for c in df.columns]

    required = ["DepotID", "StandardizedID", "Latitude", "Longitude"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(
            f"El archivo {path} no tiene las columnas requeridas {required}. "
            f"Columnas disponibles: {list(df.columns)}"
        )

    has_capacity = "Capacity" in df.columns

    depots: Dict[str, Depot] = {}
    for _, row in df.iterrows():
        numeric_id = int(row["DepotID"])
        code = str(row["StandardizedID"]).strip().lower()
        lat = float(row["Latitude"])
        lon = float(row["Longitude"])

        if has_capacity:
            capacity = float(row["Capacity"])
        else:
            capacity = 1e9  # dummy, no se usa

        depots[code] = Depot(
            numeric_id=numeric_id,
            code=code,
            lat=lat,
            lon=lon,
            capacity=capacity,
        )

    return depots


# =========================
# Distancias Haversine
# =========================

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def build_distance_and_time(config: MainConfig, avg_speed_kmh: float = 30.0):
    distance_km: Dict[Tuple[str, str], float] = {}
    time_h: Dict[Tuple[str, str], float] = {}

    nodes_coords: Dict[str, Tuple[float, float]] = {}

    for code, c in config.clients.items():
        nodes_coords[code] = (c.lat, c.lon)

    for code, d in config.depots.items():
        nodes_coords[code] = (d.lat, d.lon)

    codes = list(nodes_coords.keys())

    for i in codes:
        lat_i, lon_i = nodes_coords[i]
        for j in codes:
            lat_j, lon_j = nodes_coords[j]
            if i == j:
                dist = 0.0
            else:
                dist = haversine_km(lat_i, lon_i, lat_j, lon_j)
            distance_km[(i, j)] = dist
            time_h[(i, j)] = dist / avg_speed_kmh if avg_speed_kmh > 0 else 0.0

    config.distance_km = distance_km
    config.time_h = time_h


# =========================
# Carga completa de instancia
# =========================

def load_instance(folder_path: str) -> MainConfig:
    folder_path = os.path.abspath(folder_path)
    files = os.listdir(folder_path)
    param_file = [f for f in files if f.startswith("parameters")][0]
    param_path = os.path.join(folder_path, param_file)

    C_fixed, C_dist, C_time, fuel_price, eff_type = load_parameters_urban(param_path)

    vehicles = load_vehicles(os.path.join(folder_path, "vehicles.csv"), eff_type, fuel_price)
    clients = load_clients(os.path.join(folder_path, "clients.csv"))

    depots_path = os.path.join(BASE_DEPOT_FOLDER, "depots.csv")
    if not os.path.exists(depots_path):
        raise FileNotFoundError(
            f"No se encontró depots.csv en la ruta de caso base: {depots_path}"
        )

    depots = load_depots(depots_path)

    config = MainConfig(
        C_fixed=C_fixed,
        C_dist=C_dist,
        C_time=C_time,
        fuel_price=fuel_price,
        vehicles=vehicles,
        clients=clients,
        depots=depots,
    )

    build_distance_and_time(config)

    return config
