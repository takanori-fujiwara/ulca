import numpy as np
from scipy import linalg

from factor_analyzer import Rotator

from manopt_dr.core import gen_ldr
from manopt_dr.predefined_func_generator import gen_cost_ulca, gen_default_proj

# ULCA class
ULCA = gen_ldr(gen_cost_ulca, gen_default_proj)

# alias of ULCA
MANOPTULCA = ULCA


class EVDULCA:
    def __init__(self,
                 n_components=2,
                 apply_varimax=False,
                 apply_consist_axes=True,
                 verbosity=0):
        self.n_components = n_components
        self.M = None
        self.alpha = None
        self.project_func_generator = lambda M: (lambda X: X @ M)
        self.projector = None
        self.apply_varimax = apply_varimax
        self.apply_consist_axes = apply_consist_axes
        self.verbosity = verbosity

    def _apply_evd(self, C0, C1, alpha):
        C = C0 - alpha * C1
        w, v = linalg.eig(C)
        return v[:, np.argsort(-np.real(w))[:self.n_components]]

    def fit(self,
            X,
            y,
            w_tg,
            w_bg,
            w_bw,
            Covs={},
            alpha=None,
            centering=True,
            gamma0=0,
            gamma1=0,
            convergence_ratio=1e-6,
            max_iter=100):
        self.alpha = alpha

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
                Cov_within = WI.T @ WI
                Cov_between = BW.T @ BW
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

        if w_tg_total + w_bw_total == 0 and gamma0 == 0:
            gamma0 = 1
        if w_bg_total == 0 and gamma1 == 0:
            gamma1 = 1

        C0 = Cov_within_tg + Cov_between + gamma0 * np.identity(d)
        C1 = Cov_within_bg + gamma1 * np.identity(d)

        if self.alpha:
            self.M = self._apply_evd(C0, C1, self.alpha)
            if self.apply_varimax:
                self.M = Rotator(method='varimax').fit_transform(self.M)
        else:
            self.alpha = 0
            self.M = self._apply_evd(C0, C1, self.alpha)
            iter = 1
            improved_ratio = 1
            for i in range(max_iter):
                prev_alpha = self.alpha
                self.alpha = np.trace(self.M.T @ C0 @ self.M) / np.trace(
                    self.M.T @ C1 @ self.M)
                self.M = self._apply_evd(C0, C1, self.alpha)

                improved_ratio = np.abs(prev_alpha - self.alpha) / self.alpha
                if self.verbosity > 0:
                    print(f'alpha: {self.alpha}, improved: {improved_ratio}')
                if improved_ratio < convergence_ratio:
                    break

            if self.apply_varimax:
                self.M = Rotator(method='varimax').fit_transform(self.M)
            if self.apply_consist_axes:
                # consist sign (column sum will be pos)
                self.M = self.M * np.sign(self.M.sum(axis=0))
                # consist order (based on max value)
                self.M = self.M[:, np.argsort(-self.M.max(axis=0))]

        self.projector = self.project_func_generator(self.M)

        return self

    def transform(self, X):
        return self.projector(X)

    def fit_transform(self,
                      X,
                      y,
                      w_tg,
                      w_bg,
                      w_bw,
                      Covs={},
                      alpha=None,
                      centering=True,
                      gamma0=0,
                      gamma1=0,
                      convergence_ratio=1e-2,
                      max_iter=100):
        return self.fit(locals()).transform(X)

    def get_final_cost(self):
        return 1 / self.alpha if self.alpha else 0

    def update_projector(self, M):
        self.M = M
        self.projector = self.project_func_generator(self.M)
        return self
