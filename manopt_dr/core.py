###
### NOTE: install pymanopt from github. Don't use pip3 install pymanopt
### https://github.com/pymanopt/pymanopt
###
import autograd.numpy as np

import pymanopt
from pymanopt.manifolds import Stiefel, Grassmann
from pymanopt.solvers import TrustRegions

from factor_analyzer import Rotator


def gen_ldr(cost_func_generator,
            project_func_generator,
            manifold_generator=Grassmann,
            solver=TrustRegions()):
    class LDR:
        def __init__(self,
                     n_components=2,
                     max_iter=100,
                     convergence_ratio=1e-2,
                     apply_varimax=True,
                     apply_consist_axes=True,
                     verbosity=0):
            self.n_components = n_components
            self.cost_func_generator = cost_func_generator
            self.manifold_generator = manifold_generator
            self.solver = solver
            self.solver._maxiter = max_iter
            self.solver._mingradnorm = convergence_ratio
            self.project_func_generator = project_func_generator
            self.M = None
            self.projector = None
            self.apply_varimax = apply_varimax
            self.apply_consist_axes = apply_consist_axes
            self.verbosity = verbosity

        def fit(self, *args, **kwargs):
            self.problem = pymanopt.Problem(
                self.manifold_generator(args[0].shape[1], self.n_components),
                cost_func_generator(*args, **kwargs))
            self.problem.verbosity = self.verbosity
            self.M = self.solver.solve(self.problem)

            if self.apply_varimax:
                self.M = Rotator(method='varimax').fit_transform(self.M)
            if self.apply_consist_axes:
                # consist sign (column sum will be pos)
                self.M = self.M * np.sign(self.M.sum(axis=0))
                # consist order (based on max value)
                self.M = self.M[:, np.argsort(-self.M.max(axis=0))]

            self.projector = self.project_func_generator(self.M)

            return self

        def transform(self, *args, **kwargs):
            return self.projector(*args, **kwargs)

        def fit_transform(self, *args, **kwargs):
            return self.fit(*args, **kwargs).transform(*args, **kwargs)

        def get_final_cost(self):
            return self.problem.cost(self.M)

        def update_projector(self, M):
            self.M = M
            self.projector = self.project_func_generator(self.M)
            return self

    return LDR
