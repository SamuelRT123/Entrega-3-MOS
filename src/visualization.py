import matplotlib.pyplot as plt


def plot_convergence(costs):
    plt.plot(costs)
    plt.xlabel("Generación")
    plt.ylabel("Costo")
    plt.title("Convergencia del GA")
    plt.show()
