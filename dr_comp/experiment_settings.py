#
# Author: Takanori Fujiwara
#
import numpy as np

from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

from cpca import CPCA  # install from https://github.com/takanori-fujiwara/ccpca
from ulca.ulca import ULCA

pca = PCA(n_components=2)
lda = LinearDiscriminantAnalysis(n_components=2)
cpca = CPCA(n_components=2)
ulca = ULCA(n_components=2)

wine = np.load('wine.npy', allow_pickle=True).flatten()[0]
ppic = np.load('ppic.npy', allow_pickle=True).flatten()[0]
ppic2 = np.load('ppic2.npy', allow_pickle=True).flatten()[0]
mnist = np.load('mnist.npy', allow_pickle=True).flatten()[0]

fig1 = {
    'data':
    wine,
    'colors':
    np.array([[0.31, 0.48, 0.65], [0.94, 0.56, 0.22], [0.87, 0.35, 0.36]]),
    'methods': [{
        'title': 'PCA',
        'dr': pca,
        'groups': [[0, 1, 2]],
        'params': {}
    }, {
        'title': 'LDA (Label 0 vs 1 vs 2)',
        'dr': lda,
        'groups': [[0], [1], [2]],
        'params': {}
    }, {
        'title': 'cPCA (N/A)',
        'dr': cpca,
        'groups': None,
        'params': {
            'alpha': 0
        }
    }, {
        'title': 'ULCA (Fig. 1)',
        'dr': ulca,
        'groups': [[0], [1], [2]],
        'params': {
            'w_tg': {
                0: 0,
                1: 0,
                2: 0
            },
            'w_bg': {
                0: 1,
                1: 1,
                2: 1
            },
            'w_bw': {
                0: 1,
                1: 1,
                2: 1
            },
            'alpha': None
        }
    }]
}

fig2 = {
    'data':
    wine,
    'colors':
    np.array([[0.31, 0.48, 0.65], [0.94, 0.56, 0.22], [0.87, 0.35, 0.36]]),
    'methods': [{
        'title': 'PCA',
        'dr': pca,
        'groups': [[0, 1, 2]],
        'params': {}
    }, {
        'title': 'LDA (Label 0 vs Labels 1 & 2)',
        'dr': LinearDiscriminantAnalysis(n_components=1),
        'groups': [[0], [1, 2]],
        'params': {}
    }, {
        'title': 'cPCA (N/A)',
        'dr': cpca,
        'groups': None,
        'params': {
            'alpha': None
        }
    }, {
        'title': 'ULCA (Fig. 2)',
        'dr': ulca,
        'groups': [[0], [1], [2]],
        'params': {
            'w_tg': {
                0: 0.8362787627856337,
                1: 0.41704556470577103,
                2: 0.8566001894111713
            },
            'w_bg': {
                0: 0,
                1: 0.9618254239294945,
                2: 0.6878804303425374
            },
            'w_bw': {
                0: 1.0,
                1: 0.4456044544201703,
                2: 0
            },
            'alpha': 3.462280952336661
        }
    }]
}

fig3 = {
    'data':
    wine,
    'colors':
    np.array([[0.31, 0.48, 0.65], [0.94, 0.56, 0.22], [0.87, 0.35, 0.36]]),
    'methods': [{
        'title': 'PCA',
        'dr': pca,
        'groups': [[0, 1, 2]],
        'params': {}
    }, {
        'title': 'LDA (N/A)',
        'dr': lda,
        'groups': None,
        'params': {}
    }, {
        'title': 'cPCA (tg: Label 2, bg: Labels 0 & 1)',
        'dr': cpca,
        'groups': [[2], [0, 1]],
        'params': {
            'alpha': None
        }
    }, {
        'title': 'ULCA (Fig. 3)',
        'dr': ulca,
        'groups': [[0], [1], [2]],
        'params': {
            'w_tg': {
                0: 0,
                1: 0,
                2: 1
            },
            'w_bg': {
                0: 1,
                1: 1,
                2: 0
            },
            'w_bw': {
                0: 0,
                1: 0,
                2: 0
            },
            'alpha': 10
        }
    }]
}

