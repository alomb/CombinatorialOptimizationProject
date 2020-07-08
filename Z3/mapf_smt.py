from Z3.model_smt import run_Z3
import random
from graphs.grid_2d_graph import generate_grid_2d_graph


"""
#   4
# 01235

# agents = [(0, 1), (1, 2)]  # makespan = 2
# agents = [(0, 2), (2, 3), (3, 0)]  # makespan = 6
# agents = [(0, 3), (3, 0)]  # makespan = 5

# Use OrderDict to avoid using sets that may change order each time edges is called to retrieve neighbors

edges_Z3 = [OrderedDict([(0, None), (1, None)]),
         OrderedDict([(0, None), (1, None), (2, None)]),
         OrderedDict([(1, None), (2, None), (3, None), (4, None)]),
         OrderedDict([(2, None), (3, None), (5, None)]),
         OrderedDict([(2, None), (4, None)]),
         OrderedDict([(3, None), (5, None)])]
"""

ROWS = 5
COLUMNS = 5

# Makespan: time steps (from 0 to makespan_size - 1)
makespan = 0

# Maximum makespan
upper_bound = 10

# TODO: check if the start/end position of an agent is equal to the start/end position of another
agents = [(random.randint(0, ROWS * COLUMNS - 1), random.randint(0, ROWS * COLUMNS - 1)),
          (random.randint(0, ROWS * COLUMNS - 1), random.randint(0, ROWS * COLUMNS - 1))]

edges, _ = generate_grid_2d_graph(ROWS, COLUMNS, agents)

# ----------------------------------------------------------------------------------------------------------------------
while not run_Z3(edges, agents, makespan) and makespan <= upper_bound:
    makespan += 1

