# ---------------------------------------------------------------------
# compress_into / decompress_into: writing directly into a target.
# ---------------------------------------------------------------------

heading("Avoiding extra allocations with compress_into")
note(
    "When you already have a buffer to write into -- a numpy array, "
    "a bytearray, or a cramjam.Buffer -- you can use compress_into() "
    "and decompress_into() to skip an intermediate allocation. They "
    "return the number of bytes written."
)

# Build some structured numeric data: 50,000 little-endian uint16
# samples that look like a noisy sine wave. Numeric arrays are a
# great fit for cramjam because they expose the buffer protocol.
n_samples = 50_000
t = np.arange(n_samples, dtype=np.float64)
signal = (10_000 + 5_000 * np.sin(t * 2 * np.pi / 200)).astype(np.uint16)

# As raw bytes, this is the input we'll compress.
raw = signal.tobytes()
note(f"Input: {n_samples:,} uint16 samples = "
     f"<strong>{len(raw):,}</strong> bytes.")

# cramjam.Buffer is a growable, file-like byte container that
# implements the buffer protocol. It's the natural target for
# compress_into / decompress_into.
compressed = cramjam.Buffer()
n_written = cramjam.zstd.compress_into(raw, compressed)
note(f"compress_into wrote <strong>{n_written:,}</strong> bytes "
     f"into the Buffer (position is now {compressed.tell()}).")

# Rewind the buffer so the decompressor reads from the start.
compressed.seek(0)

# Pre-allocate the destination as a numpy array of the right size
# and decompress straight into its memory.
restored = np.empty(n_samples, dtype=np.uint16)
n_read = cramjam.zstd.decompress_into(compressed, restored)
note(f"decompress_into wrote <strong>{n_read:,}</strong> bytes "
     "directly into the numpy array.")

# Verify the round-trip preserved every sample.
assert np.array_equal(restored, signal)
note("Round-trip verified: every sample matches the original.")

# Show a tiny preview of the recovered samples.
preview = ", ".join(str(int(x)) for x in restored[:12])
display(HTML(f"<pre>first 12 samples: {preview}, ...</pre>"), append=True)
