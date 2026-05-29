# ---------------------------------------------------------------------
# Fitting a smooth curve through noisy samples by sparse least squares.
# ---------------------------------------------------------------------

heading("Fitting a smooth signal with sparseqr.solve")
note(
    "We have 400 noisy samples of an unknown smooth signal on a grid "
    "of 120 points. We stack two sparse blocks: one that says "
    "'<em>predicted value at sample location should match the "
    "measurement</em>' and another that penalises roughness via "
    "second differences. <code>sparseqr.solve</code> finds the "
    "least-squares solution in one call."
)

n_grid = 120
n_samples = 400
smoothing_weight = 5.0

# The hidden truth: a smooth function on a uniform grid.
grid = np.linspace(0, 1, n_grid)
truth = np.sin(2 * np.pi * grid) + 0.4 * np.cos(6 * np.pi * grid)

# Random sample locations (as integer grid indices) and noisy readings.
sample_idx = rng.integers(0, n_grid, size=n_samples)
measurements = truth[sample_idx] + rng.normal(0, 0.25, size=n_samples)

# Block 1: data-fidelity. Each row picks out one grid value.
rows = np.arange(n_samples)
data_block = scipy.sparse.csr_matrix(
    (np.ones(n_samples), (rows, sample_idx)),
    shape=(n_samples, n_grid),
)

# Block 2: smoothness via second differences (x[i-1] - 2 x[i] + x[i+1]).
n_diff = n_grid - 2
diff_rows = np.repeat(np.arange(n_diff), 3)
diff_cols = np.concatenate([
    np.arange(n_diff), np.arange(1, n_diff + 1), np.arange(2, n_diff + 2),
])
diff_vals = np.tile([1.0, -2.0, 1.0], n_diff) * smoothing_weight
smooth_block = scipy.sparse.csr_matrix(
    (diff_vals, (diff_rows, diff_cols)),
    shape=(n_diff, n_grid),
)

# Stack the blocks; right-hand side has zeros for the smoothness rows.
A = scipy.sparse.vstack([data_block, smooth_block]).tocsc()
b = np.concatenate([measurements, np.zeros(n_diff)])

note(
    f"Design matrix A is {A.shape} with {A.nnz} non-zeros &mdash; far "
    f"more equations ({A.shape[0]}) than unknowns ({A.shape[1]}). "
    f"<code>sparseqr.solve</code> handles this overdetermined case "
    f"in the least-squares sense."
)

# tolerance=0 means: don't drop any columns, treat A as full-rank.
estimate = sparseqr.solve(A, b, tolerance=0)
estimate = np.asarray(estimate).ravel()

rmse = np.sqrt(np.mean((estimate - truth) ** 2))
note(f"RMSE between estimate and the hidden truth: <strong>{rmse:.3f}</strong>.")

fig, ax = plt.subplots(figsize=(9, 4))
ax.scatter(
    grid[sample_idx], measurements,
    s=12, alpha=0.35, color="gray", label="Noisy samples",
)
ax.plot(grid, truth, color="steelblue", linewidth=2, label="Hidden truth")
ax.plot(grid, estimate, color="crimson", linewidth=2,
        label="Least-squares estimate")
ax.set_xlabel("x")
ax.set_ylabel("value")
ax.set_title("Sparse least-squares fit via SuiteSparseQR")
ax.legend(loc="upper right")
fig.tight_layout()
display(fig, append=True)
