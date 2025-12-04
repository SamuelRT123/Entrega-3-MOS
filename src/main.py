# main.py

import random

from data_loader import load_instance
from ga_algorithm import GeneticAlgorithm
from verification import export_verification


# ============================
# PARÁMETROS GLOBALES DEL GA
# ============================

# Semilla para reproducibilidad (CAMBIA ESTO PARA NUEVOS EXPERIMENTOS)
SEED = 42

# Tamaño de población
POP_SIZE = 50

# Número de generaciones
N_GENERATIONS = 200

# Probabilidades de operadores
P_CROSS = 0.8      # probabilidad de cruce
P_MUT = 0.2        # probabilidad de mutación


def main():
    # Fijar semilla global (por si hay otros randoms fuera del GA)
    random.seed(SEED)

    # ============================
    # CARGA DE INSTANCIA
    # ============================
    instance_path = "./data/Proyecto_Caso_Base"
    config = load_instance(instance_path)

    # ============================
    # CONSTRUCCIÓN DEL GA
    # ============================
    ga = GeneticAlgorithm(
        config=config,
        pop_size=POP_SIZE,
        generations=N_GENERATIONS,
        crossover_rate=P_CROSS,
        mutation_rate=P_MUT,
        seed=SEED,
    )

    # ============================
    # EJECUCIÓN
    # ============================
    best, history = ga.evolve()

    print("\nMejor solución encontrada:")
    print("Costo:", best.cost)
    print("Factible:", best.is_feasible)
    print("\nParámetros GA usados:")
    print(f"  Semilla           : {SEED}")
    print(f"  Población         : {POP_SIZE}")
    print(f"  Generaciones      : {N_GENERATIONS}")
    print(f"  P(cruce)          : {P_CROSS}")
    print(f"  P(mutación)       : {P_MUT}")

    export_verification(
        best,
        config,
        "verificacion_metaheuristica_GA_caso2.csv",
    )


if __name__ == "__main__":
    main()
