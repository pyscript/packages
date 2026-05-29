# ---------------------------------------------------------------------
# Quirks of low-precision arithmetic: a cautionary tale.
# ---------------------------------------------------------------------

heading("Summing 10,000 small numbers in bfloat16")
note(
    "We draw 10,000 values uniformly from [0, 1). The true sum "
    "is around 5,000. Watch what happens when bfloat16 accumulates."
)

samples = rng.uniform(size=10_000).astype(bfloat16)

# Naive: accumulate in bfloat16. Once the running total reaches 256,
# adding a value below 1 has no effect (the next representable
# bfloat16 above 256 is 258).
naive_sum = samples.sum()

# Better: accumulate in float32 and cast back at the end.
careful_sum = samples.sum(dtype=np.float32).astype(bfloat16)

# Reference: full float32 sum.
true_sum = samples.astype(np.float32).sum()

note(
    f"Naive bfloat16 sum: <strong>{float(naive_sum):.1f}</strong><br>"
    f"Accumulated in float32, cast to bfloat16: "
    f"<strong>{float(careful_sum):.1f}</strong><br>"
    f"True (float32) sum: <strong>{float(true_sum):.1f}</strong>"
)

heading("Why? bfloat16's spacing grows with magnitude")
note(
    "Floating point numbers get sparser as they grow. Above 256, "
    "consecutive bfloat16 values are 2 apart, so adding 0.5 is "
    "indistinguishable from adding zero."
)

# Visualize the gap between adjacent bfloat16 values across magnitudes.
magnitudes = np.array([2.0 ** k for k in range(-4, 16)], dtype=bfloat16)
next_up = np.array(
    [np.nextafter(m, bfloat16(np.inf)) for m in magnitudes],
    dtype=bfloat16,
)
spacing = (next_up.astype(np.float32) - magnitudes.astype(np.float32))

fig, ax = plt.subplots(figsize=(8, 4))
ax.loglog(magnitudes.astype(np.float32), spacing, marker="o",
          color="crimson", label="bfloat16 spacing")
ax.axvline(256, color="gray", linestyle="--",
           label="x = 256 (spacing crosses 1)")
ax.set_xlabel("Value (x)")
ax.set_ylabel("Distance to next bfloat16")
ax.set_title("Bfloat16 quantization gap vs. magnitude")
ax.legend()
ax.grid(True, which="both", alpha=0.3)
fig.tight_layout()
display(fig, append=True)
