from CPLEX.model_cp import run_CPLEX
from graphs.grid_2d_graph import generate_grid_2d_graph
import random

# ======================================================================================================================
# Variables and constants
# ======================================================================================================================

""""
# agents = [(0, 2), (2, 3), (3, 0)]
# agents = [(0, 3), (3, 0)]

#   4
# 01235
#edges = [{0, 1}, {1, 0, 2}, {1, 2, 3, 4}, {2, 3, 5}, {2, 4}, {3, 5}]
"""

ROWS = 5
COLUMNS = 5

# TODO: check if the start/end position of an agent is equal to the start/end position of another
agents = [(random.randint(0, ROWS * COLUMNS - 1), random.randint(0, ROWS * COLUMNS - 1)),
          (random.randint(0, ROWS * COLUMNS - 1), random.randint(0, ROWS * COLUMNS - 1))]

edges, shortest_path = generate_grid_2d_graph(ROWS, COLUMNS, agents)

# layers from 0 to l - 1 both included
num_layers = 1
upper_bound = 10

check, RET = run_CPLEX(edges, agents, upper_bound, num_layers)

while not check and num_layers < upper_bound:
    check, RET = run_CPLEX(edges, agents, upper_bound, num_layers)
    num_layers += 1

num_layers = round((RET - shortest_path)/2 + 1)

if check:
    _, mksp = run_CPLEX(edges, agents, RET, num_layers)
else:
    print("unsatisfiable")