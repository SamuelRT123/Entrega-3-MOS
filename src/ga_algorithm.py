import random
from representation import CVRPSolution
from evaluation import evaluate_solution
from data_loader import MainConfig
from operators import crossover, mutate, repair



class GeneticAlgorithm:
    
    def __init__(self, config: MainConfig, pop_size=30, generations=200):
        self.config = config
        self.pop_size = pop_size
        self.generations = generations
        self.population = []

        # ÚNICO depósito (por enunciado)
        self.depot_code = config.depot.code

    def create_individual(self) -> CVRPSolution:
        """
        Crea individuo inicial: permutación de clientes repartida en k rutas.
        """
        clients_codes = list(self.config.clients.keys())
        random.shuffle(clients_codes)

        k = max(1, len(self.config.vehicles))
        routes = [[] for _ in range(k)]

        for i, c in enumerate(clients_codes):
            routes[i % k].append(c)

        routes = [[self.depot_code] + r + [self.depot_code] for r in routes]
        return CVRPSolution(routes)

    def init_population(self):
        self.population = []
        for _ in range(self.pop_size):
            ind = self.create_individual()
            ind = repair(ind, self.config, self.depot_code)
            self.population.append(ind)

    def evolve(self):
        self.init_population()

        best_costs = []

        for gen in range(self.generations):
            self.population.sort(key=lambda s: evaluate_solution(s, self.config))
            best = self.population[0]
            best_costs.append(best.cost)

            new_pop = self.population[:5]  # elitismo

            while len(new_pop) < self.pop_size:
                p1, p2 = random.sample(self.population[:15], 2)

                child = crossover(p1, p2, self.config, self.depot_code)
                child = mutate(child, self.config, self.depot_code)
                child = repair(child, self.config, self.depot_code)

                new_pop.append(child)

            self.population = new_pop
            print(f"Gen {gen} | Best Cost: {best.cost:.2f}")

        return self.population[0], best_costs
