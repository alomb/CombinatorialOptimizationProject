from Z3.model_smt import run_Z3
from CPLEX.model_cp import run_CPLEX, solving_MAPF
from graphs.grid_2d_graph import generate_grid_2d_graph
import time
import numpy as np
import random
import matplotlib.pyplot as plt

# TODO: understand how to get solver statistics to plot them

ROWS = 2
COLUMNS = 2
MAX_SIZE = 5

time_CPLEX = []
time_Z3 = []

size_range = np.linspace(ROWS, MAX_SIZE, MAX_SIZE - ROWS + 1)

while ROWS <= MAX_SIZE:

    makespan = 0
    upper_bound = 2 * ROWS

    agents = [(random.randint(0, ROWS * COLUMNS - 1), random.randint(0, ROWS * COLUMNS - 1)),
             (random.randint(0, ROWS * COLUMNS - 1), random.randint(0, ROWS * COLUMNS - 1))]

    edges, shortest_path = generate_grid_2d_graph(ROWS, COLUMNS, agents)

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

    end = time.time()
    time_CPLEX.append(end - start)

    ROWS += 1
    COLUMNS += 1

fig, ax = plt.subplots()
plt.title("Z3 vs CPLEX")
plt.plot(size_range, time_Z3, "-b", label='Z3')
plt.plot(size_range, time_CPLEX, "-r", label='CPLEX')
ax.set_xlabel("Graph's size")
ax.set_ylabel("time")
ax.legend(loc='best')
plt.yscale('log')
plt.show()