from docplex.cp.model import *

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

# model.add(alternative(Nin[0][0][0], [N[0][0][0], N[1][1][0]]))

# model.add(no_overlap([Nin[0][0][0], Nin[1][0][0], N[1][0][0], N[1][1][0]]))

# More than one agent cannot occur at the same node at the same time (15)
[no_overlap([N[vertex][agent][layer]
             for agent in range(agents_len)
             for layer in range(num_layers)])
 for vertex in range(edges_len)]