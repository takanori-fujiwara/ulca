###
### NOTE: install pymanopt from github. Don't use pip3 install pymanopt
### https://github.com/pymanopt/pymanopt
###
import autograd.numpy as np

import pymanopt
from pymanopt.manifolds import Stiefel, Grassmann
from pymanopt.optimizers import TrustRegions

from factor_analyzer import Rotator


def gen_ldr(cost_func_generator,
            project_func_generator,
            manifold_generator=Grassmann,
            optimizer=TrustRegions()):
    """Linear dimensionality reduction method generator using manifold optimization as a general optimization problem optimizer.

    Parameters
    ----------
    cost_func_generator: function generator
        Generator of cost function of linear dimensionality reduction.
        Examples can be found in predefined_func_generator.py, such as gen_cost_pca.
        Available predefined cost function genertors:
        - PCA (gen_cost_pca)
        - LDA (gen_cost_lda)
        - cPCA (gen_cost_cpca)
        - ccPCA (gen_cost_ccpca)
        - ULCA (gen_cost_ulca)
    project_func_generator: function generator
        Generator of projection function of linear dimensionality reduction.
        Example can be found in predefined_func_generator.py, such as gen_default_proj.
        Available predefined projection function genertors:
        - Matrix multiplication with data and projection matrix (gen_default_proj)
    manifold_generator: Pymanopt Manifold class (Grassman or Stiefel), optional, (default=Grassmann)
        Manifold class used for generating manifold optimization problem.
        Grassman or Stiefel should be used.
        Refer to https://www.pymanopt.org/ for more details.
    optimizer: Pymanopt optimizer class, (default=pymanopt.optimizers.TrustRegions())
        Optimizer class used for solving manifold optimization problem.
        In default, pymanopt.optimizers.TrustRegions() is used.
        Other settings and optimizers can be used.
        For example, pymanopt.optimizers.SteepestDescent().
        Refer to https://www.pymanopt.org/ for more details.

    Return
    ----------
    LDR (linear dimensionality reduction) class.

    Examples
    --------
    >>> from sklearn import datasets, preprocessing
    >>> from manopt_dr.core import gen_ldr
    >>> from manopt_dr.predefined_func_generator import gen_cost_ulca, gen_default_proj

    >>> # example 1: generate PCA class
    >>> PCA = gen_ldr(gen_cost_pca, gen_default_proj)

    >>> # example 2: generate ULCA class
    >>> ULCA = gen_ldr(gen_cost_ulca, gen_default_proj)

    >>> # usage example:
    >>> dataset = datasets.load_wine()
    >>> X = dataset.data
    >>> X = preprocessing.scale(X)

    >>> pca = PCA(n_components=2)
    >>> pca.fit_transform(X)
    """

    class LDR:
        """Linear dimensionality reduction class.
        Parameters
        ----------
        n_components: int, optional, (default=2)
            Number of componentes to take.
        max_iter: int, optional, (default=100)
            Maximum number of iterations used by Pymanopt Optimizer.
        convergence_ratio: float, optional (default=1e-2)
            Convergence ratio ("mingradnorm") used by Pymanopt Optimizer.
        apply_varimax: bool, optional, (default=True)
            If True, apply varimax rotation to the obtained components
        apply_consist_axes: bool, optional, (default=True)
            If True, signs of axes and order of axes are adjusted and generate
            more consistent axes' signs and orders.
            Refer to Sec. 4.2.4 in Fujiwara et al., Interactive Dimensionality
            Reduction for Comparative Analysis, 2021
        verbosity: int, optional, (default=0)
            Level of information logged by the optimizer while it operates, 0 is
            silent, 2 is most information. Refer to https://www.pymanopt.org/.
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
        optimizer: Pymanopt Optimizer class
            Optimizer class used for solving manifold optimization problem.
        M: numpy array, shape(n_features, n_components)
            Projection matrix.
        apply_varimax: bool
            Applying varimax rotation to the obtained components or not.
        apply_consist_axes:
            Applying adjustment of signs of axes and order of axes or not.
        verbosity: int
            Level of information logged.
        """

        def __init__(self,
                     n_components=2,
                     max_iterations=100,
                     convergence_ratio=1e-2,
                     apply_varimax=True,
                     apply_consist_axes=True,
                     verbosity=0):
            self.n_components = n_components
            self.cost_func_generator = cost_func_generator
            self.manifold_generator = manifold_generator
            self.optimizer = optimizer
            self.optimizer._max_iterations = max_iterations
            self.optimizer._min_gradient_norm = convergence_ratio
            self.project_func_generator = project_func_generator
            self.M = None
            self.projector = None
            self.apply_varimax = apply_varimax
            self.apply_consist_axes = apply_consist_axes
            self.verbosity = verbosity

        def fit(self, *args, **kwargs):
            """fit method similar to other DR classes in scikit-learn
            Parameters
            ----------
            args: arguments
            kwargs: keyward arguments

            Returns
            -------
            self.
            """
            manifold = self.manifold_generator(args[0].shape[1],
                                               self.n_components)
            self.problem = pymanopt.Problem(
                manifold, cost_func_generator(manifold, *args, **kwargs))
            self.optimizer._verbosity = self.verbosity
            self.M = self.optimizer.run(self.problem).point

            if self.apply_varimax and self.n_components > 1:
                self.M = Rotator(method='varimax').fit_transform(self.M)
            if self.apply_consist_axes:
                # consist sign (column sum will be pos)
                self.M = self.M * np.sign(self.M.sum(axis=0))
                # consist order (based on max value)
                self.M = self.M[:, np.argsort(-self.M.max(axis=0))]

            self.projector = self.project_func_generator(self.M)

            return self

        def transform(self, *args, **kwargs):
            """transform method similar to other DR classes in scikit-learn
            Parameters
            ----------
            args: arguments
            kwargs: keyward arguments

            Returns
            -------
            Embedding result: numpy array, shape(n_instances, n_components).
            """
            return self.projector(*args, **kwargs)

        def fit_transform(self, *args, **kwargs):
            """fit_transform method similar to other DR classes in scikit-learn
            Parameters
            ----------
            args: arguments
            kwargs: keyward arguments

            Returns
            -------
            Embedding result: numpy array, shape(n_instances, n_components).
            """
            return self.fit(*args, **kwargs).transform(*args, **kwargs)

        def get_final_cost(self):
            """Obtain objective value/cost obtained after optimization.
            Returns
            -------
            cost: float
            """
            return self.problem.cost(self.M)

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

    return LDR
