import networkx as nx

from solvers.model_smt import run_Z3
from environments.environments import environments

"""
This file allows to call to a specific graph the SMT-based solution based on Z3Py.
"""

# Maximum makespan
SIZE = 5
UPPER_BOUND = SIZE * 2

number_of_agents = 10
agents, edges, _, max_shortest_path = environments(nx.grid_2d_graph, number_of_agents, n=SIZE, m=SIZE)

makespan = max_shortest_path

check, _, memory_usage, number_of_conflicts, decisions = run_Z3(edges, agents, makespan)

while not check and makespan <= UPPER_BOUND:
    makespan += 1
    check, _, memory_usage, number_of_conflicts, decisions = run_Z3(edges, agents, makespan)
