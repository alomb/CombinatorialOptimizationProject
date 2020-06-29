from z3 import *

# ======================================================================================================================
# Functions
# ======================================================================================================================

# arc(x, y)
# x = src node
# y = dst node
# a directed arc exists between x and y
arc_ = Function('arc', IntSort(), IntSort(), BoolSort())

# orig(a)
# a = agent
# map agent a to its initial position
orig_ = Function('orig', IntSort(), IntSort())

# dest(a)
# a = agent
# map agent a to its final position
dest_ = Function('dest', IntSort(), IntSort())

# at(x, a, t)
# x = vertex
# a = agent
# t = time step
at_ = Function('at', IntSort(), IntSort(), IntSort(), BoolSort())

# pass(x, y, a, t)
# x = source vertex
# y = destination vertex
# a = agent
# t = time step
pass_ = Function('pass', IntSort(), IntSort(), IntSort(), IntSort(), BoolSort())

# ======================================================================================================================
# Set of variables
# ======================================================================================================================

# Graph
# ----------------------------------------------------------------------------------------------------------------------

edges = [{0, 1}, {1, 0}, {2}]
V_size = len(edges)
E = []

for index, neighbors in enumerate(edges):
    for neighbor in neighbors:
        E.append(arc_(index, neighbor))

E_size = len(E)

# Time steps (from 0 to T_size - 1)
# ----------------------------------------------------------------------------------------------------------------------

T_size = 2

# Agents (from 0 to A_size - 1)
# ----------------------------------------------------------------------------------------------------------------------

A_size = 2

# Summations using at
# ----------------------------------------------------------------------------------------------------------------------

# Sum over vertices (SV)
# The presence of a specific agent, in a specific time is mapped to:
# 1 if there is a true at()
# 0 otherwise

SV_temp = [[[If(at_(vertex, agent, time), 1, 0)
             for vertex in range(V_size)]
            for time in range(T_size)]
           for agent in range(A_size)]

"""
SV sums the values of SV_temp, obtaining the number of vertices occupied in a specific time and by a specific agent. 
It is used in constraint (3) to avoid that in each time step, the agent occupies more than one position.
"""

SV = [[sum(SV_temp[agent][time])
       for time in range(T_size)]
      for agent in range(A_size)]

SV = [element for sublist in SV for element in sublist]

# Sum over agents (SA)

SA_temp = [[[If(at_(vertex, agent, time), 1, 0)
             for agent in range(A_size)]
            for time in range(T_size)]
           for vertex in range(V_size)]

"""
SA sums the values of SA_temp, obtaining the number of agents occupying in a specific time a specific vertex. 
It is used in constraint (4) to avoid that in each time step, the vertex is occupied by more than one agent.
"""

SA = [[sum(SA_temp[vertex][time])
       for time in range(T_size)]
      for vertex in range(V_size)]

SA = [element for sublist in SA for element in sublist]

# Summations using pass
# ----------------------------------------------------------------------------------------------------------------------

# Each neighbor of a certain vertex, in a specific time for a specific agent is mapped to:
# 1 if there is a true pass() between it and the vertex set of neighbors
# 0 otherwise
SE_temp = [[[list(map(lambda n: If(pass_(vertex, n, agent, time), 1, 0), edges[vertex]))
             for vertex in range(V_size)]
            for time in range(T_size)]
           for agent in range(A_size)]

"""
SE sums the values of SE_temp, obtaining the number of movements from the vertex to its neighbors, in a specific time, 
for a specific agent. It is used in constraint (5) to avoid that in each time step, the agent at a certain position 
moves to a not allowed vertex or to more than one neighbor.
"""

SE = [[[sum(SE_temp[agent][time][vertex])
        for vertex in range(V_size)]
       for time in range(T_size)]
      for agent in range(A_size)]

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

# Start position (1)
s.add([ForAll([a],
              Implies(
                  And(a >= 0, a < A_size), at_(orig_(a), a, 0))
              )])

# Final position (2)
s.add([ForAll([a],
              Implies(
                  And(a >= 0, a < A_size), at_(dest_(a), a, T_size - 1))
              )])

# Each agent occupies at most one node (3)
s.add([sv <= 1 for sv in SV])

# Every node is occupied by at most one agent (4)
s.add([sa <= 1 for sa in SA])

# If an agent is in a node it needs to leave by one of the outgoing arcs (5)
s.add([Implies(at_(vertex, agent, time), SE[agent][time][vertex] == 1)
       for vertex in range(V_size)
       for time in range(T_size)
       for agent in range(A_size)])

# If an agent is using an arc, it needs to arrive at the corresponding node in the next time step (6)
s.add([ForAll([x, y, a, t],
              Implies(
                  And(x >= 0, x < V_size, y >= 0, y < V_size, t >= 0, t < T_size - 1, a >= 0, a < A_size, arc_(x, y)),
                  Implies(
                      pass_(x, y, a, t),
                      at_(y, a, t + 1)
                  )
              ))])

# Two agents can't occupy two opposite arcs at the same time (no-swap constraint) (7)

# TODO

# Instance constraints
s.add(
    E + [
        # Agent 0
        orig_(0) == 0,
        dest_(0) == 0,
        at_(orig_(0), 0, 0),
        # TODO: Check if necessary
        # at_(V[1], A[0], T[0]) == False,

        # Agent 1
        orig_(1) == 1,
        dest_(1) == 1,
        at_(orig_(1), 1, 0),
    ]
)

if s.check() == sat:
    print(s.model())

# ----------------------------------------------------------------------------------------------------------------------
