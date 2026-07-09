# ---------------------------------------------------------------------
# Multilevel DWT: a classic wavelet denoising recipe.
# ---------------------------------------------------------------------

heading("Multilevel decomposition: a piecewise signal with noise")
note(
    "Real signals often have features at many scales. "
    "`wavedec` decomposes a signal into one approximation array "
    "plus several detail arrays, one per level."
)

n_samples = 1024
t = np.linspace(0, 1, n_samples, endpoint=False)

# Piecewise signal: a smooth ramp, a flat region, and a sine burst.
clean = np.where(t < 0.3, 2 * t,
         np.where(t < 0.6, 0.6,
                  0.6 + 0.8 * np.sin(2 * np.pi * 12 * (t - 0.6))))
noise_sigma = 0.25
noisy = clean + noise_sigma * rng.standard_normal(n_samples)

# Decompose to 4 levels with the symlet-8 wavelet.
wavelet = "sym8"
coeffs = pywt.wavedec(noisy, wavelet, level=4)
sizes = [len(c) for c in coeffs]
note(
    f"`wavedec` returned {len(coeffs)} arrays for a 4-level "
    f"decomposition: 1 approximation + 4 detail levels. "
    f"Lengths (coarse to fine): {sizes}."
)

# Universal threshold (Donoho & Johnstone): sigma * sqrt(2 * log(n)).
# Estimate sigma robustly from the finest detail level using its MAD.
finest_detail = coeffs[-1]
sigma_est = np.median(np.abs(finest_detail)) / 0.6745
threshold = sigma_est * np.sqrt(2 * np.log(n_samples))
note(f"Estimated noise sigma: {sigma_est:.3f}. "
     f"Universal threshold: {threshold:.3f}.")

# Soft-threshold every detail level; leave the approximation alone.
denoised_coeffs = [coeffs[0]] + [
    pywt.threshold(c, value=threshold, mode="soft") for c in coeffs[1:]
]
denoised = pywt.waverec(denoised_coeffs, wavelet)[: len(noisy)]

rmse_noisy = np.sqrt(np.mean((noisy - clean) ** 2))
rmse_denoised = np.sqrt(np.mean((denoised - clean) ** 2))
note(
    f"RMSE before denoising: <strong>{rmse_noisy:.3f}</strong>. "
    f"After wavelet soft-thresholding: "
    f"<strong>{rmse_denoised:.3f}</strong>."
)

fig, axes = plt.subplots(3, 1, figsize=(9, 6), sharex=True)
axes[0].plot(t, clean, color="black")
axes[0].set_title("Clean signal")
axes[1].plot(t, noisy, color="gray", linewidth=0.8)
axes[1].set_title("Noisy signal")
axes[2].plot(t, denoised, color="seagreen")
axes[2].plot(t, clean, color="black", linewidth=0.8, alpha=0.4,
             label="clean")
axes[2].set_title(f"Denoised ({wavelet}, soft threshold)")
axes[2].legend(loc="upper right")
fig.tight_layout()
display(fig, append=True)
