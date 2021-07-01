#
# Authors: Takanori Fujiwara and Xinhai Wei
#
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# import tikzplotlib

# 1. Evaluation of ULCA
df = pd.read_csv('./perf_eval_ucla.csv')

manopt_relax = df[df['method'] == 'manopt_ulca'][df['alpha'] != 'auto']
manopt_strict = df[df['method'] == 'manopt_ulca'][df['alpha'] == 'auto']
evd_relax = df[df['method'] == 'evd_ulca'][df['alpha'] != 'auto']
evd_strict = df[df['method'] == 'evd_ulca'][df['alpha'] == 'auto']

# 1-1. Relaxed ULCA
plt.figure(figsize=(6, 6))
for data, label, ls in zip([evd_relax, manopt_relax], ['EVD', 'Man'],
                           ['dashed', 'solid']):
    for i, n in enumerate([1000, 5000, 10000]):
        X = data[data['n'] == n]['d']
        Y = data[data['n'] == n]['ave_comp_time']
        plt.plot(X,
                 Y,
                 label=f'{label} (n:{n})',
                 linestyle=ls,
                 marker='.',
                 c=f'C{i}')
plt.xscale('log')
plt.yscale('log')
plt.xlabel(r'Number of attributes ($d$)')
plt.ylabel('Completion time (second)')
plt.legend(loc='lower right')
plt.tight_layout()
# tikzplotlib.save('ulca_relax_time.tex')
plt.show()

# 1-2. Non-relaxed ULCA
plt.figure(figsize=(6, 6))
for data, label, ls in zip([evd_strict, manopt_strict], ['EVD', 'Man'],
                           ['dashed', 'solid']):
    for i, n in enumerate([1000, 5000, 10000]):
        X = data[data['n'] == n]['d']
        Y = data[data['n'] == n]['ave_comp_time']
        plt.plot(X,
                 Y,
                 label=f'{label} (n:{n})',
                 linestyle=ls,
                 marker='.',
                 c=f'C{i}')
plt.xscale('log')
plt.yscale('log')
plt.xlabel(r'Number of attributes ($d$)')
plt.ylabel('Completion time (second)')
plt.legend()
plt.tight_layout()
# tikzplotlib.save('ulca_strict_time.tex')
plt.show()

# 2. Evaluation of the backward parameter selection
df = pd.read_csv('./perf_eval_backward_n1000.csv')

# 2-1. Completion time
colors = ['#e377c2', '#bcbd22', '#17becf']
plt.figure(figsize=(6, 6))
for d, ls in zip([100, 10], ['solid', 'dashed']):
    for i, c in enumerate([2, 4, 6]):
        X = df[df['d'] == d][df['c'] == c]['max_iter']
        Y = df[df['d'] == d][df['c'] == c]['ave_comp_time']
        plt.plot(X,
                 Y,
                 label=f'd:{d}, c:{c}',
                 linestyle=ls,
                 marker='.',
                 c=colors[i])
plt.xlabel(r'Maximum number of iterations')
plt.ylabel('Completion time (second)')
plt.legend(loc='upper left')
plt.tight_layout()
# tikzplotlib.save('backward_time.tex')
plt.show()

# 2-1. accuracy
plt.figure(figsize=(6, 6))
for d, ls in zip([100, 10], ['solid', 'dashed']):
    for i, c in enumerate([2, 4, 6]):
        X = df[df['d'] == d][df['c'] == c]['max_iter']
        Y = df[df['d'] == d][df['c'] == c]['ave_precision']
        plt.plot(X,
                 Y,
                 label=f'd:{d}, c:{c}',
                 linestyle=ls,
                 marker='.',
                 c=colors[i])
plt.xlabel(r'Maximum number of iterations')
plt.ylabel('Accuracy')
plt.legend(loc='lower right')
plt.tight_layout()
# tikzplotlib.save('backward_prec.tex')
plt.show()
