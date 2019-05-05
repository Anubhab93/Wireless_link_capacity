import networkx as nx
import matplotlib.pyplot as plt

edge_list = [(0,1), (1,2), (2,3), (1,0), (2,1)]
node_list = [0, 1, 2, 3]
G = nx.Graph()
G.add_nodes_from(node_list)
G.add_edges_from(edge_list)

nx.draw(G)
plt.show()