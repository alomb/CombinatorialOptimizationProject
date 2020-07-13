import networkx as nx

from solvers.model_cp import solving_MAPF, run_CPLEX
from environments.environments import environments

"""
This file allows to call to a specific graph the CP-based solution based on IBM CPLEX.
"""

number_of_agents = 2
UPPER_BOUND = 10

agents, edges, shortest_path = environments(nx.grid_2d_graph, [(0, 1), (1, 0)], n=2, m=2)

check, RET, num_layers, solve_time, memory_usage, number_of_conflicts, decisions = \
    solving_MAPF(agents, edges, UPPER_BOUND, shortest_path)

if check:
    _, mksp, solve_time, memory_usage, number_of_conflicts, decisions = \
        run_CPLEX(edges, agents, RET, num_layers)
else:
    print("unsatisfiable")
