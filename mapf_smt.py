import networkx as nx

from solvers.model_smt import run_Z3
from environments.environments import environments

"""
This file allows to call to a specific graph the SMT-based solution based on Z3Py.
"""

# Makespan: time steps (from 0 to makespan_size - 1)
makespan = 0

# Maximum makespan
UPPER_BOUND = 10

number_of_agents = 2
agents, edges, _ = environments(nx.grid_2d_graph, number_of_agents, n=5, m=5)

check, memory_usage, number_of_conflicts, decisions = run_Z3(edges, agents, makespan)

while not check and makespan <= UPPER_BOUND:
    makespan += 1
    check, memory_usage, number_of_conflicts, decisions = run_Z3(edges, agents, makespan)
