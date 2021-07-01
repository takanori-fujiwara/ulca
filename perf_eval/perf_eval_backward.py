#
# Authors: Takanori Fujiwara and Xinhai Wei
#
import time
import numpy as np
import pandas as pd
from random import sample
from scipy.spatial.distance import pdist
from sklearn.cluster import KMeans
from sklearn.preprocessing import scale

from ulca.ulca import ULCA
from ulca_ui.utils.weight_opt import optimize_cost, total_cost


def compute_covs(X, y):
    labels = np.unique(y)
    Covs = {}

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
        Cov_within = WI.T @ WI
        Cov_between = BW.T @ BW
        Covs[label] = {'within': Cov_within, 'between': Cov_between}

    return Covs


def run_perf_eval(n=100,
                  d=10,
                  c=3,
                  alpha=1,
                  method='manopt_ulca',
                  n_runs=10,
                  gamma0=1e-3,
                  gamma1=1e-3,
                  max_iter=10,
                  file_prefix='./document_vec_',
                  return_details=False,
                  log_file='./log2.txt'):
    X = np.load(f'{file_prefix}{d}.npy')

    # randomly sample rows
    sampled_indices = sample(list(range(X.shape[0])), n)
    X = X[sampled_indices, :]

    # assign labels based on k-means clustering
    y = KMeans(n_clusters=c).fit(X).labels_

    print(
        f'n:{n}, d:{d}, c:{c}, alpha:{alpha}, n_run:{n_runs}, max_iter:{max_iter}'
    )
    X = scale(X)

    ulca = None
    if method == 'manopt_ulca':
        ulca = ULCA(n_components=2, apply_varimax=False)
    else:
        ulca = EVDULCA(n_components=2, apply_varimax=False)

    # generate an initial result
    w_tg = np.random.rand(c)
    w_bg = np.random.rand(c)
    w_bw = np.random.rand(c)

    # prepare covariance infor in advance
    Covs = compute_covs(X, y)

    # initial embedding result
    Z = ulca.fit_transform(X,
                           y=y,
                           Covs=Covs,
                           w_tg=w_tg,
                           w_bg=w_bg,
                           w_bw=w_bw,
                           alpha=alpha,
                           gamma0=gamma0,
                           gamma1=gamma1)

    uniq_labels = np.unique(y)

    current_centers = {}
    current_areas = {}
    for label in uniq_labels:
        means = Z[y == label, :].mean(axis=0)
        Z_centered = Z[y == label, :] - means
        Cov = Z_centered.T @ Z_centered
        # skip using pi
        current_centers[label] = means
        current_areas[label] = np.sqrt(Cov[0, 0]) * np.sqrt(Cov[1, 1])

    # prepare random interaction
    selected_labels = np.random.randint(c, size=n_runs)
    selected_interactions = np.random.randint(2, size=n_runs)
    selected_positions = np.array(
        [current_centers[label] for label in selected_labels])
    selected_scales = np.array([1] * n_runs)

    xy_mins = np.min(Z, axis=0)
    xy_maxs = np.max(Z, axis=0)
    xy_range = xy_maxs - xy_mins

    min_scale = 0.2
    max_scale = 5
    max_moving_range = 1.1
    xy_interction_range = xy_range * (max_moving_range - 1)
    xy_interction_mins = xy_mins - 0.5 * xy_interction_range
    xy_interction_maxs = xy_maxs + 0.5 * xy_interction_range

    for i in range(n_runs):
        if selected_interactions[i] == 0:
            # move
            pos_x = np.random.uniform(xy_interction_mins[0],
                                      xy_interction_maxs[0])
            pos_y = np.random.uniform(xy_interction_mins[1],
                                      xy_interction_maxs[1])
            selected_positions[i, 0] = pos_x
            selected_positions[i, 1] = pos_y
        else:
            # scale
            selected_scales[i] = np.random.uniform(min_scale, max_scale)

    initial_weights = list(w_tg) + list(w_bg) + list(w_bw)

    comp_time = []
    original_costs = []
    best_costs = []
    costs = []
    precisions = []

    with open(log_file, 'a') as log_file:
        for i in range(n_runs):
            if i % 10 == 0:
                print(f'{i}th run')

            updated_label = selected_labels[i]
            interaction = selected_interactions[i]
            updated_pos = selected_positions[i]
            updated_scale = selected_scales[i]

            # scale
            w_area = 0.8
            w_dist = 0.2
            if interaction == 0:
                # move
                w_area = 0.2
                w_dist = 0.8

            ideal_centers = {}
            ideal_areas = {}
            for l in uniq_labels:
                ideal_centers[l] = current_centers[l]
                ideal_areas[l] = current_areas[l]
                if l == updated_label:
                    ideal_centers[l] = updated_pos
                    ideal_areas[l] *= updated_scale
            ideal_dists = pdist(np.array(list(ideal_centers.values())))

            original_cost = total_cost(updated_label,
                                       ideal_areas,
                                       ideal_dists,
                                       Z,
                                       y,
                                       w_area=w_area,
                                       w_dist=w_dist)
            # when original_cost <= 0, there is no solution
            if original_cost <= 0:
                continue

            _, best_cost = optimize_cost(dr=ulca,
                                         initial_weights=initial_weights,
                                         updated_label=updated_label,
                                         ideal_areas=ideal_areas,
                                         ideal_dists=ideal_dists,
                                         X=X,
                                         y=y,
                                         with_alpha=True,
                                         alpha=alpha,
                                         Covs=Covs,
                                         w_area=w_area,
                                         w_dist=w_dist,
                                         Z_prev=Z,
                                         apply_geom_trans=False,
                                         n_components=2,
                                         method='COBYLA',
                                         options={'maxiter': 1000})

            # when best_cost >= original_cost, there is no solution
            if best_cost < original_cost:
                start_time = time.perf_counter()
                _, cost = optimize_cost(dr=ulca,
                                        initial_weights=initial_weights,
                                        updated_label=updated_label,
                                        ideal_areas=ideal_areas,
                                        ideal_dists=ideal_dists,
                                        X=X,
                                        y=y,
                                        with_alpha=True,
                                        alpha=alpha,
                                        Covs=Covs,
                                        w_area=w_area,
                                        w_dist=w_dist,
                                        Z_prev=Z,
                                        apply_geom_trans=False,
                                        n_components=2,
                                        method='COBYLA',
                                        options={'maxiter': max_iter})
                end_time = time.perf_counter()

                # if optimization generates a larger cost than the original
                # discard the result
                if cost > original_cost:
                    cost = original_cost

                comp_time.append(end_time - start_time)
                original_costs.append(original_cost)
                best_costs.append(best_cost)
                costs.append(cost)
                precision = (original_cost - cost) / (original_cost -
                                                      best_cost)

                log_file.write(
                    f'{d},{c},{max_iter},{i},{cost},{best_cost},{original_cost},{precision}\n'
                )

                if precision > 1:
                    precision = 1
                elif precision < 0:
                    precision = 0

                precisions.append(precision)

    ave_time = np.mean(np.array(comp_time))
    var_time = np.var(np.array(comp_time))
    ave_precision = np.mean(np.array(precisions))
    var_precision = np.var(np.array(precisions))

    print(
        f'ave comp time: {ave_time}, ave_precision: {ave_precision}, success: {len(comp_time)}'
    )
    if return_details:
        return ave_time, ave_precision, var_time, var_precision, len(
            comp_time
        ), comp_time, original_costs, best_costs, costs, precisions
    else:
        return ave_time, ave_precision, var_time, var_precision, len(comp_time)


