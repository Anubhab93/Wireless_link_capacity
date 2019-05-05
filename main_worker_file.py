import math
import wireless_apartments as wa
import wireless_singlehouse as ws
import matplotlib.pyplot as plt
import configparser
import networkx as nx

def draw_graph(node_list, edge_list):

    G = nx.Graph()
    G.add_nodes_from(node_list)
    G.add_edges_from(edge_list)
    all_node_degrees = list(G.degree(node_list))
    sum_degree = 0
    for (u,v) in all_node_degrees:
        sum_degree += float(v)
    print("Average node degree: {}".format(sum_degree/len(node_list)))
    print(len(G))
    #nx.draw_shell(G, with_labels=True, node_size=200)
    #plt.savefig('apartment_high.png')
    #plt.show()
    if nx.is_connected(G):
        print("graph is being saved")
        print(len(G))
        nx.write_yaml(G, 'singlehouse_extreme.yaml')

def count_building_numbers(stlen, bw):

    """
    :param stlen: length of the street
    :param bw: width of the building
    :return: total number of building assuming buildings are on both sides of the road
    """
    bn = math.floor(stlen/bw)  # number of buildings on each side of the road
    return 2*bn


def main():

    config = configparser.ConfigParser()
    config.read('config.ini')
    st_length = float(config['STREET']['StreetLength'])
    st_w = float(config['STREET']['StreetWidth'])
    b_w = float(config['BUILDING']['BuildingWidth'])
    a_h = float(config['BUILDING']['FloorHeight'])
    nf = int(config['BUILDING']['FloorNumbers'])
    txp = float(config['ROUTER']['TxPower'])
    rsp = float(config['ROUTER']['Speed'])
    rsp = rsp * 10**6
    cbtrt = float(config['CONTENT']['Bitrate'])
    cbtrt = cbtrt * 1000
    thr = float(cbtrt/rsp)
    bn = count_building_numbers(stlen=st_length, bw=b_w) # total number of buildings on both sides of the road
    scenrsh = config['SCENARIO'].getboolean('SingleHouse')
    scenra = config['SCENARIO'].getboolean('Apartment')
    if scenrsh:
        print("Singlehouse scenario selected")
        edge_list = ws.wireless_singlehouse_graph_info(st_w, b_w, bn, txp, thr)
        node_list = [x for x in range(bn)]
        draw_graph(node_list, edge_list)
    if scenra:
        print("Apartment scenario selected")
        edge_list = wa.wireless_apartments_graph_info(st_w, b_w, bn, nf, a_h, txp, thr)
        node_list = [x for x in range(bn*nf)]
        draw_graph(node_list, edge_list)

if __name__ == "__main__":

    main()
