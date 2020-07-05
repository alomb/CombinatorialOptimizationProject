from Z3.model_smt import run
from collections import OrderedDict

# List of neighbors, agents are represented by the index

#   4
# 01235

# Use OrderDict to avoid using sets that may change order each time edges is called to retrieve neighbors
edges = [OrderedDict([(0, None), (1, None)]),
         OrderedDict([(0, None), (1, None), (2, None)]),
         OrderedDict([(1, None), (2, None), (3, None), (4, None)]),
         OrderedDict([(2, None), (3, None), (5, None)]),
         OrderedDict([(2, None), (4, None)]),
         OrderedDict([(3, None), (5, None)])]

# Makespan: time steps (from 0 to makespan_size - 1)
makespan = 0
# Maximum makespan
upper_bound = 10

agents = [(0, 1), (1, 2)]  # makespan = 2
# agents = [(0, 2), (2, 3), (3, 0)]  # makespan = 6
# agents = [(0, 3), (3, 0)]  # makespan = 5

# ----------------------------------------------------------------------------------------------------------------------
while not run(edges, agents, makespan) and makespan <= upper_bound:
    makespan += 1