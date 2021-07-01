#
# Authors: Takanori Fujiwara and Xinhai Wei
#
import time
import numpy as np
import pandas as pd
from random import sample
from sklearn.cluster import KMeans
from sklearn.preprocessing import scale

from ulca.ulca import ULCA, EVDULCA


def run_perf_eval(n=100,
                  d=10,
                  c=3,
                  alpha=1,
                  methods=['manopt_ulca', 'evd_ulca'],
                  n_runs=10,
                  gamma0=1e-3,
                  gamma1=1e-3,
                  file_prefix='./document_vec_',
                  return_details=False):
    X = np.load(f'{file_prefix}{d}.npy')

    # randomly sample rows
    sampled_indices = sample(list(range(X.shape[0])), n)
    X = X[sampled_indices, :]

    # assign labels based on k-means clustering
    y = KMeans(n_clusters=c).fit(X).labels_

    print(f'n:{n}, d:{d}, c:{c}, alpha:{alpha}, n_run:{n_runs}')
    X = scale(X)

    ulcas = {}
    for method in methods:
        if method == 'manopt_ulca':
            ulcas[method] = ULCA(n_components=2,
                                 apply_varimax=False,
                                 apply_consist_axes=False)
        else:
            ulcas[method] = EVDULCA(n_components=2,
                                    apply_varimax=False,
                                    apply_consist_axes=False)

    comp_time = {}
    for method in methods:
        comp_time[method] = []

    for i in range(n_runs):
        w_tg = np.random.rand(c)
        w_bg = np.random.rand(c)
        w_bw = np.random.rand(c)

        obj_vals = []
        for method in methods:
            ulca = ulcas[method]
            start_time = time.perf_counter()
            ulca.fit(X,
                     y=y,
                     w_tg=w_tg,
                     w_bg=w_bg,
                     w_bw=w_bw,
                     alpha=alpha,
                     gamma0=gamma0,
                     gamma1=gamma1)
            end_time = time.perf_counter()
            comp_time[method].append(end_time - start_time)

    ave_time = {}
    for method in methods:
        ave_time[method] = np.mean(np.array(comp_time[method]))

    print(f'ave comp time: {ave_time}')
    if return_details:
        return ave_time, ave_obj_val_ratios, c, comp_time
    else:
        return ave_time


if __name__ == '__main__':
    n_runs = 10
    c = 3
    gamma0 = 0
    gamma1 = 0

    methods = ['manopt_ulca', 'evd_ulca']
    alphas = [1, None]  # None is auto selection of alpha
    ns = [100, 500, 1000, 5000, 10000]
    ds = [10, 50, 100, 500, 1000]

    result = []
    for alpha in alphas:
        for n in ns:
            for d in ds:
                ave_comp_time = run_perf_eval(n=n,
                                              d=d,
                                              c=c,
                                              alpha=alpha,
                                              gamma0=gamma0,
                                              gamma1=gamma1,
                                              methods=methods,
                                              n_runs=n_runs)

                for method in methods:
                    result.append({
                        'n_runs': n_runs,
                        'method': method,
                        'alpha': alpha if alpha else 'auto',
                        'n': n,
                        'd': d,
                        'c': c,
                        'ave_comp_time': ave_comp_time[method]
                    })

    result = pd.DataFrame(result)
    result.to_csv('perf_eval_ucla.csv', index=False)
