## Interactive Dimensionality Reduction for Comparative Analysis

About
-----
* ULCA and visual UI that can be directly used from Python and the Jupyter Notebook from: ***Interactive Dimensionality Reduction for Comparative Analysis***.
Takanori Fujiwara, Xinhai Wei, Jian Zhao, and Kwan-Liu Ma.
IEEE Transactions on Visualization and Computer Graphics and IEEE VIS 2021.
[arXiv Preprint](https://arxiv.org/abs/2106.15481)

* Demonstration video: https://takanori-fujiwara.github.io/s/ulca/index.html

* Features
  * New dimensionality reduction method, ULCA (unified linear comparative analysis). ULCA unifies and enhances linear discriminant analysis and contrastive PCA (Abid and Zhang et al., 2018).

  * Backward parameter selection of ULCA based on the user-performed changes over the embedding result.

  * Web-based visual user interface that can be directly used from Python and the Jupyter Notebook.

  * Manifold-optimization-based linear dimensionality reduction framework (implementation of the work by Cunningham and Ghahramani, 2015).

    * J. P. Cunningham and Z. Ghahramani. Linear dimensionality reduction: Survey, insights, and generalizations. J. Mach. Learn. Res., 16(1):2859-2900, 2015.

******

Content
-----
* manopt_dr: Manifold optimization based linear dimensionality reduction method generator.
* ulca: Manifold-optimization-based and EVD-based ULCA.
* ulca_ui: Visual interface that can be used from the Jupyter Notebook.
* perf_eval: Python scripts used for the performance evaluation.
* case_studies: Notebooks that demonstrate the results shown in the case studies.

******

Setup
-----

### Requirements
* Python3 (latest)
* Note: Tested on macOS Big Sur, Ubuntu 20.04 LTS, and Windows 10 with Python 3.9/3.10 and Google Chrome.

### Setup

* Install manopt_dr, ulca, and ulca_ui

  * Download/Clone this repository

  * Move to the downloaded repository, then:

    `pip3 install .`

### Usage
* See sample.py or the notebooks in the case studies directory.
  - To run sample.py from the command line, use -i option:

    `python3 -i sample.py` or `python -i sample.py`

  - Detailed documentations can be found each related source code.
    (e.g., ulca.py: there are documentations about ULCA. plot.py: ULCA's UI)

******

## How to Cite
Please, cite:    
Takanori Fujiwara, Xinhai Wei, Jian Zhao, and Kwan-Liu Ma, "Interactive Dimensionality Reduction for Comparative Analysis". IEEE Transactions on Visualization and Computer Graphics, vol. 28, no. 1, 2022.
