from utils.environments import *
from solvers.model_cp import solving_MAPF, run_CPLEX
import networkx as nx
import matplotlib.pyplot as plt
from solvers.model_smt import run_Z3


edges = [{0, 1, 2}, {0, 1, 2}, {0, 1, 2}]
agents = [(0, 1), (1, 2), (2, 0)]
UPPER_BOUND = 1
graph = nx.uniform_random_intersection_graph(len(edges), len(edges), 1)
min_shortest_path, makespan = min_max_shortest_path(graph, agents)

print("ENVIRONMENT: ")
[print(str(node) + ": " + str(neighbors)) for node, neighbors in enumerate(edges)]
print("AGENTS: ")
print(agents)

sep = "=" * 50
print(sep)
print("Z3")
check, _, _, _, _, _ = run_Z3(edges, agents, makespan)

while not check and makespan <= UPPER_BOUND:
    makespan += 1
    check, _, _, _, _, _ = run_Z3(edges, agents, makespan)

if not check and makespan >= UPPER_BOUND:
    print("Unsatisfiable")

print(sep)
print("CPLEX")
print("Step 1) Searching for optimal number of layers")
check, RET, num_layers, _, _, _, _ = \
    solving_MAPF(agents, edges, UPPER_BOUND, min_shortest_path)

print(sep)
print("Step 2) Solving with %d layers" % num_layers)
print(sep)
if check:
    _, mksp, _, _, _, _, _ = \
        run_CPLEX(edges, agents, RET, num_layers)
else:
    print("Unsatisfiable")

nx.draw(graph, with_labels=True)
plt.show()
