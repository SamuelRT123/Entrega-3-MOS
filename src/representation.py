# Cromosoma: 
class CVRPSolution:
    def __init__(self, routes):
        self.routes = routes  # [['cd01', 'c005', 'c003'], ['cd01', 'c005', 'c003']]
        #cada fila es un vehiculo y las columnas es la ruta que este sigue.
        self.cost = None
        self.is_feasible = True

    def copy(self):
        return CVRPSolution([r.copy() for r in self.routes])
