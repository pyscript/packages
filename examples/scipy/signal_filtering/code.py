# ---------------------------------------------------------------------
# scipy.signal: clean a noisy ECG-like signal and find its peaks.
# ---------------------------------------------------------------------

heading("Filtering a noisy heartbeat trace")
note(
    "We synthesize a 5-second signal at 250 Hz containing a 1.2 Hz "
    "heartbeat plus 60 Hz mains hum and high-frequency noise. A "
    "Butterworth low-pass filter cleans it up, and find_peaks counts "
    "the beats."
)

sample_rate = 250            # samples per second
duration = 5.0               # seconds
t = np.arange(0, duration, 1 / sample_rate)

# A heartbeat-like pulse train at ~72 bpm (1.2 Hz) using narrow Gaussians.
beat_times = np.arange(0.4, duration, 1 / 1.2)
heartbeat = sum(
    np.exp(-((t - bt) ** 2) / (2 * 0.02 ** 2)) for bt in beat_times
)

mains_hum = 0.4 * np.sin(2 * np.pi * 60 * t)
hf_noise = 0.25 * rng.standard_normal(t.size)
raw = heartbeat + mains_hum + hf_noise

# Design a 4th-order Butterworth low-pass at 8 Hz, applied with
# filtfilt for zero phase distortion.
sos = signal.butter(N=4, Wn=8, btype="lowpass", fs=sample_rate, output="sos")
clean = signal.sosfiltfilt(sos, raw)

# Locate beats: peaks at least 0.5 s apart and above a sensible height.
peaks, _ = signal.find_peaks(clean, height=0.5, distance=int(0.5 * sample_rate))
bpm = 60.0 * len(peaks) / duration
note(f"Detected <strong>{len(peaks)}</strong> beats in "
     f"{duration:.1f} s &rarr; about <strong>{bpm:.0f} bpm</strong>.")

fig, (ax_raw, ax_clean) = plt.subplots(2, 1, figsize=(9, 5), sharex=True)
ax_raw.plot(t, raw, color="lightgray")
ax_raw.set_title("Raw signal (heartbeat + 60 Hz hum + noise)")
ax_raw.set_ylabel("Amplitude")

ax_clean.plot(t, clean, color="steelblue", label="Filtered")
ax_clean.plot(t[peaks], clean[peaks], "rx", markersize=10, label="Peaks")
ax_clean.set_title("After Butterworth low-pass + peak detection")
ax_clean.set_xlabel("Time (s)")
ax_clean.set_ylabel("Amplitude")
ax_clean.legend(loc="upper right")
fig.tight_layout()
display(fig, append=True)
