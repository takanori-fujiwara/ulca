from scipy.linalg import svd


def find_best_rotate(Z_prev, Z):
    U, s, Vh = svd(Z_prev.T @ Z)
    R = Vh.T @ U.T
    return R
