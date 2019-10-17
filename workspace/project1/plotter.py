# plotter.py
import networkx as nx
import matplotlib.pyplot as plt

def plot_graph(G, show=False):
    fig = plt.figure()
    pos = nx.layout.spring_layout(G)
    labels =nx.draw_networkx_labels(G,pos)
    # nodes = nx.draw_networkx_nodes(G, pos, node_color='blue', alpha=0.5, node_size = 600)
    nx.draw(G,pos, node_size=500)

    # edges = nx.draw_networkx_edges(G, pos, arrows=True,
                               # arrowsize=10, width=2)

    # nx.draw(G,with_labels=True, alpha=0.5)
    # pdb.set_trace()
    if show:
        plt.show()
    return fig
