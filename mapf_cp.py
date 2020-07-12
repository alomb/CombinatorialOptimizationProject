from CPLEX.model_cp import run_CPLEX
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
graph = "intersection_graph"

agents, edges, shortest_path = environments(ROWS, COLUMNS, number_of_agents, graph)

# layers from 0 to l - 1 both included
num_layers = 1
upper_bound = 10

check, RET = run_CPLEX(edges, agents, upper_bound, num_layers)

while not check and num_layers < upper_bound:
    check, RET = run_CPLEX(edges, agents, upper_bound, num_layers)
    num_layers += 1

print("num_layers good", num_layers)
num_layers = round((RET - shortest_path)/2) + 1
print("num_layers not good", num_layers)

if check:
    _, mksp = run_CPLEX(edges, agents, RET, num_layers)
else:
    print("unsatisfiable")