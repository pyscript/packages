# ---------------------------------------------------------------------
# Compare cramjam's built-in algorithms on the same input.
# ---------------------------------------------------------------------
import cramjam
import matplotlib.pyplot as plt


heading("Which algorithm should I reach for?")
note(
    "Every cramjam algorithm submodule exposes the same compress() / "
    "decompress() API, so swapping one for another is a one-line "
    "change. Let's run the same payload through several of them and "
    "see how the compressed sizes compare."
)

# A more realistic payload: a chunk of pseudo-JSON-like log lines
# mixed with some random-ish noise. Real workloads usually fall
# somewhere between "highly compressible" and "incompressible".
log_line = (
    '{"level":"INFO","msg":"request handled","user":"alice",'
    '"path":"/api/v1/items","status":200,"duration_ms":12}\n'
)
payload = (log_line * 500).encode("utf-8")
note(f"Payload size: <strong>{len(payload):,}</strong> bytes "
     "(500 repeated log lines).")

# Each entry is (display name, module). Cramjam's API is uniform
# across all of these.
algorithms = [
    ("snappy", cramjam.snappy),
    ("lz4", cramjam.lz4),
    ("gzip", cramjam.gzip),
    ("zstd", cramjam.zstd),
    ("brotli", cramjam.brotli),
    ("bzip2", cramjam.bzip2),
]

results = []
for name, mod in algorithms:
    compressed = mod.compress(payload)
    # Sanity-check that we can decompress what we just compressed.
    assert bytes(mod.decompress(compressed)) == payload
    results.append((name, len(compressed)))

# Render a small comparison table.
rows = "".join(
    f"<tr><td>{name}</td>"
    f"<td style='text-align:right'>{size:,}</td>"
    f"<td style='text-align:right'>{size / len(payload):.2%}</td></tr>"
    for name, size in results
)
display(HTML(
    "<table><thead><tr>"
    "<th>algorithm</th><th>compressed bytes</th><th>ratio</th>"
    "</tr></thead><tbody>" + rows + "</tbody></table>"
), append=True)

# And a bar chart for visual comparison.
names = [n for n, _ in results]
sizes = [s for _, s in results]

fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(names, sizes, color="teal")
ax.axhline(len(payload), color="gray", linestyle="--",
           label=f"original ({len(payload):,} bytes)")
ax.set_ylabel("Compressed size (bytes)")
ax.set_title("Compressed size by algorithm (smaller is better)")
ax.legend()
fig.tight_layout()
display(fig, append=True)
