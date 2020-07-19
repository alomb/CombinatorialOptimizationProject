from utils.animation import movement_animation
from solvers.model_smt import run_Z3
from utils.environments import *

"""
This file allows to call to a specific graph the SMT-based solution based on Z3Py. Feel free to change graph, agents 
sizes etc..
"""

SIZE = 3
# Maximum makespan
UPPER_BOUND = SIZE * 2
SEED = 42
number_of_agents = 4

# e.g. the grid environment
agents, edges, graph = environments(nx.grid_2d_graph, number_of_agents, SEED, n=SIZE, m=SIZE)

# The maximum shortest path is used as the initial makespan
_, makespan = min_max_shortest_path(graph, agents)

# The loop used to find the solution with the minimal makespan
check, _, memory_usage, number_of_conflicts, decisions, paths = run_Z3(edges, agents, makespan)

while not check and makespan <= UPPER_BOUND:
    makespan += 1
    check, _, memory_usage, number_of_conflicts, decisions, paths = run_Z3(edges, agents, makespan)

if not check and makespan >= UPPER_BOUND:
    print("Unsatisfiable")

# Comment to not generate gif
if paths is not None:
    movement_animation(graph, paths, "./resources/small_grid_2d.gif", seed=SEED)

# Uncomment to only visualize graph
"""
nx.draw(graph, with_labels=True)
plt.show()
"""
