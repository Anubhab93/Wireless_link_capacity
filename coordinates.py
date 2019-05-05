from scipy.spatial import distance
import sys

def get_all_coordinates(sw, bw, bn, nf, fh):

    """
    :param sw: width of the street (in meter)
    :param bw: width of a single building (in meter)
    :param bn: total number of building (counting both sides of the road) (in meter)
    :param nf: number of floors in each building
    :param fh: height of each floor
    :return: calculate and return a 3D array/matrix that contains the distance between any two houses (in meter)
    """
    total_nodes = bn * nf
    node_eachside = int(total_nodes / 2)  # number of buildings on eaach side of the road
    xcords = [float(bw) / 2] * nf  # taking the coordinates of the centers only
    j = nf
    while (j < node_eachside):
        xcrd = [xcords[j - 1] + bw]*nf # coordinates of each block
        for item in xcrd:
            xcords.append(item)
        j += nf
    for i in range(len(xcords)):
        xcords.append(xcords[i])
    ycords = [0] * node_eachside
    for j in range(node_eachside):
        val = sw + bw  # assuming buildings are square, so building length = building width
        ycords.append(float(val))
    zcords = []
    for j in range(bn):
        for k in range(nf):
            hgt = k*fh  # height of each floor w.r.t. to the ground floor
            zcords.append(hgt)
    if len(xcords) != len(ycords):
        sys.exit("X and Y coordinates array are not of same length")
    elif len(ycords) != len(zcords):
        sys.exit("Z and Y coordinates array are not of same length")
    elif len(xcords) != len(zcords):
        sys.exit("Z and X coordinates array are not of same length")
    else:
        all_coordinates = []
        all_coordinates.append(xcords)
        all_coordinates.append(ycords)
        all_coordinates.append(zcords)
        return all_coordinates

def get_distance_matrix(all_coords):

    """
    :param all_coords: 3D coordinates of the nodes
    :return: distance between any two node
    """
    xcoords = all_coords[0]
    ycoords = all_coords[1]
    zcoords = all_coords[2]
    bn = len(xcoords)
    distance_mat = [[0 for col in range(bn)] for row in range(bn)]
    count = 0
    while count < (bn-1):
        j = count + 1
        while j < bn:
            a = (xcoords[count], ycoords[count], zcoords[count])
            b = (xcoords[j], ycoords[j], zcoords[j])
            distance_mat[count][j] = round(distance.euclidean(a, b), 2)
            j += 1
        count += 1
    for i in range(0, bn):
        for j in range(0, bn):
            if (i != j):
                distance_mat[j][i] = distance_mat[i][j]
    return distance_mat

if __name__ == "__main__":

    sw = 1
    bw = 1
    bn = 4
    nf = 2
    fh = 1
    allc = get_all_coordinates(sw, bw, bn, nf, fh)
    xcoords = allc[0]
    ycoords = allc[1]
    zcoords = allc[2]
    bn = len(xcoords)
    for j in range(bn):
        print("({},{},{})".format(xcoords[j], ycoords[j], zcoords[j]))
    dm = get_distance_matrix(allc)
    for j in range(len(dm)):
        print(dm[j])
