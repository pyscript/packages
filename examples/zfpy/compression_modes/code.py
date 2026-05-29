# ---------------------------------------------------------------------
# zfp's three lossy modes: fixed-rate, fixed-precision, fixed-accuracy.
# ---------------------------------------------------------------------
#
# - rate=R       : guarantees R bits per value (predictable size).
# - precision=P  : keeps P bits of transform precision.
# - tolerance=T  : bounds the absolute error per value.
#
# Each takes the same input and produces a buffer you can decompress.

heading("One signal, three modes")
note(
    "A noisy 2D image. We sweep each mode across a few settings and "
    "plot compression ratio against the reconstruction error."
)

# A 256x256 image with structure plus a little noise.
n = 256
yy, xx = np.mgrid[0:n, 0:n] / n
image = (
    np.sin(8 * np.pi * xx) * np.cos(6 * np.pi * yy)
    + 0.3 * np.exp(-((xx - 0.5) ** 2 + (yy - 0.5) ** 2) * 30)
).astype(np.float64)
image += rng.normal(0, 0.02, size=image.shape)

original_bytes = image.nbytes


def measure(**kwargs):
    """Compress, decompress, return (ratio, max_abs_error)."""
    buf = zfpy.compress_numpy(image, write_header=True, **kwargs)
    back = zfpy.decompress_numpy(buf)
    return original_bytes / len(buf), float(np.max(np.abs(image - back)))


rates = [4, 8, 12, 16, 24]
precisions = [8, 12, 16, 20, 24]
tolerances = [1e-1, 1e-2, 1e-3, 1e-4, 1e-5]

rate_results = [measure(rate=r) for r in rates]
prec_results = [measure(precision=p) for p in precisions]
tol_results = [measure(tolerance=t) for t in tolerances]

note("Sample of results (fixed-rate mode):")
header = "<tr><th>rate (bits/val)</th><th>ratio</th><th>max error</th></tr>"
rows = "".join(
    f"<tr><td>{r}</td><td>{ratio:.1f}x</td><td>{err:.2e}</td></tr>"
    for r, (ratio, err) in zip(rates, rate_results)
)
display(HTML(f"<table border='1' cellpadding='4'>{header}{rows}</table>"),
        append=True)

# Plot all three modes on a single ratio-vs-error chart.
fig, ax = plt.subplots(figsize=(8, 5))
for label, results in [
    ("fixed-rate", rate_results),
    ("fixed-precision", prec_results),
    ("fixed-accuracy", tol_results),
]:
    ratios = [r for r, _ in results]
    errors = [e if e > 0 else 1e-16 for _, e in results]
    ax.plot(ratios, errors, marker="o", label=label)

ax.set_xlabel("Compression ratio")
ax.set_ylabel("Max absolute error")
ax.set_yscale("log")
ax.set_title("zfp compression modes: ratio vs. error")
ax.grid(True, which="both", linestyle="--", alpha=0.4)
ax.legend()
fig.tight_layout()
display(fig, append=True)
