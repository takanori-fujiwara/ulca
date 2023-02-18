import sys
import os
from distutils.core import setup

setup(name='ulca',
      version=0.2,
      packages=[''],
      package_dir={'': '.'},
      package_data={
          '': [
              'ulca_ui/index.html', 'ulca_ui/favicon.ico',
              'ulca_ui/style/*.css', 'ulca_ui/script/*.js'
          ],
      },
      include_package_data=True,
      install_requires=[
          'autograd', 'ipython', 'numpy', 'scipy', 'pandas', 'pymanopt',
          'simple-websocket-server', 'factor-analyzer'
      ],
      py_modules=[
          'manopt_dr', 'manopt_dr.core', 'manopt_dr.predefined_func_generator',
          'ulca', 'ulca.ulca', 'ulca_ui', 'ulca_ui.plot', 'ulca_ui.utils',
          'ulca_ui.utils.weight_opt', 'ulca_ui.utils.geom_trans'
      ])
