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
graph_type = "intersection_graph"

agents, edges, shortest_path = environments(ROWS, COLUMNS, number_of_agents, graph_type)

agents = [(0, 1), (1, 2), (2, 0)]

check, RET, num_layers,solve_time, memory_usage, number_of_conflicts, decisions = solving_MAPF(agents, edges, upper_bound, shortest_path)

if check:
    _, mksp, solve_time, memory_usage, number_of_conflicts, decisions = run_CPLEX(edges, agents, RET, num_layers)
else:
    print("unsatisfiable")