import numpy as np

def isSquare(mat):

    """
    :param mat: a matrix of any dimension
    :return: if the matrix is true, it returns true, else returns false
    """
    return all(len(row) == len(mat) for row in mat)

def num_rows(mat):

    """
    :param mat: any dimensional matrix
    :return: the number of rows in the matrix
    """
    return len(mat)


def num_cols(mat):
    """
    :param mat: any dimensional matrix
    :return: the number of columns in the matrix
    """
    return len(mat[0])

def min_mat(mat):

    """
    :param mat: a 2D matrix
    :return: returns the minimum value in the matrix
    """
    arr = np.array(mat)
    return np.min(arr)

