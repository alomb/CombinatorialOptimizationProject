from docplex.cp.model import *
import docplex.cp.utils_visu as visu

model = CpoModel()

# ======================================================================================================================
# Variables and constants
# ======================================================================================================================

agents = [(0, 0), (1, 1)]
agents_len = len(agents)

edges = [{0, 1}, {1, 0}]
edges_len = len(edges)

# layers from 0 to l - 1 both included
num_layers = 1
upper_bound = 1

makespan = integer_var(0, upper_bound, name="MKSP")

N = [[[interval_var(start=(0, upper_bound), end=(0, upper_bound), name="N%s_%s_%s" % (vertex, agent, layer))
       for layer in range(num_layers)]
      for agent in range(agents_len)]
     for vertex in range(edges_len)]

Nin = [[[interval_var(start=(0, upper_bound), end=(0, upper_bound), name="Nin%s_%s_%s" % (vertex, agent, layer))
         for layer in range(num_layers)]
        for agent in range(agents_len)]
       for vertex in range(edges_len)]

Nout = [[[interval_var(start=(0, upper_bound), end=(0, upper_bound), name="Nout%s_%s_%s" % (vertex, agent, layer))
          for layer in range(num_layers)]
         for agent in range(agents_len)]
        for vertex in range(edges_len)]

A = [[[[interval_var(start=(0, upper_bound), end=(0, upper_bound), name="Nout%s_%s_%s_%s" % (vertex, neighbor, agent, layer))
        for layer in range(num_layers)]
       for agent in range(agents_len)]
      for neighbor in edges[vertex] if vertex != neighbor]
     for vertex in range(edges_len)]

A_equal = [[[[interval_var(start=(0, upper_bound), end=(0, upper_bound), length=0, name="Nout%s_%s_%s_%s" % (vertex, neighbor, agent, layer))
        for layer in range(num_layers - 1)]
       for agent in range(agents_len)]
      for neighbor in edges[vertex] if vertex == neighbor]
     for vertex in range(edges_len)]


# ======================================================================================================================
# Constraints
# ======================================================================================================================

# (1)
[model.add(presence_of(N[pair[0]][a][0]) == 1) for a, pair in enumerate(agents)]

# (2)
[model.add(presence_of(N[pair[1]][a][num_layers - 1]) == 1) for a, pair in enumerate(agents)]

# (3)
[model.add(presence_of(Nin[pair[0]][a][0]) == 0) for a, pair in enumerate(agents)]

# (4)
[model.add(presence_of(Nout[pair[1]][a][num_layers - 1]) == 0) for a, pair in enumerate(agents)]

# (5)
[model.add(logical_and(
    if_then(presence_of(N[vertex][agent][layer]), presence_of(Nin[vertex][agent][layer])),
    if_then(presence_of(Nin[vertex][agent][layer]), presence_of(N[vertex][agent][layer]))))
 if pair[0] != vertex or layer != 0
 else True
 for layer in range(num_layers)
 for agent, pair in enumerate(agents)
 for vertex in range(edges_len)]

# (6)
[model.add(logical_and(
    if_then(presence_of(N[vertex][agent][layer]), presence_of(Nout[vertex][agent][layer])),
    if_then(presence_of(Nout[vertex][agent][layer]), presence_of(N[vertex][agent][layer]))))
 if pair[1] != vertex or layer != num_layers - 1
 else True
 for layer in range(num_layers)
 for agent, pair in enumerate(agents)
 for vertex in range(edges_len)]

# (9)
[model.add(if_then(presence_of(A[vertex][neighbor][agent][layer]), presence_of(Nin[neighbor][agent][layer])))
 for vertex in range(edges_len)
 for neighbor in range(len(edges[vertex].difference({vertex})))
 for agent in range(agents_len)
 for layer in range(num_layers)]

# (10)
[model.add(if_then(presence_of(A[vertex][neighbor][agent][layer]), presence_of(Nout[vertex][agent][layer])))
 for vertex in range(edges_len)
 for neighbor in range(len(edges[vertex].difference({vertex})))
 for agent in range(agents_len)
 for layer in range(num_layers)]

# (11)
[model.add(if_then(presence_of(A_equal[vertex][vertex][agent][layer]), presence_of(Nin[vertex][agent][layer + 1])))
 for vertex in range(edges_len)
 for agent in range(agents_len)
 for layer in range(num_layers - 1)]

# (12)
[model.add(if_then(presence_of(A_equal[vertex][vertex][agent][layer]), presence_of(Nout[vertex][agent][layer])))
 for vertex in range(edges_len)
 for agent in range(agents_len)
 for layer in range(num_layers - 1)]

# (13)
[model.add(start_of(N[pair[0]][a][0]) == 0) for a, pair in enumerate(agents)]

# (14)
[model.add(end_of(N[pair[1]][a][num_layers - 1]) == makespan) for a, pair in enumerate(agents)]

# (15)
[model.add(start_of(N[vertex][agent][layer]) == end_of(Nin[vertex][agent][layer]))
 if pair[0] != vertex or layer != 0
 else True
 for layer in range(num_layers)
 for agent, pair in enumerate(agents)
 for vertex in range(edges_len)]

# (16)
[model.add(end_of(N[vertex][agent][layer]) == start_of(Nout[vertex][agent][layer]))
 if pair[1] != vertex or layer != num_layers - 1
 else True
 for layer in range(num_layers)
 for agent, pair in enumerate(agents)
 for vertex in range(edges_len)]

# model.add(alternative(Nin[0][0][0], [N[0][0][0], N[1][1][0]]))

# model.add(no_overlap([Nin[0][0][0], Nin[1][0][0], N[1][0][0], N[1][1][0]]))

# Solve model

#print("Solving model....")
#msol = model.solve(FailLimit=100000, TimeLimit=10)
#print("Solution: ")
#msol.print_solution()