# main.py

from data_loader import load_instance
from ga_algorithm import GeneticAlgorithm
from verification import export_verification

if __name__ == "__main__":
    # Cambia esta ruta para correr Caso Base / Caso 2 / Caso 3
    # ejemplo: "./data/Proyecto_Caso_Base"
    instance_path = "./data/Proyecto_Caso_2"

    config = load_instance(instance_path)

    ga = GeneticAlgorithm(config, pop_size=40, generations=100)
    best, history = ga.evolve()

    print("\n===========================")
    print("Mejor solución encontrada:")
    print("Costo:", best.cost)
    print("Factible:", best.is_feasible)
    print("Rutas:", best.routes)

    export_verification(
        best,
        config,
        "verificacion_metaheuristica_GA_caso2.csv"
    )
    print("Archivo de verificación generado.")
