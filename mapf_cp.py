from CPLEX.model_cp import run_CPLEX, solving_MAPF
from environments.environments import environments

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

ROWS = 3
COLUMNS = 3
number_of_agents = 3
upper_bound = 10
graph = "intersection_graph"

agents, edges, shortest_path = environments(ROWS, COLUMNS, number_of_agents, graph)

agents = [(0, 0), (0, 1), (2, 1)]

check, RET, num_layers = solving_MAPF(agents, edges, upper_bound, shortest_path)

if check:
    _, mksp = run_CPLEX(edges, agents, RET, num_layers)
else:
    print("unsatisfiable")