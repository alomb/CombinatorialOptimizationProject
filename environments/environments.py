import networkx as nx
import matplotlib.pyplot as plt
import random


def environments(number_of_agents, graph_type, **kwargs):
    """
    Create an environment from a NetworkX graph.

    :param number_of_agents: the number of agents
    :param graph_type: one of the following string
        "grid_2d_graph"
        "intersection_graph"
        "karate_club_graph"
    :return: list of agents' positions, list of neighbors for each vertex and the minimum shortest path
    """

    if graph_type == "grid_2d_graph":
        graph = nx.grid_2d_graph(kwargs["rows"], kwargs["columns"])
    elif graph_type == "intersection_graph":
        graph = nx.uniform_random_intersection_graph(kwargs["rows"], kwargs["columns"], 1)
    elif graph_type == "karate_club_graph":
        graph = nx.karate_club_graph()
    else:
        raise ValueError("Graph type not found.")

    graph = nx.convert_node_labels_to_integers(graph)

    edges = []

    for node, neighbors in graph.adj.items():
        edges.insert(node, set())
        edges[node].add(node)
        for neighbor, _ in neighbors.items():
            edges[node].add(neighbor)

    agents = generate_agents(edges, number_of_agents)

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
    """

    if number_of_agents * 2 > len(edges):
        raise ValueError("There are too many agents.")

    agents = []
    available_positions = list(range(len(edges)))

    while len(agents) < number_of_agents:
        agents.append((available_positions.pop(random.randrange(len(available_positions))),
                       available_positions.pop(random.randrange(len(available_positions)))))

    return agents