fig9a = {
    'data':
    ppic,
    'colors':
    np.array([[0.31, 0.48, 0.65], [0.87, 0.35, 0.36], [0.36, 0.63, 0.32]]),
    'methods': [{
        'title': 'PCA',
        'dr': pca,
        'groups': [[0, 1]],
        'params': {}
    }, {
        'title': 'LDA (Dem vs Rep)',
        'dr': LinearDiscriminantAnalysis(n_components=1),
        'groups': [[0], [1]],
        'params': {}
    }, {
        'title': 'cPCA (tg: Dem, bg: Rep)',
        'dr': cpca,
        'groups': [[0], [1]],
        'params': {
            'alpha': None
        }
    }, {
        'title': 'ULCA (Fig. 9a)',
        'dr': ulca,
        'groups': [[0], [1]],
        'params': {
            'w_tg': {
                0: 1,
                1: 0
            },
            'w_bg': {
                0: 0,
                1: 1
            },
            'w_bw': {
                0: 0,
                1: 0
            },
            'alpha': 20
        }
    }]
}

fig9b = {
    'data':
    ppic2,
    'colors':
    np.array([[0.31, 0.48, 0.65], [0.87, 0.35, 0.36], [0.36, 0.63, 0.32]]),
    'methods': [{
        'title': 'PCA',
        'dr': pca,
        'groups': [[0, 1]],
        'params': {}
    }, {
        'title': 'LDA (N/A)',
        'dr': lda,
        'groups': None,
        'params': {}
    }, {
        'title': 'cPCA (tg: Dem(-), bg: Dem(+) and Rep)',
        'dr': cpca,
        'groups': [[2], [0, 1]],
        'params': {
            'alpha': None
        }
    }, {
        'title': 'ULCA (Fig. 9b)',
        'dr': ulca,
        'groups': [[0], [1], [2]],
        'params': {
            'w_tg': {
                0: 0,
                1: 0,
                2: 1
            },
            'w_bg': {
                0: 1,
                1: 1,
                2: 0
            },
            'w_bw': {
                0: 0,
                1: 0,
                2: 0
            },
            'alpha': None
        }
    }]
}

fig9c = {
    'data':
    ppic2,
    'colors':
    np.array([[0.31, 0.48, 0.65], [0.87, 0.35, 0.36], [0.36, 0.63, 0.32]]),
    'methods': [{
        'title': 'PCA',
        'dr': pca,
        'groups': [[0, 1]],
        'params': {}
    }, {
        'title': 'LDA (Dem(+) vs Rep)',
        'dr': LinearDiscriminantAnalysis(n_components=1),
        'groups': [[0], [1]],
        'params': {}
    }, {
        'title': 'cPCA (tg: Dem(-), bg: Dem(+) and Rep)',
        'dr': cpca,
        'groups': [[2], [0, 1]],
        'params': {
            'alpha': None
        }
    }, {
        'title': 'ULCA (Fig. 9c)',
        'dr': ulca,
        'groups': [[0], [1], [2]],
        'params': {
            'w_tg': {
                0: 0.038365900514515154,
                1: 0.03189631955255691,
                2: 0.6337167203034522
            },
            'w_bg': {
                0: 0.3389743652498261,
                1: 0.34867744858465005,
                2: 0.058115068138408006
            },
            'w_bw': {
                0: 0.24387188666965084,
                1: 0.024342165313444287,
                2: 0.9843778233029735
            },
            'alpha': 3.2938344688343313
        }
    }]
}

