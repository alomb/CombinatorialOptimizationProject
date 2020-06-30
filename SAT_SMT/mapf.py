from z3 import *

# ======================================================================================================================
# Functions
# ======================================================================================================================

# arc(x, y)
# x = src node
# y = dst node
# the directed arc x -> y exists
arc_ = Function('arc', IntSort(), IntSort(), BoolSort())

# orig(a)
# a = agent
# map a a to its initial position
orig_ = Function('orig', IntSort(), IntSort())

# dest(a)
# a = agent
# map a a to its final position
dest_ = Function('dest', IntSort(), IntSort())

# at(x, a, t)
# x = vertex
# a = agent
# t = time step
# a is on the vertex x at t
at_ = Function('at', IntSort(), IntSort(), IntSort(), BoolSort())

# pass(x, y, a, t)
# x = source vertex
# y = destination vertex
# a = agent
# t = time step
# a pass through arc x -> y at t
pass_ = Function('pass', IntSort(), IntSort(), IntSort(), IntSort(), BoolSort())

# ======================================================================================================================
# Set of variables
# ======================================================================================================================

# Graph
# ----------------------------------------------------------------------------------------------------------------------

# List of neighbors, agents are represented by the index
edges = [{0, 1}, {0, 2, 1}, {1, 3, 2, 4}, {2, 3, 5}, {2, 4}, {3, 5}]
V_size = len(edges)
# Edges constraints
E = []

for index, neighbors in enumerate(edges):
    for neighbor in neighbors:
        E.append(arc_(index, neighbor))

# Time steps (from 0 to T_size - 1)
# ----------------------------------------------------------------------------------------------------------------------

T = 6
assert T >= 1

# Agents (from 0 to A_size - 1)
# ----------------------------------------------------------------------------------------------------------------------

agents = [(0, 2), (2, 3), (3, 0)]  # T = 6
# agents = [(0, 3), (3, 0)]  # T = 5
A_size = len(agents)
# Agent constraints
A = []

for index, pair in enumerate(agents):
    A.append(orig_(index) == pair[0])
    A.append(dest_(index) == pair[1])

# Summations using at
# ----------------------------------------------------------------------------------------------------------------------

# The presence of a specific agent, in a specific time is mapped to:
# 1 if there is a true at()
# 0 otherwise

sum3_tmp = [[[If(at_(vertex, agent, time), 1, 0)
              for vertex in range(V_size)]
             for time in range(T + 1)]
            for agent in range(A_size)]

"""
sum3 sums the values of sum3_tmp, obtaining the number of vertices occupied in a specific time and by a specific agent. 
It is used in constraint (3) to avoid that in each time step, the agent occupies more than one position.
"""

sum3 = [[sum(sum3_tmp[agent][time])
         for time in range(T + 1)]
        for agent in range(A_size)]

sum3 = [element for sublist in sum3 for element in sublist]

sum4_tmp = [[[If(at_(vertex, agent, time), 1, 0)
              for agent in range(A_size)]
             for time in range(T + 1)]
            for vertex in range(V_size)]

"""
sum4 sums the values of sum4_tmp, obtaining the number of agents occupying in a specific time a specific vertex. 
It is used in constraint (4) to avoid that in each time step, the vertex is occupied by more than one agent.
"""

sum4 = [[sum(sum4_tmp[vertex][time])
         for time in range(T + 1)]
        for vertex in range(V_size)]

sum4 = [element for sublist in sum4 for element in sublist]

# Summations using pass
# ----------------------------------------------------------------------------------------------------------------------

# Each neighbor of a certain vertex, in a specific time for a specific agent is mapped to:
# 1 if there is a true pass() between it and the vertex set of neighbors
# 0 otherwise
sum5_tmp = [[[list(map(lambda n: If(pass_(vertex, n, agent, time), 1, 0), edges[vertex]))
              for vertex in range(V_size)]
             for time in range(T)]
            for agent in range(A_size)]

"""
sum5 sums the values of sum5_tmp, obtaining the number of movements from the vertex to its neighbors, in a specific 
time, for a specific agent. It is used in constraint (5) to avoid that in each time step, the agent at a certain 
position moves to a not allowed vertex or to more than one neighbor.
"""


