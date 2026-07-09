"""
A first look at soxr: high-quality one-dimensional sample-rate conversion.

We synthesize a short sine tone at 48 kHz, downsample it to 16 kHz with
a single call to `soxr.resample`, and confirm the duration and shape of
the output. See https://python-soxr.readthedocs.io for the full API.
"""
import numpy as np
import soxr
import matplotlib.pyplot as plt
from IPython.core.display import display, HTML

heading("Resampling a 440 Hz tone from 48 kHz to 16 kHz")
note(
    "soxr.resample takes a 1D (mono) or 2D (multi-channel) NumPy "
    "array and converts between any two sample rates. The output "
    "keeps the same dtype and dimensionality as the input."
)

# 0.25 seconds of an A4 (440 Hz) sine at the original sample rate.
source_rate = 48_000
target_rate = 16_000
duration_s = 0.25

t = np.linspace(0, duration_s, int(source_rate * duration_s), endpoint=False)
tone_48k = np.sin(2 * np.pi * 440 * t).astype(np.float32)

# A single function call performs the conversion.
tone_16k = soxr.resample(tone_48k, source_rate, target_rate)

note(
    f"Input: {tone_48k.shape[0]} samples @ {source_rate} Hz "
    f"({tone_48k.shape[0] / source_rate:.3f} s)<br>"
    f"Output: {tone_16k.shape[0]} samples @ {target_rate} Hz "
    f"({tone_16k.shape[0] / target_rate:.3f} s)<br>"
    f"libsoxr version: <code>{soxr.__libsoxr_version__}</code>"
)

# Plot the first few milliseconds of each so we can see the waveforms align.
fig, ax = plt.subplots(figsize=(9, 4))
ms = 1000
ax.plot(np.arange(len(tone_48k)) / source_rate * ms, tone_48k,
        color="lightgray", label=f"Original @ {source_rate} Hz")
ax.plot(np.arange(len(tone_16k)) / target_rate * ms, tone_16k,
        color="crimson", marker="o", markersize=3, linewidth=1,
        label=f"Resampled @ {target_rate} Hz")
ax.set_xlim(0, 10)
ax.set_xlabel("Time (ms)")
ax.set_ylabel("Amplitude")
ax.set_title("440 Hz sine: original vs. resampled")
ax.legend(loc="upper right")
fig.tight_layout()
display(fig, append=True)
