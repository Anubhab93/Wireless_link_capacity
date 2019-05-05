import numpy as np
import sys
from scipy.spatial import distance
import math_ops


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
        #ldb = np.random.normal(loc=0, scale=5.06)
        ldb = -4.12
        loss = (21.2 * np.log10(d)) + 29.2 + (21.1 * np.log(2.4)) + ldb +(b+1) * 15
        return loss
    except ValueError as ex:
        print("Error in calculating total path loss for signle houses")
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

def calculate_distance_matrix(sw, bw, bn):

    """
    :param sw: width of the street (in meter)
    :param bw: width of a single building (in meter)
    :param bn: total number of building (counting both sides of the road) (in meter)
    :return: calculate and return a 2D array/matrix that contains the distance between any two houses (in meter)
    """

    distance_mat = [[0 for col in range(bn)] for row in range(bn)]
    bn_eachside = int(bn/2)  # number of buildings on eaach side of the road
    xcords = [float(bw)/2]  # taking the coordinates of the centers only
    j = 1
    while(j < bn_eachside):
        xcords.append(xcords[j - 1] + bw)
        j += 1
    for i in range(len(xcords)):
        xcords.append(xcords[i])
    ycords = [0] * bn_eachside
    for j in range(bn_eachside):
        val = sw + bw   # assuming buildings are square, so building length = building width
        ycords.append(float(val))
    count = 0
    while count < bn:
        j = count + 1
        while j < bn:
            a = (xcords[count], ycords[count])
            b = (xcords[j], ycords[j])
            distance_mat[count][j] = round(distance.euclidean(a, b),2)
            j += 1
        count += 1
    for i in range(0, bn):
        for j in range(0, bn):
            if (i != j):
                distance_mat[j][i] = distance_mat[i][j]
    return distance_mat


def calculate_building_intersection_matrix(bn):

    """
    :param bn: total number of buildings on both sides
    :return: matrix of number of buildings between any two building
    """

    int_mat = [[0 for col in range(bn)] for row in range(bn)]
    bn_eachside = int(bn/2)
    i = 0
    while i < (bn_eachside - 1):
        j = i + 2
        bval = 1
        while j < bn_eachside:
            int_mat[i][j] = bval
            bval += 1
            j += 1
        i += 1
    for i in range(0, bn_eachside):
        for j in range(0, bn_eachside):
            if (i != j):
                int_mat[j][i] = int_mat[i][j]
    i = bn_eachside
    while i < (bn - 1):
        j = i + 2
        bval = 1
        while j < bn:
            int_mat[i][j] = bval
            bval += 1
            j += 1
        i += 1
    for i in range(bn_eachside, bn):
        for j in range(bn_eachside, bn):
            if (i != j):
                int_mat[j][i] = int_mat[i][j]
    return int_mat

def calculate_link_capacity_matrix(dist_mat, intersection_mat, tx_power):

    """
    :param dist_mat: distance matrix returned from calculate_distance_matrix method
    :param intersection_mat: intersection matrix returned from calculate_building_intersection_matrix method
    :param tx_power: tx power in dBm
    :return: link capacity matrix, that contains link capacity between any two houses
    """

    if(math_ops.isSquare(dist_mat)==False):
        sys.exit("the distance matrix is not square. Please check again and try")
    elif(math_ops.isSquare(intersection_mat)==False):
        sys.exit("the intersection matrix is not square. Please check again and try")
    elif(math_ops.num_rows(dist_mat)!= math_ops.num_rows(intersection_mat)):
        sys.exit("The dimensions of distance and interseection matrix do not match")
    else:
        n_house = math_ops.num_rows(dist_mat)
        link_capacity_matrix = [[0 for col in range(n_house)] for row in range(n_house)]
        for i in range(0, n_house):
            for j in range(i+1, n_house):
                pl = calculate_pathloss_for_residential_area(dist_mat[i][j], intersection_mat[i][j])
                link_capacity_matrix[i][j] = calculate_link_capacity(tx_power, pl)
        for i in range(0, n_house):
            for j in range(i+1, n_house):
                link_capacity_matrix[j][i] = link_capacity_matrix[i][j]
        return link_capacity_matrix

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
            if(i>j):
                if(lnk_mat[i][j]> threshold):
                    l = []
                    l.append(i)
                    l.append(j)
                    edge_list.append(tuple(l))
    return edge_list

def wireless_singlehouse_graph_info(sw, bw, bn, txp, thr):

    """
    :param sw: width of the street (in meter)
    :param bw: width of a building (in meter)
    :param bn: number of buildings in total on both sides of street
    :param txp: trnsmission power of router
    :param thr: threshold, it is the ratio of = video_bitrate/B (bandwidth of the router).
    if min reqd bitrate is - 700 kbps, B - 100 Mbps, then thr = 0.007
    :return: list of edges of the graph of singlehouses
    """

    dst_mat = calculate_distance_matrix(sw=sw, bw=bw, bn=bn)
    ints_mat = calculate_building_intersection_matrix(bn=bn)
    l_mat = calculate_link_capacity_matrix(dst_mat, ints_mat, tx_power=txp)
    edge_list = create_graph_edges(bn, l_mat, thr)
    return edge_list



if __name__ == "__main__":

    print(wireless_singlehouse_graph_info(sw=20, bw=4, bn=10, txp=25, thr=0.0007))