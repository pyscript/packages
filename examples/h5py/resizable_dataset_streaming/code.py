# ---------------------------------------------------------------------
# Resizable datasets: append batches of data as they arrive.
# ---------------------------------------------------------------------

heading("Streaming sensor batches into a resizable dataset")
note(
    "When you don't know the final size up front -- a logger, a "
    "training run, an instrument feed -- create a dataset with "
    "<code>maxshape</code> that allows growth, then call "
    "<code>resize()</code> before each append."
)

batch_size = 100
num_batches = 12

with h5py.File("stream.h5", "w", driver="core", backing_store=False) as f:
    # maxshape=(None,) means "this axis can grow without limit".
    # Chunking is required for resizable datasets.
    readings = f.create_dataset(
        "sensor/readings",
        shape=(0,),
        maxshape=(None,),
        dtype="float32",
        chunks=(batch_size,),
    )
    readings.attrs["sample_rate_hz"] = 50

    # Simulate batches arriving one at a time.
    drift = 0.0
    for i in range(num_batches):
        drift += rng.normal(0, 0.1)
        batch = rng.normal(loc=drift, scale=1.0, size=batch_size)

        # Grow the dataset, then write into the new tail region.
        new_length = readings.shape[0] + batch.size
        readings.resize((new_length,))
        readings[-batch.size:] = batch.astype("float32")

    note(
        f"After {num_batches} batches the dataset holds "
        f"<strong>{readings.shape[0]}</strong> samples "
        f"(chunk size: {readings.chunks[0]})."
    )

    # Read it all back in one go for plotting.
    all_samples = readings[...]

# Plot the streamed signal with batch boundaries marked.
fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(all_samples, color="steelblue", linewidth=0.8)
for boundary in range(batch_size, num_batches * batch_size, batch_size):
    ax.axvline(boundary, color="lightgray", linewidth=0.5)
ax.set_title("Streamed samples (batch boundaries in gray)")
ax.set_xlabel("Sample index")
ax.set_ylabel("Reading")
fig.tight_layout()
display(fig, append=True)

heading("Why this matters", level=3)
note(
    "The same pattern scales from a few hundred samples to billions: "
    "HDF5 stores chunks independently, so appending is cheap and "
    "readers can slice into any region without touching the rest of "
    "the file. Combined with attributes and groups, you get a "
    "self-describing archive that's easy to share with collaborators."
)
