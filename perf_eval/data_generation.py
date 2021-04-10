#
# Authors: Takanori Fujiwara and Xinhai Wei
#
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import numpy as np

# load 20newsgroups dataset
news20 = fetch_20newsgroups()
documents = news20.data

# learning settings
n_docs_used = -1  # -1: use all

# documents to text counts/frequencies
# min_df is set for reducing # of cols of documents_cv
# to save memory when fitting with LDA
cv = CountVectorizer(min_df=0.001)
documents_cv = cv.fit_transform(documents[:n_docs_used])

# apply Latent Dirichlet Allocation to make arbitrary # of attributes
for n_topics in [10, 50, 100, 500, 1000, 5000, 10000]:
    # this is to avoid using large memory space by using many workers
    n_jobs = -1
    if n_topics > 500:
        n_jobs = 4
    if n_topics > 1000:
        n_jobs = 1

    max_iter = 50
    if n_topics > 1000:
        max_iter = 10

    print(f'processing: {n_topics} with {n_jobs} workers')

    lda = LatentDirichletAllocation(n_components=n_topics,
                                    max_iter=max_iter,
                                    n_jobs=n_jobs)
    X = lda.fit_transform(documents_cv)

    np.save(f'document_vec_{n_topics}.npy', X)

# X's rows: documents (length: n_docs_used), cols: topics (length: n_topics)
