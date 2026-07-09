# ---------------------------------------------------------------------
# Attributes (metadata), chunked storage, and gzip compression.
# ---------------------------------------------------------------------

heading("Storing a 2D image with metadata")
note(
    "HDF5 really shines when you attach metadata directly to your "
    "data. Every group and dataset has an <code>attrs</code> proxy "
    "that behaves like a dictionary -- perfect for units, timestamps, "
    "instrument settings, and so on."
)

# A synthetic "thermal scan" of a 128x128 surface with a hot spot.
y, x = np.mgrid[0:128, 0:128]
hot_spot = 40 * np.exp(-((x - 80) ** 2 + (y - 50) ** 2) / 400)
ambient = 18 + 0.02 * y
scan = ambient + hot_spot + rng.normal(0, 0.3, size=(128, 128))

with h5py.File("scan.h5", "w", driver="core", backing_store=False) as f:
    # `chunks=True` lets HDF5 pick a sensible chunk shape, which is
    # required for compression. `compression="gzip"` then squeezes
    # the bytes on disk -- transparent to the reader.
    dset = f.create_dataset(
        "thermal/scan_01",
        data=scan.astype(np.float32),
        chunks=True,
        compression="gzip",
        compression_opts=4,
    )

    # Attributes attach to any object. Here we describe the dataset.
    dset.attrs["units"] = "celsius"
    dset.attrs["instrument"] = "IR-2000"
    dset.attrs["captured_at"] = "2026-04-12T09:30:00Z"
    dset.attrs["calibration"] = np.array([0.98, 0.02], dtype=np.float32)

    # Attributes also work on groups, including the root group.
    f.attrs["experiment"] = "bench-test-A"
    f.attrs["operator"] = "R. Mehta"

    note(
        f"Dataset shape: {dset.shape}, chunks: {dset.chunks}, "
        f"compression: {dset.compression}"
    )

    # List attributes back out, as you would in an analysis script.
    rows = "".join(
        f"<tr><td><code>{k}</code></td><td>{v!r}</td></tr>"
        for k, v in dset.attrs.items()
    )
    display(HTML(
        "<table><tr><th>Attribute</th><th>Value</th></tr>"
        + rows + "</table>"
    ), append=True)

    # Slicing reads only the requested region from disk -- handy for
    # huge files. Here we pull a single row across the hot spot.
    row_50 = dset[50, :]

heading("Reading a slice without loading the whole dataset", level=3)
note(
    "Indexing a Dataset with NumPy syntax reads just that region. "
    "Below: a horizontal slice through row 50, where the hot spot "
    "lives."
)

fig, (ax_img, ax_line) = plt.subplots(1, 2, figsize=(9, 4))
im = ax_img.imshow(scan, cmap="inferno", origin="lower")
ax_img.axhline(50, color="cyan", linewidth=1)
ax_img.set_title("Thermal scan")
fig.colorbar(im, ax=ax_img, label="°C")

ax_line.plot(row_50, color="crimson")
ax_line.set_title("Row 50 temperature profile")
ax_line.set_xlabel("Column")
ax_line.set_ylabel("°C")
fig.tight_layout()
display(fig, append=True)
