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
V_size = 3
E_size = 4
T_size = 2

# Time steps
# ----------------------------------------------------------------------------------------------------------------------


# Edges
# ----------------------------------------------------------------------------------------------------------------------

Edges = [{0, 1}, {1, 0}, {2}]
E = []

for index, neighbors in enumerate(Edges):
    for neighbor in neighbors:
        E.append(arc_(index, neighbor))

# Time steps
# ----------------------------------------------------------------------------------------------------------------------

# Agents
# ----------------------------------------------------------------------------------------------------------------------


# Sum of the at(v, a, t) functional symbols for every time step, agent and vertex
# ----------------------------------------------------------------------------------------------------------------------

# Sum over vertices (SV)

SV_temp = [[[If(at_(vertex, agent, time), 1, 0)
             for vertex in range(V_size)]
            for time in range(T_size)]
           for agent in range(A_size)]

SV = [[sum(SV_temp[agent][time])
       for time in range(T_size)]
      for agent in range(A_size)]

SV = [element for sublist in SV for element in sublist]

# Sum over agents (SA)

SA_temp = [[[If(at_(vertex, agent, time), 1, 0)
             for agent in range(A_size)]
            for time in range(T_size)]
           for vertex in range(V_size)]

SA = [[sum(SA_temp[vertex][time])
       for time in range(T_size)]
      for vertex in range(V_size)]

SA = [element for sublist in SA for element in sublist]

# Sum of the pass(x, y, a, t) functional symbols for every time step, agent and arc
# ----------------------------------------------------------------------------------------------------------------------

SE_temp = [[[list(map(lambda n: If(pass_(vertex, n, agent, time), 1, 0), Edges[vertex]))
             for vertex in range(V_size)]
            for time in range(T_size)]
           for agent in range(A_size)]

SE = [[[sum(SE_temp[agent][time][vertex])
        for vertex in range(V_size)]
       for time in range(T_size)]
      for agent in range(A_size)]

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

# If an agent is in a node it needs to leave by one of the outgoing arcs (5)
s.add([Implies(at_(vertex, agent, time), SE[agent][time][vertex] == 1)
      for vertex in range(V_size)
      for time in range(T_size)
      for agent in range(A_size)])

s.add(
    # Graph
    E +

    [
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
        # TODO: Check if necessary
        # at_(V[0], A[1], T[0]) == False,

        # Start position (1)
        ForAll([a], Implies(
            And(a >= 0, a < A_size), at_(orig_(a), a, 0))),

        # Final position (2)
        ForAll([a], Implies(
            And(a >= 0, a < A_size), at_(dest_(a), a, T_size - 1))),

        # Each agent occupies at most one node (3)
        # ForAll(x, Implies(And(x >= 0, x < V_size), SVZ3[x] <= 1)),

        # Every node is occupied by at most one agent (4)
        # ForAll(a, Implies(And(a >= 0, a < A_size), SAZ3[a] <= 1)),

        # If an agent is using an arc, it needs to arrive at the corresponding node in the next time step (6)
        ForAll([x, y, a, t], Implies(
            And(x >= 0, x < V_size, y >= 0, y < V_size, t >= 0, t < T_size - 1, a >= 0, a < A_size, arc_(x, y)),
            Implies(
                pass_(x, y, a, t),
                at_(y, a, t + 1)
            )
        )),

        # Two agents can't occupy two opposite arcs at the same time (no-swap constraint) (7)

        # TODO
    ]
)

print(s.check())
print(s.model())

# ----------------------------------------------------------------------------------------------------------------------
