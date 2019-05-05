import numpy as np
import coordinates

def calculate_pathloss_for_residential_area(d, b):

    """
    this model is based on ITU-R. We have assumed that wifi signal will operate at 2.4 GHz.
    :d: d is the distance between from the source house to the destination house
    :b: b is the number of buildings in between these two houses
    it is calculated using the formula
    PL = 10 * alpha * log(d) + beta + 10 * gamma * log(f)+ N(0,sigma) + (k+1) * Building_entry_loss dB
    where 'd' is in meter, 'f' is in GHz and for residential area N is a zero mean gaussian random variable with a std deviation sigma.
    k is the number of buildings that lie in the LoS propagation.
    We are assuming there is no loss for floor as all
    the routers in all the houses are in the same floor.

    values used in the simulations -

    alpha = 2.12, beta = 29.2, gamma = 2.11, sigma = 5.06, building_entry_loss = 15dB for traditional homes

    These values are obtained from the following - ITU-R P.1411-9 &  ITU-R P.2109

    :return: total path loss in in dB
    """
    try:
        ldb = np.random.normal(loc=0, scale=5.06)
        loss = (21.2 * np.log10(d)) + 29.2 + (21.1 * np.log(2.4)) + ldb +(b+1) * 15
        return loss
    except ValueError as ex:
        print("Error in calculating total path loss for signle houses")
        print(ex)

def calculate_pathloss_for_apartments(d):

    """
    We are assuming a pathloss model based on ITU-R P.1238-7 which provides propagation data and prediction method for the planning of indoor radiocommunication systems.
    In this case the pathloss model can be formulated as

    P L = 20 × log f + N × log d + Lf (n) − 28dB

    where f is the operating frequency in MHz, N is the distance power loss coefficient, d is the distance between the sender and the receiver in meter, Lf is the floor penetration
    loss factor in dB and n is the number of floors between the sender and the receiver. For residential area, the value of N is
    given as 28 when f is 2.4 GHz. For apartments, the value of Lf is assumed to be 10 and it is independent of the value of n.

    :return: pathloss in dB
    """

    try:
        loss = (20 * np.log10(2400)) + (28 * np.log10(d)) - 18
        return loss
    except ValueError as ex:
        print("Error in calculating total path loss in apartments")
        print(ex)

def calculate_link_capacity(tx_power, pathloss):

    """
    :param tx_power: power of Tx-antenna in dBm
    :param pathloss: calculated from the above method, in db
    :return: link capacity between any two houses

    link : https://www.lifewire.com/wireless-standards-802-11a-802-11b-g-n-and-802-11ac-816553
    """
    try:
        rx_power = tx_power - pathloss
        rx_power_abs = 10**(rx_power/20)  # converting the power from dBm to absolute value
        max_capacity = np.log2(1 + rx_power_abs)  # normalized w.r.t B
        return max_capacity
    except ValueError as ex:
        print("Error in calculating link capacity")
        print(ex)

def calculate_building_intersection_matrix(bn, nf):

    """
    :param bn: number of buildings (including both sides of the road)
    :param nf: number of floors in each building
    :return: number of buildings that lies between any two nodes
    """
    total_nodes = bn * nf
    node_eachside = int(total_nodes/2)
    int_mat = [[0 for col in range(total_nodes)] for row in range(total_nodes)]
    i = 0
    while i < node_eachside:
        j = i + 1
        while j < node_eachside:
            snode = i
            dnode = j
            s_id = int(snode / nf)
            d_id = int(dnode / nf)
            val = d_id - s_id - 1
            if val < 0:
                val = 0
            int_mat[i][j] = val
            j += 1
        i += 1
    for i in range(0, node_eachside):
        for j in range(node_eachside, total_nodes):
            int_mat[i][j] = 0
    for i in range(node_eachside, total_nodes):
        for j in range(0, node_eachside):
            int_mat[i][j] = 0
    for i in range(0, node_eachside):
        for j in range(0, node_eachside):
            if (i != j):
                int_mat[j][i] = int_mat[i][j]
    i = total_nodes-1
    while i >= node_eachside:
        j = total_nodes - 1
        while j >= node_eachside:
            int_mat[i][j] = int_mat[total_nodes -1 -i][total_nodes - 1 - j]
            j = j - 1
        i = i - 1
    for i in range(node_eachside, total_nodes):
        for j in range(node_eachside, total_nodes):
            if (i != j):
                int_mat[i][j] = int_mat[j][i]
    return int_mat

