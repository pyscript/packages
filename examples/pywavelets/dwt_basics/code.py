"""
A first look at PyWavelets.

The Discrete Wavelet Transform (DWT) splits a signal into
"approximation" coefficients (a smoothed version) and "detail"
coefficients (the high-frequency wiggle that was filtered out).
We use it here to denoise a noisy sine wave and see the parts of
the signal at different scales.

Docs: https://pywavelets.readthedocs.io/
"""
from IPython.core.display import display, HTML
import numpy as np
import matplotlib.pyplot as plt
import pywt

rng = np.random.default_rng(7)


heading("Built-in wavelet families")
note(
    "PyWavelets ships with over 100 wavelet filters. They are "
    "grouped into families like Daubechies (db), Symlets (sym), "
    "and Coiflets (coif). Here are the family short names:"
)
display(HTML("<code>" + ", ".join(pwt for pwt in pywt.families()) + "</code>"),
        append=True)

heading("A noisy heartbeat-like signal")
note(
    "We build a synthetic signal: two sine components plus Gaussian "
    "noise, sampled at 512 points."
)

n_samples = 512
t = np.linspace(0, 1, n_samples, endpoint=False)
clean = np.sin(2 * np.pi * 7 * t) + 0.5 * np.sin(2 * np.pi * 23 * t)
noisy = clean + 0.4 * rng.standard_normal(n_samples)

# Single-level DWT with the Daubechies-4 wavelet.
approx, detail = pywt.dwt(noisy, "db4")
note(
    f"Original length: {len(noisy)}. After one level of DWT with 'db4': "
    f"approximation has {len(approx)} coefficients and detail has "
    f"{len(detail)} coefficients (each roughly half the input length)."
)

# Reconstruct the signal exactly from the two coefficient arrays.
reconstructed = pywt.idwt(approx, detail, "db4")
max_error = np.max(np.abs(noisy - reconstructed[: len(noisy)]))
note(f"DWT followed by IDWT is lossless. Max reconstruction error: "
     f"{max_error:.2e}")

# Plot the noisy signal alongside the approximation and detail.
fig, axes = plt.subplots(3, 1, figsize=(9, 6), sharex=False)
axes[0].plot(t, noisy, color="gray", linewidth=0.8)
axes[0].plot(t, clean, color="crimson", linewidth=1.2, alpha=0.7,
             label="clean")
axes[0].set_title("Noisy signal (gray) with underlying clean signal (red)")
axes[0].legend(loc="upper right")

axes[1].plot(approx, color="steelblue")
axes[1].set_title("Approximation coefficients (low-frequency content)")

axes[2].plot(detail, color="darkorange")
axes[2].set_title("Detail coefficients (high-frequency content + noise)")

fig.tight_layout()
display(fig, append=True)
