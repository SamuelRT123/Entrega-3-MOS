import time
from ga_algorithm import GeneticAlgorithm


def run_experiment(instance, runs=3):
    results = []

    for i in range(runs):
        ga = GeneticAlgorithm(instance)
        start = time.time()
        best = ga.evolve()
        elapsed = time.time() - start
        results.append((best.cost, elapsed))

    return results
