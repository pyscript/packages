# ---------------------------------------------------------------------
# joblib.Parallel: write a parallel loop with the same shape as a
# sequential one. The recipe is:
#
#     Parallel(n_jobs=...)(delayed(func)(arg) for arg in args)
#
# `delayed` captures the call without invoking it, and `Parallel`
# dispatches the captured calls. See:
# https://joblib.readthedocs.io/en/stable/parallel.html
# ---------------------------------------------------------------------

heading("Parallel loops with joblib")
note(
    "We'll estimate &pi; with a Monte Carlo simulation, splitting "
    "the work across several batches. Each batch throws random "
    "darts at the unit square and counts those landing inside the "
    "quarter circle of radius 1."
)


def estimate_pi_batch(n_samples, seed):
    """Return 4 * (fraction of points inside the unit circle)."""
    local_rng = np.random.default_rng(seed)
    xs = local_rng.random(n_samples)
    ys = local_rng.random(n_samples)
    inside = int(((xs * xs + ys * ys) <= 1.0).sum())
    return 4.0 * inside / n_samples


# Eight batches of 50,000 samples, each with its own seed.
batch_size = 50_000
seeds = list(range(8))

# Sequential baseline: a plain list comprehension.
start = time.perf_counter()
sequential_estimates = [estimate_pi_batch(batch_size, s) for s in seeds]
sequential_elapsed = time.perf_counter() - start

# Parallel version: same shape, wrapped in Parallel/delayed.
# n_jobs=2 keeps the demo lightweight; -1 would use all CPUs.
start = time.perf_counter()
parallel_estimates = Parallel(n_jobs=2)(
    delayed(estimate_pi_batch)(batch_size, s) for s in seeds
)
parallel_elapsed = time.perf_counter() - start

combined_pi = float(np.mean(parallel_estimates))
note(
    f"Combined estimate of &pi; from {len(seeds)} batches: "
    f"<strong>{combined_pi:.5f}</strong> "
    f"(error vs math.pi: {abs(combined_pi - math.pi):.5f})."
)
note(
    f"Sequential loop: {sequential_elapsed:.3f}s. "
    f"Parallel loop: {parallel_elapsed:.3f}s."
)

# Plot the per-batch estimates against the true value.
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(seeds, parallel_estimates, "o-", color="steelblue",
        label="Per-batch estimate")
ax.axhline(math.pi, color="crimson", linestyle="--",
           label="math.pi")
ax.set_xlabel("Batch (seed)")
ax.set_ylabel("Estimate of \u03c0")
ax.set_title("Monte Carlo estimates of \u03c0 across parallel batches")
ax.legend()
fig.tight_layout()
display(fig, append=True)
