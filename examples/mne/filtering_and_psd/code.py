# ---------------------------------------------------------------------
# Filtering a Raw object and inspecting its frequency content.
# ---------------------------------------------------------------------

heading("Cleaning a noisy signal with band-pass filtering")
note(
    "We'll build a single-channel Raw with a 10 Hz alpha rhythm, "
    "a 50 Hz line-noise contaminant, and slow drift. Then we apply "
    "a band-pass filter and compare power spectra before and after."
)

sampling_freq = 500.0
duration_s = 30.0
n_samples = int(sampling_freq * duration_s)
times = np.arange(n_samples) / sampling_freq

alpha = 1.0 * np.sin(2 * np.pi * 10.0 * times)
line_noise = 0.8 * np.sin(2 * np.pi * 50.0 * times)
slow_drift = 1.2 * np.sin(2 * np.pi * 0.3 * times)
white_noise = rng.normal(0, 0.5, size=n_samples)

# Combined signal in microvolt-range, scaled to volts for MNE.
signal = (alpha + line_noise + slow_drift + white_noise) * 1e-6

info = mne.create_info(ch_names=["Oz"], sfreq=sampling_freq, ch_types="eeg")
raw = mne.io.RawArray(signal[np.newaxis, :], info)

# `copy()` keeps the original around so we can compare. `filter` is
# an in-place band-pass between 1 Hz and 40 Hz, removing both slow
# drift and the 50 Hz line noise.
raw_filtered = raw.copy().filter(l_freq=1.0, h_freq=40.0)

heading("Comparing the time series")
note("First two seconds before and after filtering:")

n_show = int(2 * sampling_freq)
raw_data, raw_times = raw[0, :n_show]
filt_data, _ = raw_filtered[0, :n_show]

fig, axes = plt.subplots(2, 1, figsize=(9, 5), sharex=True)
axes[0].plot(raw_times, raw_data[0] * 1e6, color="gray")
axes[0].set_title("Raw signal (µV)")
axes[1].plot(raw_times, filt_data[0] * 1e6, color="darkgreen")
axes[1].set_title("Band-pass 1-40 Hz (µV)")
axes[1].set_xlabel("Time (s)")
fig.tight_layout()
display(fig, append=True)

heading("Power spectral density")
note(
    "MNE's `compute_psd` uses Welch's method by default. The alpha "
    "peak around 10 Hz survives filtering, while the 50 Hz line and "
    "low-frequency drift are strongly attenuated."
)

psd_raw = raw.compute_psd(fmin=0.1, fmax=80.0)
psd_filt = raw_filtered.compute_psd(fmin=0.1, fmax=80.0)

freqs = psd_raw.freqs
power_raw = psd_raw.get_data()[0]
power_filt = psd_filt.get_data()[0]

fig, ax = plt.subplots(figsize=(9, 4))
ax.semilogy(freqs, power_raw, color="gray", label="Raw")
ax.semilogy(freqs, power_filt, color="darkgreen", label="Filtered")
ax.axvline(10, color="steelblue", linestyle="--", linewidth=1,
           label="Alpha (10 Hz)")
ax.axvline(50, color="crimson", linestyle="--", linewidth=1,
           label="Line (50 Hz)")
ax.set_xlabel("Frequency (Hz)")
ax.set_ylabel("Power (V²/Hz)")
ax.set_title("Power spectral density")
ax.legend()
fig.tight_layout()
display(fig, append=True)
