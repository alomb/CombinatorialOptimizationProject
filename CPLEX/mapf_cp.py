from docplex.cp.model import *
import re

model = CpoModel()

# ======================================================================================================================
# Variables and constants
# ======================================================================================================================

# agents = [(0, 2), (2, 3), (3, 0)]
# agents = [(0, 3), (3, 0)]
agents = [(0, 1), (1, 0)]
agents_len = len(agents)

#   4
# 01235
edges = [{0, 1}, {1, 0, 2}, {1, 2, 3, 4}, {2, 3, 5}, {2, 4}, {3, 5}]
edges_len = len(edges)

# layers from 0 to l - 1 both included
num_layers = 4
upper_bound = 20

makespan = integer_var(0, upper_bound, name="MKSP")

N = [[[interval_var(start=(0, upper_bound), end=(0, upper_bound),
                    name="N_%s_%s_%s" % (vertex, agent, layer), optional=True)
       for layer in range(num_layers)]
      for agent in range(agents_len)]
     for vertex in range(edges_len)]

Nin = [[[interval_var(start=(0, upper_bound), end=(0, upper_bound),
                      name="Nin_%s_%s_%s" % (vertex, agent, layer), optional=True)
         for layer in range(num_layers)]
        for agent in range(agents_len)]
       for vertex in range(edges_len)]

Nout = [[[interval_var(start=(0, upper_bound), end=(0, upper_bound),
                       name="Nout_%s_%s_%s" % (vertex, agent, layer), optional=True)
          for layer in range(num_layers)]
         for agent in range(agents_len)]
        for vertex in range(edges_len)]

A = [dict((neighbor, [[interval_var(start=(0, upper_bound), end=(0, upper_bound), length=1,
                                    name="A_%s_%s_%s_%s" % (vertex, neighbor, agent, layer), optional=True)
                       for layer in range(num_layers)]
                      for agent in range(agents_len)])
          for neighbor in edges[vertex] if vertex != neighbor)
     for vertex in range(edges_len)]

A_equal = [[[[interval_var(start=(0, upper_bound), end=(0, upper_bound), length=0,
                           name="Ae_%s_%s_%s_%s" % (vertex, neighbor, agent, layer), optional=True)
              for layer in range(num_layers - 1)]
             for agent in range(agents_len)]
            for neighbor in edges[vertex] if vertex == neighbor]
           for vertex in range(edges_len)]

# ======================================================================================================================
# Constraints
# ======================================================================================================================

# (1) All agents must occupy their starting position at the first layer
[model.add(presence_of(N[pair[0]][a][0]) == 1) for a, pair in enumerate(agents)]

# (2) All agents must occupy their ending position at the last layer
[model.add(presence_of(N[pair[1]][a][num_layers - 1]) == 1) for a, pair in enumerate(agents)]

# (3) All agents don't traverse edges to reach their first position at the first layer
[model.add(presence_of(Nin[pair[0]][a][0]) == 0) for a, pair in enumerate(agents)]

# (4) All agents don't traverse edges from their last position at the last layer
[model.add(presence_of(Nout[pair[1]][a][num_layers - 1]) == 0) for a, pair in enumerate(agents)]

# (5) For all agents and vertex (excluding origins) each N requires a Nin (and vice versa) for each layer (excluding
# the first)
[model.add(logical_and(
    if_then(presence_of(N[vertex][agent][layer]), presence_of(Nin[vertex][agent][layer])),
    if_then(presence_of(Nin[vertex][agent][layer]), presence_of(N[vertex][agent][layer]))))
 if pair[0] != vertex or layer != 0
 else True
 for layer in range(num_layers)
 for agent, pair in enumerate(agents)
 for vertex in range(edges_len)]

# (6) For all agents and vertices (excluding destinations) each N requires a Nout (and vice versa) for each layer
# (excluding the last)
[model.add(logical_and(
    if_then(presence_of(N[vertex][agent][layer]), presence_of(Nout[vertex][agent][layer])),
    if_then(presence_of(Nout[vertex][agent][layer]), presence_of(N[vertex][agent][layer]))))
 if pair[1] != vertex or layer != num_layers - 1
 else True
 for layer in range(num_layers)
 for agent, pair in enumerate(agents)
 for vertex in range(edges_len)]

# (7) For each vertex, agent and layer Nin to that vertex requires AT MOST a traverse from one neighbor
[model.add(
    alternative(Nin[vertex][agent][layer],
                [A_equal[vertex][0][agent][layer - 1]] +
                [A[neighbor][vertex][agent][layer] for neighbor in edges[vertex].difference({vertex})]
                if layer > 0 else
                [A[neighbor][vertex][agent][layer] for neighbor in edges[vertex].difference({vertex})]
                ))
    for layer in range(num_layers)
    for agent in range(agents_len)
    for vertex in range(edges_len)]

# (8) For each vertex, agent and layer Nout from that vertex requires AT MOST a traverse to one neighbor
[model.add(
    alternative(Nout[vertex][agent][layer],
                [A_equal[vertex][0][agent][layer]] +
                [A[vertex][neighbor][agent][layer] for neighbor in edges[vertex].difference({vertex})]
                if layer < num_layers - 1 else
                [A[vertex][neighbor][agent][layer] for neighbor in edges[vertex].difference({vertex})]
                ))
    for layer in range(num_layers)
    for agent in range(agents_len)
    for vertex in range(edges_len)]

