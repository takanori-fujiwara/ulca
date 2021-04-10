import autograd.numpy as np
from scipy import optimize
from scipy.spatial.distance import pdist

from .geom_trans import find_best_rotate


def cost_area(updated_label, ideal_areas, Z, y):
    uniq_labels = np.unique(y)

    class_areas = {}
    for label in uniq_labels:
        means = Z[y == label, :].mean(axis=0)
        Z_centered = Z[y == label, :] - means
        Cov = Z_centered.T @ Z_centered
        # skip using pi
        class_areas[label] = np.sqrt(Cov[0, 0]) * np.sqrt(Cov[1, 1])

    cost = 0.0
    for label in uniq_labels:
        ideal = ideal_areas[updated_label] / ideal_areas[label] if ideal_areas[
            label] > 0 else -1
        actual = class_areas[updated_label] / class_areas[
            label] if class_areas[label] > 0 else -1

        # normalized loss within 0-1
        cost += min(1, np.abs((ideal - actual) / ideal)) / len(uniq_labels)

    return cost


def cost_dist(updated_label, ideal_dists, Z, y):
    uniq_labels = np.unique(y)

    class_centers = np.zeros((len(uniq_labels), Z.shape[1]))
    for i, label in enumerate(uniq_labels):
        class_centers[i, :] = Z[y == label, :].mean(axis=0)

    actual_dists = pdist(class_centers)

    # normalized loss within 0-1
    denom = np.sqrt((ideal_dists**2).sum())

    cost = np.sqrt(
        ((ideal_dists - actual_dists)**2).sum()) / denom if denom > 0 else 1

    return cost


def total_cost(updated_label,
               ideal_areas,
               ideal_dists,
               Z,
               y,
               w_area=0.5,
               w_dist=0.5):
    c_area = cost_area(updated_label=updated_label,
                       ideal_areas=ideal_areas,
                       Z=Z,
                       y=y)
    c_dist = cost_dist(updated_label=updated_label,
                       ideal_dists=ideal_dists,
                       Z=Z,
                       y=y)
    cost = w_area * c_area + w_dist * c_dist

    return cost


def gen_cost_func(dr,
                  updated_label,
                  ideal_areas,
                  ideal_dists,
                  X,
                  y,
                  alpha,
                  with_alpha,
                  Covs,
                  w_area=0.5,
                  w_dist=0.5,
                  Z_prev=None,
                  apply_geom_trans=True,
                  n_components=2):
    uniq_labels = np.unique(y)
    _Covs = {}

    # precompute Covs for faster optimization
    if len(Covs.keys()) == 0:
        X_c = X - X.mean(axis=0)
        class_mean = {}
        for label in uniq_labels:
            class_mean[label] = X_c[y == label, :].mean(axis=0)

        X_class_mean = np.zeros(X.shape)
        for label in uniq_labels:
            X_class_mean[y == label, :] = class_mean[label]

        all_mean = 0  # this equals to X_c.mean()

        for label in uniq_labels:
            # to compute within-cov
            WI = X_c[y == label, :] - X_class_mean[y == label, :]
            # to compute between-cov
            BW = X_class_mean[y == label, :] - all_mean
            Cov_within = WI.T @ WI
            Cov_between = BW.T @ BW
            Covs[label] = {'within': Cov_within, 'between': Cov_between}
    else:
        _Covs = Covs

    def cost_func(weights):
        # TODO: find better way for separating weights from Dash's inputs
        n_labels = len(uniq_labels)
        tg_weights = weights[:n_labels]
        bg_weights = weights[n_labels * 1:n_labels * 2]
        bw_weights = weights[n_labels * 2:n_labels * 3]

        w_tg = {}
        w_bg = {}
        w_bw = {}
        for i, label in enumerate(uniq_labels):
            w_tg[label] = tg_weights[i]
            w_bg[label] = bg_weights[i]
            w_bw[label] = bw_weights[i]

        if with_alpha:
            alpha_ = weights[-1]
        else:
            alpha_ = alpha

        Z = dr.fit(X,
                   y=y,
                   w_tg=w_tg,
                   w_bg=w_bg,
                   w_bw=w_bw,
                   Covs=Covs,
                   alpha=alpha_).transform(X)

        if apply_geom_trans and Z_prev is not None:
            R = find_best_rotate(Z_prev, Z)
            Z = Z @ R

        return total_cost(updated_label=updated_label,
                          ideal_areas=ideal_areas,
                          ideal_dists=ideal_dists,
                          Z=Z,
                          y=y,
                          w_area=w_area,
                          w_dist=w_dist)

    return cost_func


def optimize_cost(dr,
                  initial_weights,
                  updated_label,
                  ideal_areas,
                  ideal_dists,
                  X,
                  y,
                  with_alpha=True,
                  alpha=None,
                  Covs={},
                  w_area=0.5,
                  w_dist=0.5,
                  Z_prev=None,
                  apply_geom_trans=True,
                  n_components=2,
                  method='COBYLA',
                  options={'maxiter': 30},
                  constraints='auto'):
    cost_func = gen_cost_func(dr=dr,
                              updated_label=updated_label,
                              ideal_areas=ideal_areas,
                              ideal_dists=ideal_dists,
                              X=X,
                              y=y,
                              with_alpha=with_alpha,
                              alpha=alpha,
                              Covs=Covs,
                              w_area=w_area,
                              w_dist=w_dist,
                              Z_prev=Z_prev,
                              apply_geom_trans=apply_geom_trans,
                              n_components=n_components)

    def nonneg(a):
        return lambda x: x[a]

    def less_or_eq_to_1(a):
        return lambda x: 1 - x[a]

    if constraints == 'auto':
        constraints = []
        for i in range(len(initial_weights)):
            constraints.append({'type': 'ineq', 'fun': nonneg(i)})
            constraints.append({'type': 'ineq', 'fun': less_or_eq_to_1(i)})

    if with_alpha:
        initial_weights = list(initial_weights) + [alpha]
        constraints.append({'type': 'ineq', 'fun': nonneg(-1)})

    opt_result = optimize.minimize(cost_func,
                                   initial_weights,
                                   method=method,
                                   options=options,
                                   constraints=constraints)
    optimized_weights = opt_result.x
    cost = opt_result.fun

    return optimized_weights, cost
