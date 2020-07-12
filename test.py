from Z3.model_smt import run_Z3
from CPLEX.model_cp import run_CPLEX, solving_MAPF
from environments.environments import environments
import time
import numpy as np
import matplotlib.pyplot as plt

# TODO: understand how to get solver statistics to plot them


def test(rows, columns, max_size, graph):

    time_CPLEX = []
    time_Z3 = []

    size_range = np.linspace(rows, max_size, max_size - rows + 1)

    while rows <= max_size:

        makespan = 0
        upper_bound = 2 * rows
        number_of_agents = rows

        agents, edges, shortest_path = environments(rows, columns, number_of_agents, graph)

        # ----------------------------------------------------------------------------------------------------------------------

        # Z3
        start = time.time()
        while not run_Z3(edges, agents, makespan) and makespan <= upper_bound:
            makespan += 1
        end = time.time()

        time_Z3.append(end - start)

        # CPLEX
        start = time.time()
        check, RET, num_layers = solving_MAPF(agents, edges, upper_bound, shortest_path)

        if check:
            run_CPLEX(edges, agents, RET, num_layers)
        else:
            print("CPLEX: unsatisfiable")

        print("="*50)

        end = time.time()
        time_CPLEX.append(end - start)

        rows += 1
        columns += 1

    fig, ax = plt.subplots()
    plt.title("Z3 vs CPLEX")
    plt.plot(size_range, time_Z3, "-b", label='Z3')
    plt.plot(size_range, time_CPLEX, "-r", label='CPLEX')
    ax.set_xlabel("Graph's size")
    ax.set_ylabel("time")
    ax.legend(loc='best')
    plt.yscale('log')
    plt.show()

ROWS = 2
COLUMNS = 2
MAX_SIZE = 5
graph = "intersection_graph"

test(ROWS, COLUMNS, MAX_SIZE, graph)