# (9) For each arc (x,y), agent and layer a traverse implies a Nin in y
[model.add(if_then(presence_of(A[vertex][neighbor][agent][layer]), presence_of(Nin[neighbor][agent][layer])))
 for vertex in range(edges_len)
 for neighbor in edges[vertex].difference({vertex})
 for agent in range(agents_len)
 for layer in range(num_layers)]

# (10) For each arc (x,y), agent and layer a traverse implies a Nout in x
[model.add(if_then(presence_of(A[vertex][neighbor][agent][layer]), presence_of(Nout[vertex][agent][layer])))
 for vertex in range(edges_len)
 for neighbor in edges[vertex].difference({vertex})
 for agent in range(agents_len)
 for layer in range(num_layers)]

# (11) For each arc (x,x), agent and layer (excluding the last) a traverse implies a Nin in x in the successive layer
[model.add(if_then(presence_of(A_equal[vertex][0][agent][layer]), presence_of(Nin[vertex][agent][layer + 1])))
 for vertex in range(edges_len)
 for agent in range(agents_len)
 for layer in range(num_layers - 1)]

# (12) For each arc (x,x), agent and layer (excluding the last) a traverse implies a Nout in x
[model.add(if_then(presence_of(A_equal[vertex][0][agent][layer]), presence_of(Nout[vertex][agent][layer])))
 for vertex in range(edges_len)
 for agent in range(agents_len)
 for layer in range(num_layers - 1)]

# (13) Each agent start their activity in their origin at time 0
[model.add(start_of(N[pair[0]][a][0]) == 0) for a, pair in enumerate(agents)]

# (14) Each agent finish their activity in their destination at time makespan
[model.add(end_of(N[pair[1]][a][num_layers - 1]) == makespan) for a, pair in enumerate(agents)]

# (15) For each vertex, agent and layer the beginning of a N activity coincides with the end of a Nin one, excluding
# the case when the vertex it's the agent origin and the layer is the first (already considered in (13))
[model.add(start_of(N[vertex][agent][layer]) == end_of(Nin[vertex][agent][layer]))
 if pair[0] != vertex or layer != 0
 else True
 for layer in range(num_layers)
 for agent, pair in enumerate(agents)
 for vertex in range(edges_len)]

# (16) For each vertex, agent and layer the beginning of a N activity coincides with the start of a Nout one, excluding
# the case when the vertex it's the agent destination and the layer is the last (already considered in (14))
[model.add(end_of(N[vertex][agent][layer]) == start_of(Nout[vertex][agent][layer]))
 if pair[1] != vertex or layer != num_layers - 1
 else True
 for layer in range(num_layers)
 for agent, pair in enumerate(agents)
 for vertex in range(edges_len)]

"""
# TDM
tm_size = edges_len * num_layers * agents_len
tm = transition_matrix(tm_size)
for i in range(tm_size):
    for j in range(tm_size):
        tm.set_value(i, j, 1)

# (17) Prevent agents to occur at the same node at the same time
[model.add(no_overlap(sequence_var([N[vertex][agent][layer]
                                    for agent in range(agents_len)
                                    for layer in range(num_layers)])))
 for vertex in range(edges_len)]
"""

# (Alternative 17) Prevent agents to occur at the same node at the same time
[model.add(if_then(logical_and(presence_of(N[vertex][agent1][layer]), presence_of(N[vertex][agent2][layer])),
                   start_of(N[vertex][agent1][layer]) -
                   end_of(N[vertex][agent2][layer]) >= 1) if agent1 != agent2 else True)
 for vertex in range(edges_len)
 for layer in range(num_layers)
 for agent1 in range(agents_len)
 for agent2 in range(agents_len)]

# (18) Prevent agents from using an arc at the same time (no-swap constraint)
[model.add(no_overlap([element for sublist in [[A[vertex][neighbor][agent][layer], A[neighbor][vertex][agent][layer]]
                                               for agent in range(agents_len)
                                               for layer in range(num_layers)] for element in sublist]))
 for vertex in range(edges_len)
 for neighbor in edges[vertex].difference({vertex})]

# Solve model
print("Solving model...")

N_result = dict()
A_result = dict()
Ae_result = dict()

result = model.solve()
solution = result.solution

print("\n\nSolution with makespan %d:" % solution["MKSP"])

for name, var in solution.var_solutions_dict.items():
    if type(name) == str and type(var) == CpoIntervalVarSolution and var.is_present():
        # Use regex to extract from the name the type of the variable and the agent involved
        tokens = re.split("_", name)
        identifier = tokens[0]

        if identifier == "N":
            N_result.setdefault(int(tokens[2]), []).append(var)
        elif identifier == "A":
            A_result.setdefault(int(tokens[3]), []).append(var)
        elif identifier == "Ae":
            Ae_result.setdefault(int(tokens[3]), []).append(var)


def print_sorted_list_of_intervals(intervals):
    """
    Print the list interval variables sorted in increasing order. Those that start and end before have the precedence.

    :param intervals: the list of interval variables to print
    :return:
    """
    intervals.sort(key=lambda x: x.start + x.end)
    for e in intervals:
        print(e)


for agent in range(agents_len):
    print("Agent %d" % agent)
    """
    if agent in N_result:
        print_sorted_list_of_intervals(N_result[agent])
    """
    if agent in A_result:
        print_sorted_list_of_intervals(A_result[agent] + Ae_result[agent])
