import networkx as nx
import matplotlib.pyplot as plt
from collections import OrderedDict

# Generate
rows = 5
columns = 7
G = nx.grid_2d_graph(rows, columns)
G = nx.convert_node_labels_to_integers(G)

# Easy removing of nodes, creation of multiple connected components should be dealt
G.remove_node(3)
G.remove_node(27)

# Restore the values from zero to number of nodes - 1
G = nx.convert_node_labels_to_integers(G)

# Convert for z3
edges = []

for node, neighbors in G.adj.items():
    edges.insert(node, OrderedDict())
    for neighbor, _ in neighbors.items():
        edges[node][neighbor] = None

[print(str(node) + ": " + str(neighbors)) for node, neighbors in enumerate(edges)]

# Draw
nx.draw(G, with_labels=True)
plt.show()
