import autograd.numpy as np
import pymanopt
"""
Exaples of cost and projection fuctions to generate linear dimensionality
reduction class with gen_ldr in core.py
Implemented cost function genertors:
    - PCA (gen_cost_pca)
    - LDA (gen_cost_lda)
    - cPCA (gen_cost_cpca)
    - ccPCA (gen_cost_ccpca)
    - ULCA (gen_cost_ulca)
Implemented projection function genertors:
    - Matrix multiplication with data and projection matrix (gen_default_proj)
"""


def gen_default_proj(M):

    def proj(X, *args, **kwargs):
        return X @ M

    return proj


def gen_cost_pca(manifold, X):
    X_c = X - X.mean(axis=0)

    @pymanopt.function.autograd(manifold)
    def cost(M):
        # this is based on Cunningham et al., 2015
        # but probably, using Cov is faster
        return np.linalg.norm(X_c - X_c @ M @ M.T)**2

    return cost


def gen_cost_lda(manifold, X, y):
    X_c = X - X.mean(axis=0)

    all_mean = X_c.mean()  # should be 0
    class_mean = {}
    for label in np.unique(y):
        class_mean[label] = X_c[y == label, :].mean(axis=0)

    X_class_mean = np.zeros(X.shape)
    for label in np.unique(y):
        X_class_mean[y == label, :] = class_mean[label]

    Cov_within = (X_c - X_class_mean).T @ (X_c - X_class_mean)
    Cov_between = (X_class_mean - all_mean).T @ (X_class_mean - all_mean)

    @pymanopt.function.autograd(manifold)
    def cost(M):
        return np.trace(M.T @ Cov_within @ M) / np.trace(M.T @ Cov_between @ M)

    return cost


def gen_cost_regularized_lda(manifold, X, y, gamma=0):
    X_c = X - X.mean(axis=0)

    all_mean = X_c.mean()  # should be 0
    class_mean = {}
    for label in np.unique(y):
        class_mean[label] = X_c[y == label, :].mean(axis=0)

    X_class_mean = np.zeros(X.shape)
    for label in np.unique(y):
        X_class_mean[y == label, :] = class_mean[label]

    Cov_within = (X_c - X_class_mean).T @ (X_c - X_class_mean)
    Cov_between = (X_class_mean - all_mean).T @ (X_class_mean - all_mean)
    Cov_between += gamma * np.identity(Cov_between.shape[0])

    @pymanopt.function.autograd(manifold)
    def cost(M):
        return np.trace(M.T @ Cov_within @ M) / np.trace(M.T @ Cov_between @ M)

    return cost


def gen_cost_cpca(manifold, X_tg, X_bg, alpha=None):
    X_tg_c = X_tg - X_tg.mean(axis=0)
    X_bg_c = X_bg - X_bg.mean(axis=0)
    Cov_tg = X_tg_c.T @ X_tg_c / X_tg_c.shape[0]
    Cov_bg = X_bg_c.T @ X_bg_c / X_bg_c.shape[0]

    @pymanopt.function.autograd(manifold)
    def cost(M):
        return np.trace(M.T @ Cov_bg @ M) / np.trace(M.T @ Cov_tg @ M)

    @pymanopt.function.autograd(manifold)
    def cost_with_alpha(M):
        return np.trace(M.T @ (alpha * Cov_bg - Cov_tg) @ M)

    if alpha:
        return cost_with_alpha
    else:
        return cost


def gen_cost_ccpca(manifold, X_tg, X_bg, alpha=None):
    X = np.vstack((X_tg, X_bg))
    X_c = X - X.mean(axis=0)
    X_bg_c = X_bg - X_bg.mean(axis=0)

    Cov_all = X_c.T @ X_c / X_c.shape[0]
    Cov_bg = X_bg_c.T @ X_bg_c / X_bg_c.shape[0]

    @pymanopt.function.autograd(manifold)
    def cost(M):
        return np.trace(M.T @ Cov_bg @ M) / np.trace(M.T @ Cov_all @ M)

    @pymanopt.function.autograd(manifold)
    def cost_with_alpha(M):
        return np.trace(M.T @ (alpha * Cov_bg - Cov_all) @ M)

    if alpha:
        return cost_with_alpha
    else:
        return cost


def gen_cost_ulca(manifold,
                  X,
                  y,
                  w_tg,
                  w_bg,
                  w_bw,
                  Covs={},
                  alpha=None,
                  centering=True,
                  gamma0=None,
                  gamma1=None):
    labels = np.unique(y)
    _Covs = {}

    # when Covs are provided, covariance computation here will be skipped
    if len(Covs.keys()) == 0:
        if centering:
            X_c = X - X.mean(axis=0)

        class_mean = {}
        for label in labels:
            class_mean[label] = X_c[y == label, :].mean(axis=0)

        X_class_mean = np.zeros(X.shape)
        for label in labels:
            X_class_mean[y == label, :] = class_mean[label]

        all_mean = 0  # this equals to X_c.mean()

        for label in labels:
            # to compute within-cov
            WI = X_c[y == label, :] - X_class_mean[y == label, :]
            # to compute between-cov
            BW = X_class_mean[y == label, :] - all_mean
            n = np.sum(y == label)

            Cov_within = WI.T @ WI / n
            Cov_between = BW.T @ BW / n
            _Covs[label] = {'within': Cov_within, 'between': Cov_between}
    else:
        _Covs = Covs

    _, d = X.shape
    Cov_within_tg = np.zeros((d, d))
    Cov_within_bg = np.zeros((d, d))
    Cov_between = np.zeros((d, d))
    w_tg_total = 0
    w_bg_total = 0
    w_bw_total = 0

    for label in labels:
        Cov_within_tg += w_tg[label] * _Covs[label]['within']
        Cov_within_bg += w_bg[label] * _Covs[label]['within']
        Cov_between += w_bw[label] * _Covs[label]['between']
        w_tg_total += w_tg[label]
        w_bg_total += w_bg[label]
        w_bw_total += w_bw[label]

    if gamma0 is None:
        if w_tg_total + w_bw_total == 0:
            gamma0 = 1
        else:
            gamma0 = 0
    if gamma1 is None:
        if w_bg_total == 0 and gamma1:
            gamma1 = 1
        else:
            gamma1 = 0

    C0 = Cov_within_tg + Cov_between + gamma0 * np.identity(d)
    C1 = Cov_within_bg + gamma1 * np.identity(d)

    @pymanopt.function.autograd(manifold)
    def cost(M):
        numerator = 1 if w_bg_total == 0 else np.trace(M.T @ C1 @ M)
        denominator = 1 if (w_tg_total +
                            w_bw_total) == 0 else np.trace(M.T @ C0 @ M)

        return numerator / denominator

    @pymanopt.function.autograd(manifold)
    def cost_with_alpha(M):
        return np.trace(M.T @ (alpha * C1 - C0) @ M)

    if alpha:
        return cost_with_alpha
    else:
        return cost
