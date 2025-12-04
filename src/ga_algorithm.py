# ga_algorithm.py

import random
from representation import CVRPSolution
from evaluation import evaluate_solution
from data_loader import MainConfig
from operators import crossover, mutate, repair
from typing import Optional


class GeneticAlgorithm:
    def __init__(
        self,
        config: MainConfig,
        pop_size: int = 30,
        generations: int = 200,
        crossover_rate: float = 0.8,
        mutation_rate: float = 0.2,
        seed: Optional[int] = None,
    ):

        """
        Algoritmo Genético para el CVRP.

        Parámetros:
          - pop_size: tamaño de la población
          - generations: número de generaciones
          - crossover_rate: probabilidad de aplicar cruce
          - mutation_rate: probabilidad de mutar un individuo
          - seed: semilla para hacer el experimento reproducible
        """
        self.config = config
        self.pop_size = pop_size
        self.generations = generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.population: list[CVRPSolution] = []

        # ÚNICO depósito (por enunciado)
        self.depot_code = config.depot.code

        # Semilla del generador aleatorio (reproducibilidad)
        if seed is not None:
            random.seed(seed)

    def create_individual(self) -> CVRPSolution:
        """
        Crea individuo inicial: permutación de clientes repartida en k rutas.
        """
        clients_codes = list(self.config.clients.keys())
        random.shuffle(clients_codes)

        # Distribuimos clientes en k rutas iniciales (k = #vehículos)
        k = max(1, len(self.config.vehicles))
        routes = [[] for _ in range(k)]

        for i, c in enumerate(clients_codes):
            routes[i % k].append(c)

        # Rodeamos cada ruta con el depósito
        routes = [[self.depot_code] + r + [self.depot_code] for r in routes]
        return CVRPSolution(routes)

    def init_population(self):
        """
        Inicializa la población aplicando reparación/evaluación a cada individuo.
        """
        self.population = []
        for _ in range(self.pop_size):
            ind = self.create_individual()
            ind = repair(ind, self.config, self.depot_code)
            self.population.append(ind)

    def evolve(self):
        """
        Ciclo principal del GA:
        - Ordena por costo
        - Elitismo
        - Selección + cruce + mutación
        """
        self.init_population()

        best_costs = []

        for gen in range(self.generations):
            # Evaluación y ordenamiento
            self.population.sort(key=lambda s: evaluate_solution(s, self.config))
            best = self.population[0]
            best_costs.append(best.cost)

            new_pop: list[CVRPSolution] = []

            # Elitismo: copiamos los mejores tal cual
            elites = 5
            new_pop.extend(self.population[:elites])

            # Relleno de la población
            while len(new_pop) < self.pop_size:
                # Selección: torneo sobre los mejores 15
                parents_pool = self.population[:min(15, len(self.population))]
                p1, p2 = random.sample(parents_pool, 2)

                # Cruce con probabilidad crossover_rate
                if random.random() < self.crossover_rate:
                    child = crossover(p1, p2, self.config, self.depot_code)
                else:
                    # Sin cruce: clonamos uno de los padres
                    child = p1.copy()

                # Mutación con probabilidad mutation_rate (lo maneja mutate)
                child = mutate(
                    child,
                    self.config,
                    self.depot_code,
                    mutation_rate=self.mutation_rate,
                )

                # Reparación/evaluación final
                child = repair(child, self.config, self.depot_code)

                new_pop.append(child)

            self.population = new_pop
            print(f"Gen {gen} | Best Cost: {best.cost:.2f} | Factible: {best.is_feasible}")

        # Aseguramos devolver el mejor ordenando al final
        self.population.sort(key=lambda s: evaluate_solution(s, self.config))
        best = self.population[0]

        return best, best_costs
