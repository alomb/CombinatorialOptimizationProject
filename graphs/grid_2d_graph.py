import networkx as nx
import matplotlib.pyplot as plt


def generate_grid_2d_graph(rows, columns, agents):

    graph = nx.grid_2d_graph(rows, columns)
    graph = nx.convert_node_labels_to_integers(graph)

    shortest_paths = []

    for agent in agents:
        shortest_paths.append(nx.shortest_path_length(graph, source=agent[0], target=agent[1]))

    graph = nx.convert_node_labels_to_integers(graph)

    """
    Generation of edges as OrderedDict
    
    edges_Z3 = []

    for node, neighbors in G.adj.items():
        edges_Z3.insert(node, OrderedDict())
        for neighbor, _ in neighbors.items():
            edges_Z3[node][neighbor] = None
    
    """

    edges = []

    for node, neighbors in graph.adj.items():
        edges.insert(node, set())
        edges[node].add(node)
        for neighbor, _ in neighbors.items():
            edges[node].add(neighbor)

    [print(str(node) + ": " + str(neighbors)) for node, neighbors in enumerate(edges)]
    print(agents)

    nx.draw(graph, with_labels=True)
    plt.show()

    return edges, min(shortest_paths)
