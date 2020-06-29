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

A_size = 2
V_size = 2
E_size = 4
T_size = 1

# Vertexes
# ----------------------------------------------------------------------------------------------------------------------

V = Array('V', IntSort(), IntSort())
for i in range(V_size):
    V = Store(V, i, i)

# Edges
# ----------------------------------------------------------------------------------------------------------------------

# Edges = [(0, 1), (0, 0), (1, 1), (1, 0)]
E = [arc_(V[0], V[1]), arc_(V[0], V[0]), arc_(V[1], V[0]), arc_(V[1], V[1])]

# Time steps
# ----------------------------------------------------------------------------------------------------------------------

T = Array('T', IntSort(), IntSort())
for i in range(T_size):
    T = Store(T, i, i)

# Agents
# ----------------------------------------------------------------------------------------------------------------------

A = Array('A', IntSort(), IntSort())
for i in range(A_size):
    A = Store(A, i, i)

# Sum of the at(v, a, t) functional symbols for every time step, agent and vertex
# ----------------------------------------------------------------------------------------------------------------------

# Sum over vertices (SV)

SV_temp = [[[If(at_(V[vertex], A[agent], T[time]), 1, 0)
             for vertex in range(V_size)]
            for time in range(T_size)]
           for agent in range(A_size)]

SV = [[sum(SV_temp[agent][time])
       for time in range(T_size)]
      for agent in range(A_size)]

SV = [element for sublist in SV for element in sublist]

"""
SVZ3 = Array('SVZ3', IntSort(), IntSort())
index = 0
for i in SV:
    SVZ3 = Store(SVZ3, index, i)
    index += 1
"""

# Sum over agents (SA)

SA_temp = [[[If(at_(V[vertex], A[agent], T[time]), 1, 0)
             for agent in range(A_size)]
            for time in range(T_size)]
           for vertex in range(V_size)]

SA = [[sum(SA_temp[vertex][time])
       for time in range(T_size)]
      for vertex in range(V_size)]

SA = [element for sublist in SA for element in sublist]

"""
SAZ3 = Array('SAZ3', IntSort(), IntSort())
index = 0
for i in SA:
    SAZ3 = Store(SAZ3, index, i)
    index += 1
"""

# ======================================================================================================================
# Constraints
# ======================================================================================================================

x = Int('x')
y = Int('y')
a = Int('a')
t = Int('t')

s = Solver()

# Each agent occupies at most one node (3)
s.add([sv <= 1 for sv in SV])
# Every node is occupied by at most one agent (4)
s.add([sa <= 1 for sa in SA])

s.add(
    # Graph
    E +

    [
        # Agent 0
        orig_(A[0]) == V[0],
        dest_(A[0]) == V[0],
        at_(orig_(A[0]), A[0], T[0]),
        # TODO: Check if necessary
        # at_(V[1], A[0], T[0]) == False,

        # Agent 1
        orig_(A[1]) == V[1],
        dest_(A[1]) == V[1],
        at_(orig_(A[1]), A[1], T[0]),
        # TODO: Check if necessary
        # at_(V[0], A[1], T[0]) == False,

        # Start position (1)
        ForAll([a], Implies(
            And(a >= 0, a < A_size), at_(orig_(A[a]), A[a], 0))),

        # Final position (2)
        ForAll([a], Implies(
            And(a >= 0, a < A_size), at_(dest_(A[a]), A[a], T_size - 1))),

        # Each agent occupies at most one node
        # ForAll(x, Implies(And(x >= 0, x < V_size), SVZ3[x] <= 1)),

        # Every node is occupied by at most one agent
        # ForAll(a, Implies(And(a >= 0, a < A_size), SAZ3[a] <= 1)),

        # If an agent is in a node it needs to leave by one of the outgoing arcs (5)

        # TODO

        # If an agent is using an arc, it needs to arrive at the corresponding node in the next time step (6)
        ForAll([x, y, a, t], Implies(
            And(x >= 0, x < V_size, y >= 0, y < V_size, t >= 0, t < T_size - 1, a >= 0, a < A_size, arc_(V[x], V[y])),
            Implies(
                pass_(V[x], V[y], A[a], T[t]),
                at_(V[y], A[a], T[t + 1])
            )
        ))

        # Two agents can't occupy two opposite arcs at the same time (no-swap constraint) (7)

        # TODO
    ]
)

print(s.check())
print(s.model())

# ----------------------------------------------------------------------------------------------------------------------
