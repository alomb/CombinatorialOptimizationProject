from docplex.cp.model import *

model = CpoModel()

# ======================================================================================================================
# Variables and constants
# ======================================================================================================================

agents = [(0, 0), (1, 1)]
agents_len = len(agents)

edges = [{0, 1}, {1, 0, 2}, {1, 2}]
edges_len = len(edges)

# layers from 0 to l - 1 both included
num_layers = 1
upper_bound = 10

makespan = integer_var(0, upper_bound, name="MKSP")

N = [[[interval_var(start=(0, upper_bound), end=(0, upper_bound), name="N%s_%s_%s" % (vertex, agent, layer),
                    optional=True)
       for layer in range(num_layers)]
      for agent in range(agents_len)]
     for vertex in range(edges_len)]

Nin = [[[interval_var(start=(0, upper_bound), end=(0, upper_bound), name="Nin%s_%s_%s" % (vertex, agent, layer),
         optional=True)
         for layer in range(num_layers)]
        for agent in range(agents_len)]
       for vertex in range(edges_len)]

Nout = [[[interval_var(start=(0, upper_bound), end=(0, upper_bound), name="Nout%s_%s_%s" % (vertex, agent, layer),
                       optional=True)
          for layer in range(num_layers)]
         for agent in range(agents_len)]
        for vertex in range(edges_len)]

A = [dict((neighbor, [[interval_var(start=(0, upper_bound), end=(0, upper_bound),
                                    name="A%s_%s_%s_%s" % (vertex, neighbor, agent, layer), optional=True)
                       for layer in range(num_layers)]
                      for agent in range(agents_len)])
          for neighbor in edges[vertex] if vertex != neighbor)
     for vertex in range(edges_len)]

A_equal = [[[[interval_var(start=(0, upper_bound), end=(0, upper_bound), length=0,
                           name="Ae%s_%s_%s_%s" % (vertex, neighbor, agent, layer))
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

# (7)
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

# (8)
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

# (9)
[model.add(if_then(presence_of(A[vertex][neighbor][agent][layer]), presence_of(Nin[neighbor][agent][layer])))
 for vertex in range(edges_len)
 for neighbor in edges[vertex].difference({vertex})
 for agent in range(agents_len)
 for layer in range(num_layers)]

# (10)
[model.add(if_then(presence_of(A[vertex][neighbor][agent][layer]), presence_of(Nout[vertex][agent][layer])))
 for vertex in range(edges_len)
 for neighbor in edges[vertex].difference({vertex})
 for agent in range(agents_len)
 for layer in range(num_layers)]

# (11)
[model.add(if_then(presence_of(A_equal[vertex][0][agent][layer]), presence_of(Nin[vertex][agent][layer + 1])))
 for vertex in range(edges_len)
 for agent in range(agents_len)
 for layer in range(num_layers - 1)]

# (12)
[model.add(if_then(presence_of(A_equal[vertex][0][agent][layer]), presence_of(Nout[vertex][agent][layer])))
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

# Prevent agents to occur at the same node at the same time (17)
[no_overlap([N[vertex][agent][layer]
             for agent in range(agents_len)
             for layer in range(num_layers)])
 for vertex in range(edges_len)]

# Prevent agents from using an arc at the same time (no-swap constraint) (18)
[no_overlap([A[vertex][neighbor][agent][layer]
             for agent in range(agents_len)
             for layer in range(num_layers)])
 for vertex in range(edges_len)
 for neighbor in edges[vertex].difference({vertex})]

# Solve model

print("Solving model....")
msol = model.solve(FailLimit=100000, TimeLimit=10)
print("Solution: ")
msol.print_solution()

