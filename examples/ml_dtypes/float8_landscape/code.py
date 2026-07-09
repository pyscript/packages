# ---------------------------------------------------------------------
# A tour of the smaller dtypes: float8 variants and int4.
# ---------------------------------------------------------------------

heading("How many distinct values does each format represent?")
note(
    "float8_e4m3fn favors precision (4 exponent, 3 mantissa). "
    "float8_e5m2 favors range (5 exponent, 2 mantissa). "
    "Both fit in a single byte, but they cover the number line "
    "very differently."
)

# Enumerate every byte pattern for each 8-bit float type and decode
# it to float32. This gives us the complete value set of each format.
all_bytes = np.arange(256, dtype=np.uint8)


def decode_all(dtype):
    """Return the float32 values of all 256 byte patterns for a dtype."""
    return all_bytes.view(dtype).astype(np.float32)


e4m3_values = decode_all(float8_e4m3fn)
e5m2_values = decode_all(float8_e5m2)

# Drop NaNs for plotting.
e4m3_finite = e4m3_values[np.isfinite(e4m3_values)]
e5m2_finite = e5m2_values[np.isfinite(e5m2_values)]

note(
    f"float8_e4m3fn finite values: <strong>{len(e4m3_finite)}</strong>, "
    f"max = {e4m3_finite.max():g}<br>"
    f"float8_e5m2 finite values: <strong>{len(e5m2_finite)}</strong>, "
    f"max = {e5m2_finite.max():g}"
)

# Plot the value distributions on a symlog axis so we can see how
# each format spaces its representable points.
fig, ax = plt.subplots(figsize=(9, 3.5))
ax.scatter(e4m3_finite, np.full_like(e4m3_finite, 1.0),
           s=10, color="steelblue", label="float8_e4m3fn")
ax.scatter(e5m2_finite, np.full_like(e5m2_finite, 0.0),
           s=10, color="crimson", label="float8_e5m2")
ax.set_xscale("symlog", linthresh=1e-3)
ax.set_yticks([0, 1])
ax.set_yticklabels(["e5m2", "e4m3fn"])
ax.set_xlabel("Representable value (symlog)")
ax.set_title("Where each float8 format places its points")
ax.legend(loc="upper center")
ax.grid(True, axis="x", alpha=0.3)
fig.tight_layout()
display(fig, append=True)

heading("Quantizing weights to int4")
note(
    "Sub-byte integers like int4 are stored unpacked (one per byte) "
    "but only the low 4 bits matter. Here we quantize a small "
    "weight vector to the int4 range [-8, 7]."
)

weights = rng.normal(scale=2.0, size=12).astype(np.float32)
scale = np.max(np.abs(weights)) / 7.0
quantized = np.round(weights / scale).clip(-8, 7).astype(int4)
recovered = quantized.astype(np.float32) * scale

rows = "<tr><th>original</th>" + "".join(
    f"<td>{w:+.2f}</td>" for w in weights
) + "</tr>"
rows += "<tr><th>int4 code</th>" + "".join(
    f"<td>{int(q)}</td>" for q in quantized
) + "</tr>"
rows += "<tr><th>dequantized</th>" + "".join(
    f"<td>{w:+.2f}</td>" for w in recovered
) + "</tr>"
display(HTML(f"<table>{rows}</table>"), append=True)

note(
    f"Mean absolute error after round-trip: "
    f"<strong>{np.abs(weights - recovered).mean():.3f}</strong>"
)
