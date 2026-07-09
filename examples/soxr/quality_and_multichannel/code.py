# ---------------------------------------------------------------------
# Quality presets and multi-channel (stereo) input.
# ---------------------------------------------------------------------

heading("Quality presets on a frequency sweep")
note(
    "soxr offers several quality presets — 'QQ', 'LQ', 'MQ', 'HQ' "
    "(default), and 'VHQ'. Higher quality keeps more of the "
    "spectrum intact at the cost of CPU. Here we resample a "
    "linear sweep from 0 to 22 kHz at 48 kHz down to 16 kHz, "
    "then look at each output's magnitude spectrum."
)

source_rate = 48_000
target_rate = 16_000
duration_s = 1.0
n = int(source_rate * duration_s)
t = np.linspace(0, duration_s, n, endpoint=False)

# Linear chirp from 0 Hz to Nyquist of the source rate.
sweep = np.sin(2 * np.pi * (0.5 * (source_rate / 2) * t) * t).astype(np.float32)

presets = ["QQ", "LQ", "MQ", "HQ", "VHQ"]
fig, ax = plt.subplots(figsize=(9, 4))
for preset in presets:
    out = soxr.resample(sweep, source_rate, target_rate, quality=preset)
    spectrum = np.abs(np.fft.rfft(out))
    freqs = np.fft.rfftfreq(len(out), d=1 / target_rate)
    # Convert to dB for a more readable plot.
    magnitude_db = 20 * np.log10(spectrum / spectrum.max() + 1e-12)
    ax.plot(freqs, magnitude_db, label=preset, linewidth=1)

ax.set_xlim(0, target_rate / 2)
ax.set_ylim(-80, 5)
ax.set_xlabel("Frequency (Hz)")
ax.set_ylabel("Magnitude (dB)")
ax.set_title("Resampled chirp spectrum by quality preset")
ax.legend(title="Quality", loc="lower left")
fig.tight_layout()
display(fig, append=True)

heading("Stereo input: 2D arrays of shape (frames, channels)")
note(
    "For multi-channel audio, pass a 2D array shaped "
    "(frames, channels). soxr resamples each channel independently "
    "and preserves the layout."
)

# Build a stereo signal: left = 300 Hz, right = 600 Hz.
left = np.sin(2 * np.pi * 300 * t).astype(np.float32)
right = np.sin(2 * np.pi * 600 * t).astype(np.float32)
stereo_48k = np.stack([left, right], axis=1)

stereo_22k = soxr.resample(stereo_48k, source_rate, 22_050)

note(
    f"Input shape: <code>{stereo_48k.shape}</code> "
    f"(dtype={stereo_48k.dtype})<br>"
    f"Output shape: <code>{stereo_22k.shape}</code> "
    f"(dtype={stereo_22k.dtype})"
)