def check_if_two_nodes_in_same_building(i, j, nf):

    """
    :param i: node id 1
    :param j: node id 2
    :param nf: number of floors in each building
    :return: True, if they are in same building, else False
    """
    s1 = int(i/nf)
    s2 = int(j/nf)
    if s1 == s2:
        return True
    else:
        return False


def calculate_pathloss_matrix(sw, bw, bn, nf, fh):

    """
    :param sw: width of the street (in meter)
    :param bw: width of a single building (in meter)
    :param bn: number of buildings (including both sides of the road)
    :param nf: number of floors in each building
    :param fh: height of each floor
    :return: pathloss in dB between any two floors
    """
    total_nodes = bn * nf
    allc = coordinates.get_all_coordinates(sw, bw, bn, nf, fh)
    dist_mat = coordinates.get_distance_matrix(allc)
    int_mat = calculate_building_intersection_matrix(bn, nf)
    pathloss_mat = [[0 for col in range(total_nodes)] for row in range(total_nodes)]
    i = 0
    while i < total_nodes:
        j = i + 1
        while j < total_nodes:
            # if two nodes are in same building, apply pathloss model 2, otherwie
            # apply pathloss model 1
            if check_if_two_nodes_in_same_building(i, j, nf):
                pathloss_mat[i][j] = calculate_pathloss_for_apartments(d=dist_mat[i][j])
            else:
                pathloss_mat[i][j] = calculate_pathloss_for_residential_area(d=dist_mat[i][j], b= int_mat[i][j])
            j += 1
        i += 1
    for i in range(0, total_nodes):
        for j in range(0, total_nodes):
            if (i != j):
                pathloss_mat[j][i] = pathloss_mat[i][j]
    return pathloss_mat

def calculate_link_capacity_matrix(pathloss_mat, tx_power):

    total_nodes = len(pathloss_mat)
    link_capacity_mat = [[0 for col in range(total_nodes)] for row in range(total_nodes)]
    for i in range(0, total_nodes):
        for j in range(0, total_nodes):
            if (i != j):
                link_capacity_mat[i][j] = calculate_link_capacity(tx_power, pathloss_mat[i][j])
    return link_capacity_mat

def create_graph_edges(n, lnk_mat, threshold):

    """
    :param n: no if users (here number of single houses)
    :param lnk_mat: link capacity matrix
    :param threshold : it is the ratio of = video_bitrate/B (bandwidth of the router)
    :return: based on the link capacity matrix, it returns the tuples where an edge can be formed
    """
    edge_list = []
    for i in range(0,n):
        for j in range(0, n):
            if(lnk_mat[i][j]> threshold):
                l = []
                l.append(i)
                l.append(j)
                edge_list.append(tuple(l))
    return edge_list


def wireless_apartments_graph_info(sw, bw, bn, nf, fh, txp, thr):

    """
    :param sw: width of the street (in meter)
    :param bw: width of a building (in meter)
    :param bn: number of buildings in total on both sides of street
    :param nf: number of floors in each building
    :param fh: height of each floor
    :param txp: trnsmission power of router
    :param thr: threshold, it is the ratio of = video_bitrate/B (bandwidth of the router).
    if min reqd bitrate is - 700 kbps, B - 100 Mbps, then thr = 0.007
    :return: list of edges of the graph of singlehouses
    """

    pathlossmat = calculate_pathloss_matrix(sw, bw, bn, nf, fh)
    l_mat = calculate_link_capacity_matrix(pathlossmat, tx_power=txp)
    edge_list = create_graph_edges(bn*nf, l_mat, thr)
    return edge_list




if __name__ == "__main__":

    bn = 8
    nf = 3
    fh = 3
    sw = 20
    bw = 4
    txp = 25
    thr = 0.0007
    print(wireless_apartments_graph_info(sw, bw, bn, nf, fh, txp, thr))