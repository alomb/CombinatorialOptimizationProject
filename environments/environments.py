import networkx as nx
import matplotlib.pyplot as plt
import random


def environments(graph_function, agents, agents_seed, **kwargs):
    """
    Create an environment from a NetworkX graph.

    :param graph_function: a function that returns a NetworkX graph, can be a customized one or one belonging to
    the wide range of predefined functions of the NetworkX library. Parameters are passed with the named
    argument **kwargs
    :param agents: the number of agents or the list containing origin and destination of each agent. In the former case
    the positions will be computed randomly.
    :param agents_seed: the random seed used for agents generation

    :return list of agents' positions, list of neighbors for each vertex and the minimum and maximum shortest path
    lengths

    :raise may generate an exception if the parameter of the NetworkX graph are not correct ot the number of agents is
    too big
    """

    graph = graph_function(**kwargs)

    graph = nx.convert_node_labels_to_integers(graph)

    edges = []

    for node, neighbors in graph.adj.items():
        edges.insert(node, set())
        edges[node].add(node)
        for neighbor, _ in neighbors.items():
            edges[node].add(neighbor)

    if type(agents) is int:
        agents = generate_agents(edges, agents, agents_seed)
    elif type(agents) is not list:
        raise Exception("agents must be an integer or a list of tuples.")
    else:
        for a in agents:
            if type(a) is not tuple:
                raise Exception("agents must be a list of tuples.")

    shortest_paths = []

    for agent in agents:
        shortest_paths.append(nx.shortest_path_length(graph, source=agent[0], target=agent[1]))

    print("ENVIRONMENT: ")
    [print(str(node) + ": " + str(neighbors)) for node, neighbors in enumerate(edges)]
    print("AGENTS: ")
    print(agents)

    nx.draw(graph, with_labels=True)
    plt.show()

    return agents, edges, min(shortest_paths), max(shortest_paths)


def generate_agents(edges, number_of_agents, seed=None):
    """
    Generate random origin and destination for a given number of agents

    :param edges: the list of neighbors for each vertex
    :param number_of_agents: the number of agents
    :return: a list of length number_of_agents, containing for each agent its origin and destination
    :param seed: the random seed

    :raise an exception when the number of agents is too big to fit in the graph
    """

    if number_of_agents * 2 > len(edges):
        raise ValueError("There are too many agents.")

    agents = []
    available_positions = list(range(len(edges)))
    random.seed(seed)

    while len(agents) < number_of_agents:
        agents.append((available_positions.pop(random.randrange(len(available_positions))),
                       available_positions.pop(random.randrange(len(available_positions)))))

    return agents


def grid_graph_with_obstacles(probability_obstacle, n, m, seed=None):
    """
    Create a grid graph removing some nodes as if they were obstacles

    :param probability_obstacle: probability to remove a node from the initial grd graph
    :param n: number of rows
    :param m: number of columns
    :param seed: the random seed
    :return: a grid graph with obstacles
    """

    graph = nx.grid_2d_graph(n, m)
    to_remove = []
    random.seed(seed)
    for n in graph:
        if random.random() <= probability_obstacle:
            to_remove.append(n)
    graph.remove_nodes_from(to_remove)

    return graph


def generate_dungeon(rooms_num, rooms_size_min, rooms_size_max, corridor_length_min, corridor_length_max, seed=None):

    if rooms_num <= 1 or rooms_size_min <= 1 or rooms_size_max <= 1 or corridor_length_min < 1 or\
            corridor_length_max < 0:
        raise ValueError("Some arguments are not correct")

    random.seed(seed)
    graph = nx.Graph()
    rooms = []
    for r in range(rooms_num):
        rooms.append(nx.grid_2d_graph(random.randint(rooms_size_min, rooms_size_max),
                                      random.randint(rooms_size_min, rooms_size_max)))
        graph = nx.disjoint_union(graph, rooms[r])

    links = [random.choice(list(i)) for i in nx.connected_components(graph)]

    for lnk in range(len(links) - 1):
        path = []
        corridor_length = range(random.randint(corridor_length_min, corridor_length_max))
        for p in corridor_length:
            path.append(max(graph.nodes) + 1 + p)

        nx.add_path(graph, [links[lnk]] + path + [links[lnk + 1]])

    return nx.convert_node_labels_to_integers(graph)