if __name__ == '__main__':
    n_runs = 500
    method = 'manopt_ulca'
    alpha = 1
    gamma0 = 0
    gamma1 = 0
    n = 1000

    ds = [10, 100]
    cs = [2, 4, 6]
    max_iterations = [5, 10, 20, 40, 80]

    result = []
    for d in ds:
        for c in cs:
            for max_iter in max_iterations:
                (ave_comp_time, ave_precision, var_time, var_precision,
                 succeeded_runs) = run_perf_eval(n=n,
                                                 d=d,
                                                 c=c,
                                                 alpha=alpha,
                                                 method=method,
                                                 n_runs=n_runs,
                                                 gamma0=gamma0,
                                                 gamma1=gamma1,
                                                 max_iter=max_iter)

                result.append({
                    'n_runs': n_runs,
                    'method': method,
                    'alpha': alpha if alpha else 'auto',
                    'n': n,
                    'd': d,
                    'c': c,
                    'max_iter': max_iter,
                    'ave_comp_time': ave_comp_time,
                    'var_time': var_time,
                    'ave_precision': ave_precision,
                    'var_precision': var_precision,
                    'succeeded_runs': succeeded_runs
                })

    result = pd.DataFrame(result)
    result.to_csv(f'perf_eval_backward2_n{n}.csv', index=False)
