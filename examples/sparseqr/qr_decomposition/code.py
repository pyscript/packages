"""
A first look at sparseqr: factorising a sparse matrix as Q R = M E.

SuiteSparseQR is a high-performance multithreaded sparse QR solver.
The Python wrapper exposes its three core operations: `qr` for the
factorisation itself, `solve` for least-squares-style linear systems,
and `rz` for the reduced upper-triangular form.

Project: https://github.com/yig/PySPQR
"""
from IPython.core.display import display, HTML

heading("A sparse matrix and its QR factorisation")
note(
    "We build a 200x200 sparse matrix with about 2% non-zero entries "
    "and factor it as <code>Q @ R = M @ P</code>, where "
    "<code>P</code> is a fill-reducing column permutation chosen by "
    "SuiteSparseQR."
)

# A reproducible sparse matrix.
M = scipy.sparse.random(
    200, 200, density=0.02, random_state=rng, format="csc",
)

# qr() returns Q, R (both sparse), the column permutation E as a
# 1-D array of column indices, and the numerical rank.
Q, R, E, rank = sparseqr.qr(M)

note(
    f"Matrix shape: {M.shape}, non-zeros: {M.nnz}. "
    f"Numerical rank reported by SuiteSparseQR: <strong>{rank}</strong>."
)
note(
    f"Q is {Q.shape} with {Q.nnz} non-zeros; "
    f"R is {R.shape} with {R.nnz} non-zeros. "
    f"E has length {len(E)} (a permutation of column indices)."
)

# Convert E (a permutation vector) to the equivalent permutation
# matrix so we can verify the factorisation.
P = sparseqr.permutation_vector_to_matrix(E)

# Q @ R should reproduce M @ P up to floating-point noise.
residual = abs((Q @ R - M @ P)).sum()
note(
    f"Sanity check &mdash; <code>|Q@R - M@P|</code> summed over all "
    f"entries: <strong>{residual:.2e}</strong> (should be tiny)."
)

note("First five rows and columns of R (upper triangular):")
display(R.toarray()[:5, :5].round(3), append=True)
