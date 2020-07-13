import networkx as nx
import matplotlib.pyplot as plt
import random


def environments(graph_function, agents, **kwargs):
    """
    Create an environment from a NetworkX graph.

    :param graph_function: a function that returns a NetworkX graph, can be a customized one or one belonging to
    the wide range of predefined functions of the NetworkX library. Parameters are passed with the named
    argument **kwargs
    :param agents: the number of agents or the list containing origin and destination of each agent. In the former case
    the positions will be computed randomly.

    :return list of agents' positions, list of neighbors for each vertex and the minimum shortest path

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
        agents = generate_agents(edges, agents)
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

    """
    nx.draw(graph, with_labels=True)
    plt.show()
    """

    return agents, edges, min(shortest_paths)


def generate_agents(edges, number_of_agents):
    """
    Generate random origin and destination for a given number of agents

    :param edges: the list of neighbors for each vertex
    :param number_of_agents: the number of agents
    :return: a list of length number_of_agents, containing for each agent its origin and destination

    :raise an exception when the number of agents is too big to fit in the graph
    """

    if number_of_agents * 2 > len(edges):
        raise ValueError("There are too many agents.")

    agents = []
    available_positions = list(range(len(edges)))

    while len(agents) < number_of_agents:
        agents.append((available_positions.pop(random.randrange(len(available_positions))),
                       available_positions.pop(random.randrange(len(available_positions)))))

    return agents
