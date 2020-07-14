import networkx as nx

from solvers.model_cp import solving_MAPF, run_CPLEX
from environments.environments import *

"""
This file allows to call to a specific graph the CP-based solution based on IBM CPLEX.
"""

number_of_agents = 2
SIZE = 5
UPPER_BOUND = 70
SEED = 42

agents, edges, shortest_path, _ = environments(generate_dungeon, 1, SEED, rooms_num=2, rooms_size_min=3,
                                               rooms_size_max=3, corridor_length_min=2, corridor_length_max=2,
                                               seed=SEED)

sep = "=" * 50
print(sep)
print("Step 1) Searching for optimal number of layers")
print(sep)
check, RET, num_layers, solve_time, memory_usage, number_of_conflicts, decisions = \
    solving_MAPF(agents, edges, UPPER_BOUND, shortest_path)

print(sep)
print("Step 2) Solving with optimal number of layers")
print(sep)
if check:
    _, mksp, solve_time, memory_usage, number_of_conflicts, decisions = \
        run_CPLEX(edges, agents, RET, num_layers)
else:
    print("unsatisfiable")
