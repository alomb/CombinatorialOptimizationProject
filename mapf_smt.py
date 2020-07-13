from solvers.model_smt import run_Z3
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

ROWS = 3
COLUMNS = 3
number_of_agents = 1
graph_type = "intersection_graph"
# Makespan: time steps (from 0 to makespan_size - 1)
makespan = 0

# Maximum makespan
upper_bound = 10

agents, edges, _ = environments(number_of_agents, graph_type, rows=ROWS, columns=COLUMNS)
# agents = [(0, 1), (1, 2), (2, 0)]

check, memory_usage, number_of_conflicts, decisions = run_Z3(edges, agents, makespan)

# ----------------------------------------------------------------------------------------------------------------------
while not check and makespan <= upper_bound:
    makespan += 1
    check, memory_usage, number_of_conflicts, decisions = run_Z3(edges, agents, makespan)