sum5 = [[[sum(sum5_tmp[agent][time][vertex])
          for vertex in range(V_size)]
         for time in range(T)]
        for agent in range(A_size)]

"""
# Each agent is mapped to the sum of pass() on both vertices of certain arc, in a specific time
sum7_tmp = [[[[If(pass_(vertex, neighbor, agent, time), 1, 0) + If(pass_(neighbor, vertex, agent, time), 1, 0)
               for agent in range(A_size)]
              for time in range(T)]
             for neighbor in edges[vertex]]
            for vertex in range(V_size)]
"""
"""
sum7 sums the values of sum7_tmp over the agents, obtaining the number of movements at a specific time step on both 
directions of a certain arc. It is used in constraint (7) to avoid that in each time step, agents swap their positions.
"""
"""
sum7 = [[[sum(sum7_tmp[vertex][neighbor][time])
          for time in range(T)]
         for neighbor in range(len(edges[vertex]))]
        for vertex in range(V_size)]
"""

# ======================================================================================================================
# Constraints
# ======================================================================================================================

# vertex
x = Int('x')
y = Int('y')
# agent
a = Int('a')
# time step
t = Int('t')

s = Solver()

# TODO: From the paper, it seems to not deal correctly arcs from and to the same vertex
"""
# Two agents can't occupy two opposite arcs at the same time (no-swap constraint) (7)
s.add([sum7[vertex][neighbor][time] <= 1
       for vertex in range(V_size)
       for time in range(T)
       for neighbor in range(len(edges[vertex]))])
"""

# Start position (1)
s.add([ForAll([a],
              Implies(
                  And(a >= 0, a < A_size),
                  at_(orig_(a), a, 0))
              )])

# Final position (2)
s.add([ForAll([a],
              Implies(
                  And(a >= 0, a < A_size),
                  at_(dest_(a), a, T))
              )])

# Each agent occupies at most one node (3)
s.add([vertex <= 1 for vertex in sum3])

# Every vertex is occupied by at most one agent (4)
s.add([agent <= 1 for agent in sum4])

# If an agent is in a node it needs to leave by one of the outgoing arcs (5)
s.add([Implies(at_(vertex, agent, time), sum5[agent][time][vertex] == 1)
       for vertex in range(V_size)
       for time in range(T)
       for agent in range(A_size)])

# If an agent is using an arc, it needs to arrive at the corresponding node in the next time step (6)
s.add([ForAll([x, y, a, t],
              Implies(
                  And(x >= 0, x < V_size, y >= 0, y < V_size, t >= 0, t <= T - 1, a >= 0, a < A_size, arc_(x, y), pass_(x, y, a, t)),
                  at_(y, a, t + 1)
              ))])

# Two agents can't occupy two opposite arcs at the same time (no-swap constraint) (7)
s.add([
    Implies(
        agent1 != agent2,
        And(
            Not(And(pass_(vertex, neighbor, agent1, time), pass_(neighbor, vertex, agent2, time))),
            Not(And(pass_(vertex, neighbor, agent2, time), pass_(neighbor, vertex, agent1, time)))
        )
    )
    for agent2 in range(A_size)
    for agent1 in range(A_size)
    for vertex in range(V_size)
    for time in range(T)
    for neighbor in edges[vertex]])

# Instance constraints
s.add(E + A)

sep = "============================="
print(sep + "\nAssertions:")
print(s.assertions())
print(sep + "\nStatistics:")
print(s.statistics())

print(s.check())
if s.check() == sat:
    model = s.model()
    # print(sep + "\nModel:")
    # print(model)

    print(sep + "\nPaths:")
    for agent in range(A_size):
        print("Agent %d:" % agent)
        for time in range(T + 1):
            for vertex in range(V_size):
                r = model.evaluate(at_(vertex, agent, time))
                if is_true(r):
                    print("at(%d, %d, %d)" % (vertex, agent, time))

    print(sep + "\nMovements:")
    for agent in range(A_size):
        print("Agent %d (until T - 1 steps):" % agent)
        for time in range(T):
            for vertex in range(V_size):
                for neighbor in edges[vertex]:
                    r = model.evaluate(pass_(vertex, neighbor, agent, time))
                    if is_true(r):
                        print("pass(%d, %d, %d, %d)" % (vertex, neighbor, agent, time))

# ----------------------------------------------------------------------------------------------------------------------
