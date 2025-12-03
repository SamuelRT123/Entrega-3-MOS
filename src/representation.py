class CVRPSolution:
    def __init__(self, routes):
        self.routes = routes  # [[0, 4, 2, 0], [0, 1, 3, 0]]
        self.cost = None
        self.is_feasible = True

    def copy(self):
        return CVRPSolution([r.copy() for r in self.routes])
