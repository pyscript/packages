"""
A first look at python-blosc2: building a compressed NDArray, peeking
at its compression stats, and reading slices back as plain NumPy.

Blosc2 is a fast, chunked, compressed N-dimensional array library. You
can think of an NDArray as a NumPy-like object whose data lives in
compressed chunks, in memory or on disk.

Docs: https://www.blosc.org/python-blosc2/python-blosc2.html
"""
from IPython.core.display import display, HTML

heading("Compressing a 2D temperature grid")
note(
    "We simulate a 1000x1000 temperature field with smooth spatial "
    "structure: exactly the kind of data that compresses very well."
)

# Build a smooth, compressible field: a sum of sinusoids plus a touch
# of noise. Smooth data has lots of redundancy for Blosc2 to exploit.
y, x = np.indices((1000, 1000))
field = (
    20.0
    + 5.0 * np.sin(x / 80.0)
    + 3.0 * np.cos(y / 60.0)
    + rng.normal(0, 0.1, size=(1000, 1000))
).astype(np.float32)

# `asarray` wraps an existing NumPy array as a compressed NDArray.
# Blosc2 picks sensible chunk and block sizes automatically.
compressed = blosc2.asarray(field)

note(
    f"NDArray shape: <code>{compressed.shape}</code>, "
    f"dtype: <code>{compressed.dtype}</code>, "
    f"chunks: <code>{compressed.chunks}</code>, "
    f"blocks: <code>{compressed.blocks}</code>."
)

# Compare uncompressed vs. compressed sizes via the schunk attribute.
uncompressed_bytes = compressed.schunk.nbytes
compressed_bytes = compressed.schunk.cbytes
ratio = uncompressed_bytes / compressed_bytes

note(
    f"Uncompressed: <strong>{uncompressed_bytes / 1e6:.2f} MB</strong>, "
    f"compressed: <strong>{compressed_bytes / 1e6:.2f} MB</strong>, "
    f"ratio: <strong>{ratio:.1f}x</strong>."
)

heading("Slicing returns plain NumPy arrays")
note(
    "Indexing an NDArray with NumPy-style slices decompresses just "
    "the requested region and returns a regular ndarray."
)

corner = compressed[:4, :4]
display(HTML(f"<pre>{np.array2string(corner, precision=2)}</pre>"),
        append=True)

# Round-trip check: decompress everything and compare against the
# original NumPy field.
roundtrip = compressed[:]
note(
    f"Round-trip lossless? "
    f"<strong>{np.array_equal(roundtrip, field)}</strong>"
)
