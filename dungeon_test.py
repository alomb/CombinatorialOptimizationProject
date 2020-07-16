from environments.environments import *
from solvers.model_cp import solving_MAPF, run_CPLEX
from solvers.model_smt import run_Z3
import networkx as nx
import matplotlib.pyplot as plt

ROOM_NUM = 3
ROOM_SIZE_MIN = 3
ROOM_SIZE_MAX = 3
CORRIDOR_LENGTH_MIN = 2
CORRIDOR_LENGTH_MAX = 2
SEED = 42
upper_bound = ROOM_NUM * ROOM_SIZE_MIN * ROOM_SIZE_MAX * CORRIDOR_LENGTH_MAX * CORRIDOR_LENGTH_MAX

sep = "=" * 50

agents = [(4, 13), (13, 22), (22, 4)]
dungeon = generate_dungeon(ROOM_NUM, ROOM_SIZE_MIN, ROOM_SIZE_MAX, CORRIDOR_LENGTH_MIN, CORRIDOR_LENGTH_MAX, SEED)

edges = []

for node, neighbors in dungeon.adj.items():
    edges.insert(node, set())
    edges[node].add(node)
    for neighbor, _ in neighbors.items():
        edges[node].add(neighbor)

print(sep)

print("ENVIRONMENT: ")
[print(str(node) + ": " + str(neighbors)) for node, neighbors in enumerate(edges)]
print("AGENTS: ")
print(agents)

min_shortest_path, max_shortest_path = min_max_shortest_path(dungeon, agents)
makespan = max_shortest_path

print(sep)
print("Z3")
check, solve_time, memory_usage, number_of_conflicts, decisions, _ = run_Z3(edges, agents, makespan)

while not check and makespan <= upper_bound:
    makespan += 1
    check, solve_time, memory_usage, number_of_conflicts, decisions, _ = run_Z3(edges, agents, makespan)

if not check and makespan >= upper_bound:
    print("Unsatisfiable")

print(sep)

print("CPLEX")
print(sep)
print("\nStep 1) Searching for optimal number of layers\n")
print(sep)
check, ret, num_layers, _, _, _, _ = \
    solving_MAPF(agents, edges, upper_bound, min_shortest_path)
print(sep)
print("\nStep 2) Solving with %d layers\n" % num_layers)
print(sep)
if check:
    _, _, _, _, _, _, _ = \
        run_CPLEX(edges, agents, ret, num_layers)
else:
    print("CPLEX: unsatisfiable")

print(sep)
nx.draw(dungeon, with_labels=True)
plt.show()