#
# Author: Takanori Fujiwara
#

# Note: need to install cPCA and ccPCA from # install from https://github.com/takanori-fujiwara/ccpca
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from experiment_settings import fig1, fig2, fig3, fig9a, fig9b, fig9c, fig10a, fig10b, fig10c

all_results = []
for fig in [fig1, fig2, fig3, fig9a, fig9b, fig9c, fig10a, fig10b, fig10c]:
    results = []

    X = fig['data']['X']
    y = fig['data']['y']
    feat_names = fig['data']['feat_names']
    colors = fig['colors']

    for method in fig['methods']:
        dr = method['dr']
        dr_name = dr.__class__.__name__
        # note: ULCA's class name is LDR

        groups = method['groups']
        title = method['title']
        Z = None
        M = None
        if groups:
            params = method['params']
            if dr_name == 'LinearDiscriminantAnalysis' or dr_name == 'LDR':
                dr_y = np.zeros(len(y))
                for i, g in enumerate(method['groups']):
                    dr_y[np.isin(y, g)] = i
                dr = dr.fit(X, dr_y, **params)
                Z = dr.transform(X)
            else:
                Xs = [X[np.isin(y, g)] for g in method['groups']]
                dr = dr.fit(*Xs, **params)
                Z = dr.transform(X)

            if dr_name == 'PCA':
                M = dr.components_.T
            elif dr_name == 'LinearDiscriminantAnalysis':
                M = dr.scalings_
            elif dr_name == 'LDR':
                M = dr.M
            else:
                M = dr.get_components()

        results.append({
            'title': title,
            'colors': colors,
            'feat_names': feat_names,
            'Z': Z,
            'M': M,
            'y': y
        })

    all_results.append(results)

for j, results in enumerate(all_results):
    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    df_M = pd.DataFrame()
    for i, r in enumerate(results):
        Z = r['Z']
        if Z is not None:
            if Z.shape[1] == 1:
                Z = np.hstack((Z, np.zeros(Z.shape)))
            xy_range = Z.max(axis=0) - Z.min(axis=0)
            max_range = np.max(xy_range) * 1.05
            lim_min = (Z.max(axis=0) + Z.min(axis=0) - max_range) / 2
            lim_max = (Z.max(axis=0) + Z.min(axis=0) + max_range) / 2
            axes[i].set_xlim([lim_min[0], lim_max[0]])
            axes[i].set_ylim([lim_min[1], lim_max[1]])

            axes[i].scatter(Z[:, 0], Z[:, 1], c=r['colors'][r['y']], s=15)
        axes[i].set_aspect('equal', adjustable='box')
        axes[i].set_title(r['title'])

        if Z is not None:
            M = r['M']
            if M.shape[1] == 1:
                M = np.hstack((M, np.zeros(M.shape)))
            df_M[i * 2] = M[:, 0]
            df_M[i * 2 + 1] = M[:, 1]
        else:
            df_M[i * 2] = 0
            df_M[i * 2 + 1] = 0
    plt.tight_layout()
    plt.savefig(f'{j}.pdf')

    df_M.columns = [
        'PCA (x)', 'PCA (y)', 'LDA (x)', 'LDA (y)', 'cPCA (x)', 'cPCA (y)',
        'ULCA (x)', 'ULCA (y)'
    ]
    if r['feat_names'] is not None:
        df_M.set_index(r['feat_names'], inplace=True)
    df_M.to_csv(f'{j}.csv')
    df_M.to_latex(f'{j}.tex')

    # heatmap for MNIST
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    for i, r in enumerate(results):
        if r['feat_names'] is None:
            pc1 = np.array(df_M.iloc[:, i * 2])
            pc2 = np.array(df_M.iloc[:, i * 2 + 1])
            abs_max = max(abs(pc1)) * 0.6

            hm_pc1 = axes[0, i].imshow(pc1.reshape(
                (int(np.sqrt(len(pc1))), int(np.sqrt(len(pc1))))),
                                       cmap='coolwarm',
                                       vmin=-abs_max,
                                       vmax=abs_max)
            fig.colorbar(hm_pc1, ax=axes[0, i])
            hm_pc2 = axes[1, i].imshow(pc2.reshape(
                (int(np.sqrt(len(pc2))), int(np.sqrt(len(pc2))))),
                                       cmap='coolwarm',
                                       vmin=-abs_max,
                                       vmax=abs_max)
            fig.colorbar(hm_pc2, ax=axes[1, i])
            axes[0, i].set_title(r['title'])
            axes[1, i].set_title(r['title'])
    plt.tight_layout()
    plt.savefig(f'{j}_heatmap.pdf')
