import networkx as nx

from solvers.model_cp import solving_MAPF, run_CPLEX
from environments.environments import environments

"""
This file allows to call to a specific graph the CP-based solution based on IBM CPLEX.
"""

number_of_agents = 2
SIZE = 5
UPPER_BOUND = SIZE * 2

agents, edges, shortest_path, _ = environments(nx.grid_2d_graph, [(0, 1), (1, 0)], n=SIZE, m=SIZE)

check, RET, num_layers, solve_time, memory_usage, number_of_conflicts, decisions = \
    solving_MAPF(agents, edges, UPPER_BOUND, shortest_path)

if check:
    _, mksp, solve_time, memory_usage, number_of_conflicts, decisions = \
        run_CPLEX(edges, agents, RET, num_layers)
else:
    print("unsatisfiable")
