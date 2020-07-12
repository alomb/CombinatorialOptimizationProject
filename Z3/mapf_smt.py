from Z3.model_smt import run_Z3
import random
from environments.environments import environments


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

ROWS = 4
COLUMNS = 4
number_of_agents = ROWS
graph = "intersection_graph"
# Makespan: time steps (from 0 to makespan_size - 1)
makespan = 0

# Maximum makespan
upper_bound = 10

agents, edges, _ = environments(ROWS, COLUMNS, number_of_agents, graph)

# ----------------------------------------------------------------------------------------------------------------------
while not run_Z3(edges, agents, makespan) and makespan <= upper_bound:
    makespan += 1

