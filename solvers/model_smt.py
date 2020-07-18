from z3 import *

# ==================================================================================================================
# Z3 Functions
# ==================================================================================================================

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


def run_Z3(edges, agents, makespan):
    """
    Create a MAPF solver using Z3Py.

    :param edges: list of OrderedDict containing for each agent (whose identifier is the index of this list) its
    neighbors
    :param agents: list of tuples containing origins and destinations
    :param makespan: the minimal time step that satisfies the problem
    :return True when a plan has been found, time to build the model, memory usage, number of conflicts and decisions
    """
    import time

    edges_len = len(edges)
    agents_len = len(agents)

    if edges_len <= 0:
        raise ArgumentError("The graph must not be empty")
    if any([vertex not in range(edges_len) for neighbors in edges for vertex in neighbors]):
        raise ArgumentError("Neighbors of nodes must be valid vertices")
    if agents_len <= 0:
        raise ArgumentError("The number of agents must be at least one")
    if any([agent[0] not in range(edges_len) or agent[1] not in range(edges_len) for agent in agents]):
        raise ArgumentError("Agents' destinations and origins must be at valid vertices")
    if makespan < 0:
        raise ArgumentError("The makespan must be greater or equal than zero")

    # ==================================================================================================================
    # Variables and summations
    # ==================================================================================================================

    start_time = time.time()
    # set_param('parallel.enable', True)
    # set_param('verbose', 10)
    s = Solver()

    # Edges definitions
    for index, neighbors in enumerate(edges):
        for neighbor in neighbors:
            s.add((arc_(index, neighbor)))

    # Origins and destinations definitions
    for index, pair in enumerate(agents):
        s.add(orig_(index) == pair[0])
        s.add(dest_(index) == pair[1])

    # Summations involving at
    # ------------------------------------------------------------------------------------------------------------------

    # The presence of a specific agent, in a specific time is mapped to:
    # 1 if there is a true at()
    # 0 otherwise

    sum3_tmp = [[[If(at_(vertex, agent, time), 1, 0)
                  for vertex in range(edges_len)]
                 for time in range(makespan + 1)]
                for agent in range(agents_len)]

    """
    sum3 sums the values of sum3_tmp, obtaining the number of vertices occupied in a specific time and by a specific 
    agent. It is used in constraint (3) to avoid that in each time step, the agent occupies more than one position.
    """

    sum3 = [[sum(sum3_tmp[agent][time])
             for time in range(makespan + 1)]
            for agent in range(agents_len)]

    sum3 = [element for sublist in sum3 for element in sublist]

    sum4_tmp = [[[If(at_(vertex, agent, time), 1, 0)
                  for agent in range(agents_len)]
                 for time in range(makespan + 1)]
                for vertex in range(edges_len)]

    """
    sum4 sums the values of sum4_tmp, obtaining the number of agents occupying in a specific time a specific vertex. 
    It is used in constraint (4) to avoid that in each time step, the vertex is occupied by more than one agent.
    """

    sum4 = [[sum(sum4_tmp[vertex][time])
             for time in range(makespan + 1)]
            for vertex in range(edges_len)]

    sum4 = [element for sublist in sum4 for element in sublist]

    # Summations involving pass
    # ------------------------------------------------------------------------------------------------------------------

    # Each neighbor of a certain vertex, in a specific time for a specific agent is mapped to:
    # 1 if there is a true pass() between it and the vertex set of neighbors
    # 0 otherwise
    sum5_tmp = [[[list(map(lambda n: If(pass_(vertex, n, agent, time), 1, 0), edges[vertex]))
                  for vertex in range(edges_len)]
                 for time in range(makespan)]
                for agent in range(agents_len)]

    """
    sum5 sums the values of sum5_tmp, obtaining the number of movements from the vertex to its neighbors, in a 
    specific time, for a specific agent. It is used in constraint (5) to avoid that in each time step, the agent at 
    a certain position moves to a not allowed vertex or to more than one neighbor.
    """

    sum5 = [[[sum(sum5_tmp[agent][time][vertex])
              for vertex in range(edges_len)]
             for time in range(makespan)]
            for agent in range(agents_len)]

    # Each agent is mapped to the sum of pass() on both vertices of certain arc, in a specific time
    sum7_tmp = [[[[If(pass_(vertex, neighbor, agent, time), 1, 0) + If(pass_(neighbor, vertex, agent, time), 1, 0)
                   if vertex != neighbor else 0
                   for agent in range(agents_len)]
                  for time in range(makespan)]
                 for neighbor in edges[vertex]]
                for vertex in range(edges_len)]

    """
    sum7 sums the values of sum7_tmp over the agents, obtaining the number of movements at a specific time step on 
    both directions of a certain arc. It is used in constraint (7) to avoid that in each time step, agents swap 
    their positions.
    """

    sum7 = [[[sum(sum7_tmp[vertex][neighbor][time])
              for time in range(makespan)]
             for neighbor in range(len(edges[vertex]))]
            for vertex in range(edges_len)]

    # Vertices
    x = Int('x')
    y = Int('y')
    # Agent
    a = Int('a')
    # Time step
    t = Int('t')

    # ==================================================================================================================
    # Constraints
    # ==================================================================================================================

    # Agent variable constraint
    s.add([And(a >= 0, a < agents_len)])

    # (1) Start position
    s.add([ForAll([a], at_(orig_(a), a, 0))])

    # (2) Final position
    s.add([ForAll([a], at_(dest_(a), a, makespan))])

    # (3) Each agent occupies at most one node
    s.add([vertex <= 1 for vertex in sum3])

    # (4) Every vertex is occupied by at most one agent
    s.add([agent <= 1 for agent in sum4])

    # (5) If an agent is in a node it needs to leave by one of the outgoing arcs
    s.add([Implies(at_(vertex, agent, time), sum5[agent][time][vertex] == 1)
           for vertex in range(edges_len)
           for time in range(makespan)
           for agent in range(agents_len)])

    # (6) If an agent is using an arc, it needs to arrive at the corresponding node in the next time step
    s.add([ForAll([x, y, a, t],
                  Implies(
                      And(x >= 0, x < edges_len, y >= 0, y < edges_len, t >= 0, t <= makespan - 1, arc_(x, y),
                          pass_(x, y, a, t)),
                      at_(y, a, t + 1)
                  ))])

    # (7) Two agents can't occupy two opposite arcs at the same time (no-swap constraint)
    s.add([sum7[vertex][neighbor][time] <= 1
           for vertex in range(edges_len)
           for time in range(makespan)
           for neighbor in range(len(edges[vertex]))])

    # ==================================================================================================================
    # Execution
    # ==================================================================================================================

    sep = "-"*50
    print("Makespan %d: %s" % (makespan, s.check()))
    if s.check() == sat:

        statistics = s.statistics()
        model = s.model()

        elapsed_time = time.time() - start_time

        """
        print(sep + "\nAssertions:")
        print(s.assertions())
        print(sep + "\nStatistics:")
        print(statistics)
        print(sep + "\nModel:")
        print(model)
        """

        memory_usage = statistics.get_key_value('max memory')
        number_of_conflicts = statistics.get_key_value('conflicts')
        decisions = statistics.get_key_value('decisions')

        # Print model variables
        """
        print(sep + "\nPaths:")
        for agent in range(agents_len):
            print("Agent %d:" % agent)
            for time in range(makespan + 1):
                for vertex in range(edges_len):
                    r = model.evaluate(at_(vertex, agent, time))
                    if is_true(r):
                        print("at(%d, %d, %d)" % (vertex, agent, time))

        print(sep + "\nMovements:")
        for agent in range(agents_len):
            print("Agent %d (until makespan - 1 steps):" % agent)
            for time in range(makespan):
                for vertex in range(edges_len):
                    for neighbor in edges[vertex]:
                        r = model.evaluate(pass_(vertex, neighbor, agent, time))
                        if is_true(r):
                            print("pass(%d, %d, %d, %d)" % (vertex, neighbor, agent, time))
        """
        paths = []
        # Print the path for each agent
        for agent in range(agents_len):
            paths.append([])
            print("Agent %d:\t" % agent, end="")
            for time in range(makespan + 1):
                for vertex in range(edges_len):
                    r = model.evaluate(at_(vertex, agent, time))
                    if is_true(r):
                        paths[agent].append(vertex)
                        print("%d\t" % vertex, end="")
                        break
            print("")

        print(sep)
        return True, elapsed_time, memory_usage, number_of_conflicts, decisions, paths
    return False, None, None, None, None, None
