import networkx as nx
import matplotlib.pyplot as plt
import random


def environments(rows, columns, number_of_agents, graph):

    if graph == "grid_2d_graph":
        G = nx.grid_2d_graph(rows, columns)
    if graph == "intersection_graph":
        G = nx.uniform_random_intersection_graph(rows, columns, 1)

    G = nx.convert_node_labels_to_integers(G)
    G = nx.convert_node_labels_to_integers(G)

    graph = nx.grid_2d_graph(rows, columns)

    graph = nx.convert_node_labels_to_integers(graph)
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
        shortest_paths.append(nx.shortest_path_length(G, source=agent[0], target=agent[1]))

    [print(str(node) + ": " + str(neighbors)) for node, neighbors in enumerate(edges)]

    nx.draw(graph, with_labels=True)
    plt.show()

    return agents, edges, min(shortest_paths)


def generate_agents(edges, number_of_agents):

    agents = []
    x = []
    y = []
    i = 0

    for agent in range(number_of_agents):
        while len(x) < number_of_agents and len(y) < number_of_agents:
            x_i = random.randint(0, len(edges) - 1)
            y_i = random.randint(0, len(edges) - 1)

            if x_i not in x and y_i not in y:
                x.append(x_i)
                y.append(y_i)

    while i < len(x):
        agents.append((x[i], y[i]))
        i += 1

    return agents