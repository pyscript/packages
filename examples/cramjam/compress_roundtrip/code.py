"""
A first look at cramjam: tiny, dependency-free Rust-backed bindings
for popular compression algorithms.

Each algorithm lives in its own submodule (cramjam.snappy,
cramjam.gzip, cramjam.zstd, ...) and exposes the same simple pair of
functions: compress() and decompress().

Project page: https://github.com/milesgranger/pyrus-cramjam
"""
from IPython.core.display import display, HTML

import cramjam


heading("Round-tripping bytes through Snappy")
note(
    "We'll take a chunk of repetitive text, compress it with Snappy, "
    "then decompress it back to the original bytes. Repetitive data "
    "compresses well, which makes the size difference easy to see."
)

# A short passage repeated a handful of times -- repetition is what
# every compression algorithm loves.
passage = (
    "PyScript runs Python in your browser via WebAssembly. "
    "cramjam ships compression algorithms with zero system deps. "
)
original = (passage * 40).encode("utf-8")

# Compress and decompress. Both calls return a cramjam.Buffer, which
# implements the buffer protocol -- you can wrap it in bytes() or
# feed it to numpy, etc.
compressed = cramjam.snappy.compress(original)
decompressed = cramjam.snappy.decompress(compressed)

# Confirm the round-trip is lossless.
assert bytes(decompressed) == original

ratio = len(compressed) / len(original)
note(
    f"Original: <strong>{len(original)}</strong> bytes &rarr; "
    f"compressed: <strong>{len(compressed)}</strong> bytes "
    f"(ratio {ratio:.2%})."
)

note("First 80 bytes of the compressed output, shown as hex:")
display(HTML(f"<pre>{bytes(compressed)[:80].hex(' ')}</pre>"), append=True)

note("And decompressed back to the original (first 120 chars):")
display(HTML(f"<pre>{bytes(decompressed)[:120].decode('utf-8')}</pre>"),
        append=True)
