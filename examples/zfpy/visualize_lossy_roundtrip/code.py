# ---------------------------------------------------------------------
# What does aggressive compression actually look like?
# ---------------------------------------------------------------------
#
# zfp partitions the array into small blocks (4x4, 4x4x4, ...) and
# compresses each block independently. At very high ratios you can
# sometimes see this block structure in the reconstruction. Let's
# make that visible on a synthetic "scientific" image.

import numpy as np
import matplotlib.pyplot as plt
import zfpy

rng = np.random.default_rng(0)


heading("Side-by-side: original vs. reconstructions")
note(
    "We compress the same field at three fixed rates and compare each "
    "reconstruction (and its error) against the original."
)

# A field with both broad structure and fine detail.
n = 192
yy, xx = np.mgrid[0:n, 0:n] / n
field = (
    np.exp(-((xx - 0.3) ** 2 + (yy - 0.4) ** 2) * 20)
    + 0.6 * np.exp(-((xx - 0.7) ** 2 + (yy - 0.6) ** 2) * 60)
    + 0.2 * np.sin(20 * np.pi * xx) * np.sin(20 * np.pi * yy)
).astype(np.float64)

rates = [2, 6, 14]  # bits per value: very tight -> generous
reconstructions = []
for rate in rates:
    buf = zfpy.compress_numpy(field, rate=rate, write_header=True)
    back = zfpy.decompress_numpy(buf)
    ratio = field.nbytes / len(buf)
    reconstructions.append((rate, ratio, back))

fig, axes = plt.subplots(2, len(rates) + 1, figsize=(11, 6))

# Top-left: original. Bottom-left: blank placeholder.
axes[0, 0].imshow(field, cmap="viridis")
axes[0, 0].set_title("Original")
axes[0, 0].axis("off")
axes[1, 0].axis("off")
axes[1, 0].text(0.5, 0.5, "errors -->", ha="center", va="center",
                fontsize=12, transform=axes[1, 0].transAxes)

# Each column: reconstruction on top, error map on bottom.
for col, (rate, ratio, back) in enumerate(reconstructions, start=1):
    axes[0, col].imshow(back, cmap="viridis",
                        vmin=field.min(), vmax=field.max())
    axes[0, col].set_title(f"rate={rate} bpv\n({ratio:.0f}x)")
    axes[0, col].axis("off")

    err = back - field
    lim = max(abs(err.min()), abs(err.max()), 1e-9)
    axes[1, col].imshow(err, cmap="RdBu", vmin=-lim, vmax=lim)
    axes[1, col].set_title(f"max |err| = {np.abs(err).max():.2e}")
    axes[1, col].axis("off")

fig.suptitle("zfp fixed-rate reconstruction vs. error")
fig.tight_layout()
display(fig, append=True)

note(
    "At very low bit rates you can sometimes spot zfp's 4x4 block "
    "boundaries in the error map &mdash; a reminder that compression "
    "is local. Increase the rate (or switch to fixed-accuracy) when "
    "your downstream analysis is sensitive to those artifacts."
)
