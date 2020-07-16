import re

from docplex.cp.model import *


def run_CPLEX(edges, agents, upper_bound, num_layers):
    """
    Create a MAPF Solver using CPLEX.

    :param edges: list of OrderedDict containing for each agent (whose identifier is the index of this list) its
    neighbors
    :param agents: list of tuples containing origins and destinations
    :param upper_bound: the maximum value that interval variables can assume, it represents the maximum makespan
    possible
    :param num_layers: the number of layers, useful for an agent to visit multiple times a vertex
    :return True when a plan has been found, time to build the model, memory usage, number of conflicts and decisions.
    paths is a list of lists containing paths of each agent.
    """

    model = CpoModel()
    agents_len = len(agents)
    edges_len = len(edges)
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

    A_equal = [[[interval_var(start=(0, upper_bound), end=(0, upper_bound), length=0,
                              name="Ae_%s_%s_%s_%s" % (vertex, vertex, agent, layer), optional=True)
                 for layer in range(num_layers - 1)]
                for agent in range(agents_len)]
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
                    [A_equal[vertex][agent][layer - 1]] +
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
                    [A_equal[vertex][agent][layer]] +
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

    # (11) For each arc (x,x), agent and layer (excluding the last) a traverse implies a Nin in x in the successive
    # layer
    [model.add(if_then(presence_of(A_equal[vertex][agent][layer]), presence_of(Nin[vertex][agent][layer + 1])))
     for vertex in range(edges_len)
     for agent in range(agents_len)
     for layer in range(num_layers - 1)]

    # (12) For each arc (x,x), agent and layer (excluding the last) a traverse implies a Nout in x
    [model.add(if_then(presence_of(A_equal[vertex][agent][layer]), presence_of(Nout[vertex][agent][layer])))
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

    # (16) For each vertex, agent and layer the beginning of a N activity coincides with the start of a Nout one,
    # excluding the case when the vertex it's the agent destination and the layer is the last (already considered
    # in (14))
    [model.add(end_of(N[vertex][agent][layer]) == start_of(Nout[vertex][agent][layer]))
     if pair[1] != vertex or layer != num_layers - 1
     else True
     for layer in range(num_layers)
     for agent, pair in enumerate(agents)
     for vertex in range(edges_len)]

    # (17) Prevent agents to occur at the same node at the same time

    # TDM
    tm_size = num_layers * agents_len
    tm = transition_matrix(tm_size)

    """
    Each vertex has the same TDM and its own no_overlap.
    In the TDM, for each agent in different layers the distance between two N can be at least 0 (default value), whereas
    for different agents must be at least 1.
    
    Example of TDM with 2 agents and 4 layers:
    00001111
    00001111
    00001111
    00001111
    11110000
    11110000
    11110000
    11110000
    """

    for i in range(tm_size):
        for j in range(tm_size):
            if j not in range((i // num_layers) * num_layers, (i // num_layers) * num_layers + num_layers):
                tm.set_value(i, j, 1)

    [model.add(no_overlap(sequence_var([N[vertex][agent][layer]
                                        for agent in range(agents_len)
                                        for layer in range(num_layers)]), tm))
     for vertex in range(edges_len)]

    # (18) Prevent agents from using an arc at the same time (no-swap constraint)
    [model.add(no_overlap([element for sublist in
                           [[A[vertex][neighbor][agent][layer], A[neighbor][vertex][agent][layer]]
                            for agent in range(agents_len)
                            for layer in range(num_layers)] for element in sublist]))
     for vertex in range(edges_len)
     for neighbor in edges[vertex].difference({vertex})]

    # (19) Minimize makespan
    model.add(model.minimize(makespan))

    # try / catch block because model.solve() returns an exception if the problem is unsatisfiable
    result = model.solve(log_output=None)
    solution = result.solution
    solve_time = result.solveTime

    if result.is_solution_optimal():
        memory_usage = result.solver_infos["PeakMemoryUsage"] * pow(10, -6)
        number_of_conflicts = result.solver_infos["FailDepthCount"]
        decisions = result.solver_infos["NumberOfChoicePoints"]
        # Solve model
        print("Solution with makespan %d:" % solution["MKSP"])

        # Print the model variables
        """        
        n_result = dict()
        a_result = dict()
        ae_result = dict()
        
        for name, var in solution.var_solutions_dict.items():
            if type(name) == str and type(var) == CpoIntervalVarSolution and var.is_present():
                # Use regex to extract from the name the type of the variable and the agent involved
                tokens = re.split("_", name)
                identifier = tokens[0]

                if identifier == "N":
                    n_result.setdefault(int(tokens[2]), []).append(var)
                elif identifier == "A":
                    a_result.setdefault(int(tokens[3]), []).append(var)
                elif identifier == "Ae":
                    ae_result.setdefault(int(tokens[3]), []).append(var)

        for agent in range(agents_len):
            print("Agent %d" % agent)
            
            if agent in n_result:
                print_sorted_list_of_intervals(n_result[agent])

            if agent in a_result:
                print_sorted_list_of_intervals(a_result[agent])

            if agent in ae_result:
                print_sorted_list_of_intervals(ae_result[agent])
        """

        # Print the path for each agent

        agents_path = dict()

        for name, var in solution.var_solutions_dict.items():
            if type(name) == str and type(var) == CpoIntervalVarSolution and var.is_present():
                # Use regex to extract from the name the type of the variable, the agent involved and the vertex.
                tokens = re.split("_", name)
                if tokens[0] == "N":
                    # Extract time steps from activity durations
                    duration = -1
                    while duration < var.end - var.start:
                        duration += 1
                        agents_path.setdefault(int(tokens[2]), {})[var.start + duration] = int(tokens[1])

        paths = []
        # Print the steps of each agent
        for a in sorted(agents_path.keys()):
            print("Agent %d:\t" % a, end="")
            paths.append([])
            for key in sorted(agents_path[a].keys()):
                paths[a].append(agents_path[a][key])
                print("%d\t" % agents_path[a][key], end="")
            print("")

        return True, solution["MKSP"], solve_time, memory_usage, number_of_conflicts, decisions, paths

    else:
        return False, -1, solve_time, None, None, None, None


def print_sorted_list_of_intervals(intervals):
    """
    Print the list interval variables sorted in increasing order. Those that start and end before have the precedence.

    :param intervals: the list of interval variables to print
    :return:
    """
    intervals.sort(key=lambda x: x.start + x.end)
    for e in intervals:
        print(e)


def solving_MAPF(agents, edges, upper_bound, shortest_path):
    """
    TODO: condition added num_layers < upper_bound to replace the satisfiability check of PaS algorithm
    Found the correct number of layers and upperbound. It represents the lines 6-12 of the Algorithm1 in the cited
    paper.

    :param agents: list of tuples containing origins and destinations
    :param edges: list of OrderedDict containing for each agent (whose identifier is the index of this list) its
    neighbors
    :param upper_bound: the maximum value that interval variables can assume, it represents the maximum makespan
    possible
    :param shortest_path:
    :return True when a plan has been found, optimal upperbound, optimal number of layers, time to build the model,
     memory usage, number of conflicts and decisions.
    """

    num_layers = 1

    check, ret, solve_time, memory_usage, number_of_conflicts, decisions, _ = \
        run_CPLEX(edges, agents, upper_bound, num_layers)

    while check is False and num_layers < upper_bound:
        check, ret, solve_time, memory_usage, number_of_conflicts, decisions, _ = \
            run_CPLEX(edges, agents, upper_bound, num_layers)
        num_layers += 1

    num_layers = round((ret - shortest_path) / 2 + 1)

    return check, ret, num_layers, solve_time, memory_usage, number_of_conflicts, decisions