fig10a = {
    'data':
    mnist,
    'colors':
    np.array([[0.31, 0.48, 0.65], [0.87, 0.35, 0.36], [0.36, 0.63, 0.32],
              [0.93, 0.78, 0.33], [0.69, 0.48, 0.63], [0.94, 0.56, 0.22],
              [0.47, 0.72, 0.70], [0.99, 0.62, 0.66], [0.61, 0.46, 0.38],
              [0.73, 0.69, 0.67]]),
    'methods': [{
        'title': 'PCA',
        'dr': pca,
        'groups': [[0, 6, 9]],
        'params': {}
    }, {
        'title': 'LDA (N/A)',
        'dr': lda,
        'groups': None,
        'params': {}
    }, {
        'title': 'cPCA (tg: 6 and 9, bg: 0)',
        'dr': cpca,
        'groups': [[6, 9], [0]],
        'params': {
            'alpha': None
        }
    }, {
        'title': 'ULCA (Fig. 10a)',
        'dr': ulca,
        'groups': [[0], [6], [9]],
        'params': {
            'w_tg': {
                0: 0,
                1: 1,
                2: 1
            },
            'w_bg': {
                0: 1,
                1: 0,
                2: 0
            },
            'w_bw': {
                0: 0,
                1: 0,
                2: 0
            },
            'alpha': 5
        }
    }]
}

fig10b = {
    'data':
    mnist,
    'colors':
    np.array([[0.31, 0.48, 0.65], [0.87, 0.35, 0.36], [0.36, 0.63, 0.32],
              [0.93, 0.78, 0.33], [0.69, 0.48, 0.63], [0.94, 0.56, 0.22],
              [0.47, 0.72, 0.70], [0.99, 0.62, 0.66], [0.61, 0.46, 0.38],
              [0.73, 0.69, 0.67]]),
    'methods': [{
        'title': 'PCA',
        'dr': pca,
        'groups': [[0, 6, 9]],
        'params': {}
    }, {
        'title': 'LDA (N/A)',
        'dr': lda,
        'groups': None,
        'params': {}
    }, {
        'title': 'cPCA (tg: 6 and 9, bg: 0)',
        'dr': cpca,
        'groups': [[6, 9], [0]],
        'params': {
            'alpha': None
        }
    }, {
        'title': 'ULCA (Fig. 10b)',
        'dr': ulca,
        'groups': [[0], [6], [9]],
        'params': {
            'w_tg': {
                0: 0,
                1: 1,
                2: 0.5
            },
            'w_bg': {
                0: 1,
                1: 0,
                2: 0
            },
            'w_bw': {
                0: 0,
                1: 0,
                2: 0
            },
            'alpha': 5
        }
    }]
}

fig10c = {
    'data':
    mnist,
    'colors':
    np.array([[0.31, 0.48, 0.65], [0.87, 0.35, 0.36], [0.36, 0.63, 0.32],
              [0.93, 0.78, 0.33], [0.69, 0.48, 0.63], [0.94, 0.56, 0.22],
              [0.47, 0.72, 0.70], [0.99, 0.62, 0.66], [0.61, 0.46, 0.38],
              [0.73, 0.69, 0.67]]),
    'methods': [{
        'title': 'PCA',
        'dr': pca,
        'groups': [[0, 6, 9]],
        'params': {}
    }, {
        'title': 'LDA (6 and 9 vs 0)',
        'dr': LinearDiscriminantAnalysis(n_components=1),
        'groups': [[6, 9], 0],
        'params': {}
    }, {
        'title': 'cPCA (tg: 6 and 9, bg: 0)',
        'dr': cpca,
        'groups': [[6, 9], [0]],
        'params': {
            'alpha': None
        }
    }, {
        'title': 'ULCA (Fig. 10c)',
        'dr': ulca,
        'groups': [[0], [6], [9]],
        'params': {
            'w_tg': {
                0: 0,
                1: 1,
                2: 0.5
            },
            'w_bg': {
                0: 1,
                1: 0,
                2: 0
            },
            'w_bw': {
                0: 1,
                1: 0,
                2: 0
            },
            'alpha': 10
        }
    }]
}
