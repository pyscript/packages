# ---------------------------------------------------------------------
# Tuning compression: different codecs and filters for the same data.
# ---------------------------------------------------------------------

import numpy as np
import blosc2

rng = np.random.default_rng(0)

heading("Comparing codecs on a noisy sensor signal")
note(
    "Blosc2 ships several codecs (ZSTD, LZ4, LZ4HC, BLOSCLZ, ZLIB) "
    "and pre-compression filters like SHUFFLE and BITSHUFFLE. "
    "The right combination depends on your data and what you "
    "value: speed, ratio, or both."
)

# A long 1D signal: a slow trend plus noise. Float data of this kind
# benefits a lot from byte-shuffling before compression.
n = 2_000_000
t = np.linspace(0, 100, n, dtype=np.float64)
signal = (
    np.sin(t) + 0.3 * np.sin(13 * t) + rng.normal(0, 0.05, size=n)
)

raw_mb = signal.nbytes / 1e6
note(f"Raw signal size: <strong>{raw_mb:.2f} MB</strong> "
     f"({n:,} float64 samples).")

# Each entry: (label, Codec, Filter). `cparams` lets us configure
# compression parameters per array.
trials = [
    ("BLOSCLZ + SHUFFLE",  blosc2.Codec.BLOSCLZ, blosc2.Filter.SHUFFLE),
    ("LZ4 + SHUFFLE",      blosc2.Codec.LZ4,     blosc2.Filter.SHUFFLE),
    ("LZ4 + BITSHUFFLE",   blosc2.Codec.LZ4,     blosc2.Filter.BITSHUFFLE),
    ("ZSTD + SHUFFLE",     blosc2.Codec.ZSTD,    blosc2.Filter.SHUFFLE),
    ("ZSTD + BITSHUFFLE",  blosc2.Codec.ZSTD,    blosc2.Filter.BITSHUFFLE),
]

rows = ["<table border='1' cellpadding='6' "
        "style='border-collapse:collapse'>"
        "<tr><th>Setting</th><th>Compressed (MB)</th>"
        "<th>Ratio</th></tr>"]

for label, codec, filt in trials:
    cparams = blosc2.CParams(
        codec=codec,
        filters=[filt],
        clevel=5,
    )
    arr = blosc2.asarray(signal, cparams=cparams)
    cbytes = arr.schunk.cbytes
    ratio = arr.schunk.nbytes / cbytes
    rows.append(
        f"<tr><td>{label}</td>"
        f"<td>{cbytes / 1e6:.2f}</td>"
        f"<td>{ratio:.2f}x</td></tr>"
    )

rows.append("</table>")
display(HTML("".join(rows)), append=True)

note(
    "BITSHUFFLE often beats SHUFFLE on floating-point data because "
    "it groups together bits that change slowly across samples, "
    "exposing more patterns to the back-end codec."
)
