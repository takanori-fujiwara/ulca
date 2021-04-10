#
# Usage Exaple in the Jupyter Notebook can be found in case_studies directory
#
from sklearn import datasets, preprocessing

from ulca.ulca import ULCA
from ulca_ui.plot import Plot

# 1. prepare data
dataset = datasets.load_wine()
X = dataset.data
y = dataset.target
feat_names = dataset.feature_names

# replace to a shorter name
feat_names[11] = 'od280/od315'

# normalization
X = preprocessing.scale(X)

# 2. prepare ULCA and parameters
ulca = ULCA(n_components=2)

w_tg = {0: 0, 1: 0, 2: 0}
w_bg = {0: 1, 1: 1, 2: 1}
w_bw = {0: 1, 1: 1, 2: 1}

# 3. apply ULCA
ulca = ulca.fit(X, y=y, w_tg=w_tg, w_bg=w_bg, w_bw=w_bw)

# 4. show the result in the interactive visual interface
# To call the interface from the command line, inline_mode need to be False
Plot().plot_emb(dr=ulca,
                X=X,
                y=y,
                w_tg=w_tg,
                w_bg=w_bg,
                w_bw=w_bw,
                feat_names=feat_names,
                inline_mode=False)
