import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import animation

from environments.environments import environments, generate_dungeon


def animation_update(frame_number, graph, agents_path, seed, ax):
    """
    Function called to update the frames in the animation

    :param frame_number: frame identifier starting from zero
    :param graph: the graph
    :param agents_path: the list of agents paths as lists
    :param seed: the seed used to draw the nodes in the same position
    :param ax: the matplotlib axes

    """
    ax.clear()

    # Modify integer values to tuples containing node index and agent identifier
    # The current node occupied by each agent
    agents_node = list(map(lambda x: x[frame_number], agents_path))
    relabel_map = dict()
    for n in graph.nodes():
        # Get all agents in that node as indices
        indices = [i for i, x in enumerate(agents_node) if x == n[0]]
        assert len(indices) <= 1

        if len(indices) == 1:
            relabel_map[(n[0], n[1])] = (n[0], "%d" % indices[0])
            graph.nodes[n]['color'] = 'r'
        else:
            relabel_map[(n[0], n[1])] = (n[0], "")
            graph.nodes[n]['color'] = 'g'

    graph = nx.relabel_nodes(graph, relabel_map)
    layout = nx.spring_layout(graph, seed=seed)

    # create a list for each node of its color
    colors = [node[1]['color'] for node in graph.nodes(data=True)]

    nx.draw(graph, with_labels=True, node_color=colors, pos=layout, ax=ax)

    # Set the title
    ax.set_title("Frame %d" % frame_number)


def movement_animation(graph, agent_paths, seed):
    """
    Produce an animation on a given graph of given paths

    :param graph: the graph
    :param agent_paths: the list of agents paths as lists
    :param seed: the seed used to draw the nodes in the same position
    """

    if not all(map(lambda i: len(i) == len(agent_paths[0]), agent_paths)):
        raise ValueError("All agents should have a path of the same length.")

    # Build plot
    fig, ax = plt.subplots(figsize=(10, 10))

    # Modify integer values to tuples containing node index and agent identifier
    # The current node occupied by each agent
    agents_node = list(map(lambda x: x[0], agent_paths))
    relabel_map = dict()
    for n in graph.nodes():
        # Get all agents in that node as indices
        indices = [i for i, x in enumerate(agents_node) if x == n]
        assert len(indices) <= 1

        if len(indices) == 1:
            relabel_map[n] = (n, "%d" % indices[0])
        else:
            relabel_map[n] = (n, "")

    graph = nx.relabel_nodes(graph, relabel_map)

    ani = animation.FuncAnimation(fig, animation_update, frames=len(agent_paths[0]), interval=1500,
                                  fargs=(graph, agent_paths, seed, ax))

    # ani.save('animation_1.gif', writer='imagemagick')

    plt.show()


# Sample data
SEED = 42

a0 = [14, 13, 12, 13, 14, 11, 19, 19]
a1 = [17, 14, 11, 19, 18, 3, 4, 1]

_, _, g = environments(generate_dungeon, 2, 40, rooms_num=2, rooms_size_min=3,
                       rooms_size_max=3, corridor_length_min=2, corridor_length_max=2,
                       seed=SEED)

movement_animation(g, [a0, a1], SEED)
