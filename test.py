from solvers.model_smt import run_Z3
from solvers.model_cp import run_CPLEX, solving_MAPF
from environments.environments import environments
import time
import numpy as np
import matplotlib.pyplot as plt

# TODO: understand how to get solver statistics to plot them


def test(rows, columns, max_size, graph_type):
    """

    :param rows
    :param columns
    :param max_size
    :param graph_type
    """

    time_CPLEX = []
    time_Z3 = []
    memory_usage_Z3 = []
    memory_usage_CPLEX = []
    number_of_conflicts_Z3 = []
    number_of_conflicts_CPLEX = []
    decisions_Z3 = []
    decisions_CPLEX = []

    size_range = np.linspace(rows, max_size, max_size - rows + 1)

    env_index = 1
    sep = "=" * 50

    while rows <= max_size:

        print(sep)
        print("ENVIRONMENT %d" % env_index)
        print(sep)
        env_index += 1

        makespan = 0
        upper_bound = 2 * rows
        number_of_agents = rows

        agents, edges, shortest_path = environments(number_of_agents, graph_type, rows=rows, columns=columns)

        # ----------------------------------------------------------------------------------------------------------------------

        # Z3
        print(sep)
        print("Z3")
        start = time.time()
        check, memory_usage, number_of_conflicts, decisions = run_Z3(edges, agents, makespan)
        end = time.time()

        while not check and makespan <= upper_bound:
            makespan += 1
            start = time.time()
            check, memory_usage, number_of_conflicts, decisions = run_Z3(edges, agents, makespan)
            end = time.time()

        time_Z3.append(end - start)
        memory_usage_Z3.append(memory_usage)
        number_of_conflicts_Z3.append(number_of_conflicts)
        decisions_Z3.append(decisions)

        # CPLEX
        print(sep)
        print("CPLEX")
        check, ret, num_layers, solve_time, memory_usage, number_of_conflicts, decisions = \
            solving_MAPF(agents, edges, upper_bound, shortest_path)

        if check:
            _, _, solve_time, memory_usage, number_of_conflicts, decisions = run_CPLEX(edges, agents, ret, num_layers)
        else:
            print("CPLEX: unsatisfiable")

        print("="*50)

        time_CPLEX.append(solve_time)
        memory_usage_CPLEX.append(memory_usage)
        number_of_conflicts_CPLEX.append(number_of_conflicts)
        decisions_CPLEX.append(decisions)

        rows += 1
        columns += 1

    """
    Statistics:
    
    time: Solving time
    memory_usage: Memory occupied in MB
    number_of_conflicts: A high number of conflicts could indicate that the solver didn't proceed very goal-directed
    decisions: Number of decision_points
    """

    fig, ax = plt.subplots(2, 2)

    fig.suptitle("Z3 vs CPLEX")
    ax[0, 0].plot(size_range, time_Z3, "-b", label='Z3')
    ax[0, 0].plot(size_range, time_CPLEX, "-r", label='CPLEX')
    ax[0, 0].set_xlabel("Graph's size")
    ax[0, 0].set_ylabel("time")
    plt.yscale('log')

    ax[0, 1].plot(size_range, memory_usage_Z3, "-b", label='Z3')
    ax[0, 1].plot(size_range, memory_usage_CPLEX, "-r", label='CPLEX')
    ax[0, 1].set_xlabel("Graph's size")
    ax[0, 1].set_ylabel("Memory's usage (MB)")
    plt.yscale('log')

    ax[1, 0].plot(size_range, number_of_conflicts_Z3, "-b", label='Z3')
    ax[1, 0].plot(size_range, number_of_conflicts_CPLEX, "-r", label='CPLEX')
    ax[1, 0].set_xlabel("Graph's size")
    ax[1, 0].set_ylabel("Number of conflicts")
    plt.yscale('log')

    ax[1, 1].plot(size_range, decisions_Z3, "-b", label='Z3')
    ax[1, 1].plot(size_range, decisions_CPLEX, "-r", label='CPLEX')
    ax[1, 1].set_xlabel("Graph's size")
    ax[1, 1].set_ylabel("Number of decision points")
    plt.yscale('log')

    plt.legend(loc='best')

    plt.show()


ROWS = 2
COLUMNS = 2
MAX_SIZE = 5

test(ROWS, COLUMNS, MAX_SIZE, "grid_2d_graph")
