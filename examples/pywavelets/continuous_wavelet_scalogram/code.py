# ---------------------------------------------------------------------
# Continuous Wavelet Transform: time-frequency view of a chirp.
# ---------------------------------------------------------------------

heading("A chirp: frequency that rises with time")
note(
    "The Continuous Wavelet Transform (CWT) computes the "
    "correlation between a signal and a wavelet at many scales "
    "and positions. Plotting |coefficients| as an image gives a "
    "<em>scalogram</em>: a time-on-x, frequency-on-y heatmap."
)

# Sampling: 2 seconds at 500 Hz.
sampling_rate_hz = 500.0
duration_s = 2.0
t = np.arange(0, duration_s, 1.0 / sampling_rate_hz)

# Linear chirp from 5 Hz to 60 Hz.
f_start, f_end = 5.0, 60.0
instantaneous_freq = f_start + (f_end - f_start) * t / duration_s
phase = 2 * np.pi * np.cumsum(instantaneous_freq) / sampling_rate_hz
chirp = np.sin(phase)

# Choose scales to cover ~3 Hz to ~80 Hz with the Morlet wavelet.
wavelet = "cmor1.5-1.0"
target_freqs_hz = np.linspace(3, 80, 96)
# scale_to_frequency: f = scale2frequency(wavelet, scale) * fs
# So scale = scale2frequency(wavelet, 1) * fs / f.
central = pywt.scale2frequency(wavelet, 1)
scales = central * sampling_rate_hz / target_freqs_hz

coeffs, freqs = pywt.cwt(
    chirp, scales=scales, wavelet=wavelet,
    sampling_period=1.0 / sampling_rate_hz,
)
note(
    f"CWT output shape: {coeffs.shape} "
    f"(scales x time samples). Frequencies span "
    f"{freqs.min():.1f} Hz to {freqs.max():.1f} Hz."
)

fig, (ax_signal, ax_scalogram) = plt.subplots(
    2, 1, figsize=(9, 6),
    gridspec_kw={"height_ratios": [1, 3]}, sharex=True,
)
ax_signal.plot(t, chirp, color="steelblue", linewidth=0.7)
ax_signal.set_title("Linear chirp, 5 Hz to 60 Hz")
ax_signal.set_ylabel("amplitude")

magnitude = np.abs(coeffs)
mesh = ax_scalogram.pcolormesh(
    t, freqs, magnitude, shading="auto", cmap="viridis",
)
ax_scalogram.set_title("Scalogram (|CWT coefficients|)")
ax_scalogram.set_xlabel("time (s)")
ax_scalogram.set_ylabel("frequency (Hz)")
fig.colorbar(mesh, ax=ax_scalogram, label="magnitude")

# Overlay the true instantaneous frequency.
ax_scalogram.plot(t, instantaneous_freq, color="white",
                  linestyle="--", linewidth=1.2,
                  label="true instantaneous freq")
ax_scalogram.legend(loc="upper left")

fig.tight_layout()
display(fig, append=True)
