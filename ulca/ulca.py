import numpy as np
from scipy import linalg

from factor_analyzer import Rotator

from manopt_dr.core import gen_ldr
from manopt_dr.predefined_func_generator import gen_cost_ulca, gen_default_proj

# ULCA class
ULCA = gen_ldr(gen_cost_ulca, gen_default_proj)

# alias of ULCA
MANOPTULCA = ULCA
"""ULCA or MANOPTULCA class: ULCA using manifold optimization.
Parameters
----------
n_components: int, optional, (default=2)
    Number of componentes to take.
max_iter: int, optional, (default=100)
    Maximum number of iterations used by Pymanopt Solver.
convergence_ratio: float, optional (default=1e-2)
    Convergence ratio ("mingradnorm") used by Pymanopt Solver.
apply_varimax: bool, optional, (default=True)
    If True, apply varimax rotation to the obtained components
apply_consist_axes: bool, optional, (default=True)
    If True, signs of axes and order of axes are adjusted and generate
    more consistent axes' signs and orders.
    Refer to Sec. 4.2.4 in Fujiwara et al., Interactive Dimensionality
    Reduction for Comparative Analysis, 2021
verbosity: int, optional, (default=0)
    Level of information logged by the solver while it operates, 0 is
    silent, 2 is most information. Refer to https://www.pymanopt.org/.

Methods (same with EVDULCA. See EVDULCA's methods)
----------
fit
transform
fit_transform
get_final_cost
update_projector

Attributes
----------
n_components: int
    Number of components.
cost_func_generator: function generator
    Generator of cost function of linear dimensionality reduction.
project_func_generator: function generator
    Generator of projection function of linear dimensionality reduction.
manifold_generator: Pymanopt Manifold class
    Manifold class used for generating manifold optimization problem.
solver: Pymanopt solver class
    Solver class used for solving manifold optimization problem.
M: numpy array, shape(n_features, n_components)
    Projection matrix.
apply_varimax: bool
    Applying varimax rotation to the obtained components or not.
apply_consist_axes:
    Applying adjustment of signs of axes and order of axes or not.
verbosity: int
    Level of information logged.
"""


class EVDULCA:
    """EVDULCA class: ULCA using eigenvalue decomposition.
    Parameters
    ----------
    n_components: int, optional, (default=2)
        Number of componentes to take.
    apply_varimax: bool, optional, (default=True)
        If True, apply varimax rotation to the obtained components
    apply_consist_axes: bool, optional, (default=True)
        If True, signs of axes and order of axes are adjusted and generate
        more consistent axes' signs and orders.
        Refer to Sec. 4.2.4 in Fujiwara et al., Interactive Dimensionality
        Reduction for Comparative Analysis, 2021
    verbosity: int, optional, (default=0)
        Level of information logged by the solver while it operates, 0 is
        silent, the other number is providing information.
    """
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
            gamma0=None,
            gamma1=None,
            convergence_ratio=1e-2,
            max_iter=100):
        """Fit the model with X and other parameters.
        Parameters
        ----------
        X: array-like of shape(n_samples, n_features)
            Training data.
        y: array-like of shape (n_samples,)
            Labels of training data's instances.
        w_tg: array-like of shape (n_groups,) or dictionary
            Target weights assigned for each group's covariance matrix.
            If array is used, array element of y must be integer.
            If dictionary is used, dictionary key and element of y must have
            correspondence.
            Each weight should be a range of [0, 1].
            (e.g., y = [0, 1, 1, 0], w_tg={0: 0.1, 1: 0.5})
        w_bg: array-like of shape (n_groups,) or dictionary
            Background weights assigned for each group's covariance matrix.
            If array is used, array element of y must be integer.
            If dictionary is used, dictionary key and element of y must have
            correspondence.
            Each weight should be a range of [0, 1].
            (e.g., y = [0, 1, 1, 0], w_bg={0: 0.1, 1: 0.5})
        w_bw: array-like of shape (n_groups,) or dictionary
            If array is used, array element of y must be integer.
            If dictionary is used, dictionary key and element of y must have
            correspondence.
            Each weight should be a range of [0, 1].
            (e.g., y = [0, 1, 1, 0], w_bw={0: 0.1, 1: 0.5})
        Covs: dictionary, optional, (default={})
            If provided, computation of within-group and between-group
            covariance matrices will be skipped.
            Use 'within' and 'between' keys to assign within-group and
            between-group covariance matrixes.
            (e.g., Covs={'within': Cov_wi, 'between': Cov_bt})
        alpha: None or float, optional (default=None)
            If None, alpha is automatically selected by solving Eq. 6 in
            Fujiwara et al., Interactive Dimensionality Reduction for
            Comparative Analysis, 2021.
            Otherwise, indicated alpha is used to solve Eq. 9.
        centering: bool, optional, (default=True)
            If True, apply centering to the entire X before covariance matrix
            computation. Note that X is not overwritten.
        gamma0: None or float, optional, (default=None)
            If None, when all elements of w_tg and w_bw are zero, gamma0=1 is
            used, for other cases, gamma0=0 is used.
            If not None, indicated value is used for gamma0.
            Refer to Sec. 4.2.3.
        gamma1: None or float, optional, (default=None)
            If None, when all elements of w_bg are zero, gamma1=1 is
            used, for other cases, gamma1=0 is used.
            If not None, indicated value is used for gamma1.
            Refer to Sec. 4.2.3.
        max_iter: int, optional, (default=100)
            Maximum number of iterations when solving Eq. 10 and 11.
            Note this parameter is only for EVDULCA (not for ULCA/MANOPTULCA)
        convergence_ratio: float, optional (default=1e-2)
            Convergence ratio when solving Eq. 10 and 11.
            Note this parameter is only for EVDULCA (not for ULCA/MANOPTULCA)

        Returns
        -------
        self.

        Examples
        -------
        from sklearn import datasets, preprocessing
        from ulca.ulca import ULCA

        >>> # prepare data
        >>> dataset = datasets.load_wine()
        >>> X = dataset.data
        >>> y = dataset.target
        >>> X = preprocessing.scale(X)

        >>> # prepare ULCA and parameters
        >>> ulca = ULCA(n_components=2)

        >>> w_tg = {0: 0, 1: 0, 2: 0}
        >>> w_bg = {0: 1, 1: 1, 2: 1}
        >>> w_bw = {0: 1, 1: 1, 2: 1}

        >>> # apply ULCA
        >>> ulca = ulca.fit(X, y=y, w_tg=w_tg, w_bg=w_bg, w_bw=w_bw)
        """
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

        if self.alpha:
            self.M = self._apply_evd(C0, C1, self.alpha)
            if self.apply_varimax and self.n_components > 1:
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

            if self.apply_varimax and self.n_components > 1:
                self.M = Rotator(method='varimax').fit_transform(self.M)
            if self.apply_consist_axes:
                # consist sign (column sum will be pos)
                self.M = self.M * np.sign(self.M.sum(axis=0))
                # consist order (based on max value)
                self.M = self.M[:, np.argsort(-self.M.max(axis=0))]

        self.projector = self.project_func_generator(self.M)

        return self

    def transform(self, X):
        """
        Apply dimensionality reduction to X.
        X is projected on the components previously extracted from a training set.
        Parameters
        ----------
        X: array-like of shape(n_samples, n_features)
            Data.
        Returns
        -------
        X_new, ndarray of shape (n_samples, n_components)
            Transformed values.
        """
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
        """Fit the model with X and apply the dimensionality reduction on X.
        Parameters
        ----------
        X: array-like of shape(n_samples, n_features)
            Training data.
        y: array-like of shape (n_samples,)
            Labels of training data's instances.
        w_tg: array-like of shape (n_groups,) or dictionary
            Target weights assigned for each group's covariance matrix.
            If array is used, array element of y must be integer.
            If dictionary is used, dictionary key and element of y must have
            correspondence.
            Each weight should be a range of [0, 1].
            (e.g., y = [0, 1, 1, 0], w_tg={0: 0.1, 1: 0.5})
        w_bg: array-like of shape (n_groups,) or dictionary
            Background weights assigned for each group's covariance matrix.
            If array is used, array element of y must be integer.
            If dictionary is used, dictionary key and element of y must have
            correspondence.
            Each weight should be a range of [0, 1].
            (e.g., y = [0, 1, 1, 0], w_bg={0: 0.1, 1: 0.5})
        w_bw: array-like of shape (n_groups,) or dictionary
            If array is used, array element of y must be integer.
            If dictionary is used, dictionary key and element of y must have
            correspondence.
            Each weight should be a range of [0, 1].
            (e.g., y = [0, 1, 1, 0], w_bw={0: 0.1, 1: 0.5})
        Covs: dictionary, optional, (default={})
            If provided, computation of within-group and between-group
            covariance matrices will be skipped.
            Use 'within' and 'between' keys to assign within-group and
            between-group covariance matrixes.
            (e.g., Covs={'within': Cov_wi, 'between': Cov_bt})
        alpha: None or float, optional (default=None)
            If None, alpha is automatically selected by solving Eq. 6 in
            Fujiwara et al., Interactive Dimensionality Reduction for
            Comparative Analysis, 2021.
            Otherwise, indicated alpha is used to solve Eq. 9.
        centering: bool, optional, (default=True)
            If True, apply centering to the entire X before covariance matrix
            computation. Note that X is not overwritten.
        gamma0: None or float, optional, (default=None)
            If None, when all elements of w_tg and w_bw are zero, gamma0=1 is
            used, for other cases, gamma0=0 is used.
            If not None, indicated value is used for gamma0.
            Refer to Sec. 4.2.3.
        gamma1: None or float, optional, (default=None)
            If None, when all elements of w_bg are zero, gamma1=1 is
            used, for other cases, gamma1=0 is used.
            If not None, indicated value is used for gamma1.
            Refer to Sec. 4.2.3.
        max_iter: int, optional, (default=100)
            Maximum number of iterations when solving Eq. 10 and 11.
            Note this parameter is only for EVDULCA (not for ULCA/MANOPTULCA)
        convergence_ratio: float, optional (default=1e-2)
            Convergence ratio when solving Eq. 10 and 11.
            Note this parameter is only for EVDULCA (not for ULCA/MANOPTULCA)
        Returns
        -------
        X_new, ndarray of shape (n_samples, n_components)
            Transformed values.
        """
        return self.fit(locals()).transform(X)

    def get_final_cost(self):
        """Obtain objective value/cost obtained after optimization.
        This cost is equal to the inverse of alpha.
        Returns
        -------
        cost: float
        """
        return 1 / self.alpha if self.alpha else 0

    def update_projector(self, M):
        """Update information related to projection
        Parameters
        ----------
        M: projection matrix (n_features, n_components)
        Returns
        -------
        self
        """
        self.M = M
        self.projector = self.project_func_generator(self.M)
        return self
