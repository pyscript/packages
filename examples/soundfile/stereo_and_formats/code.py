# ---------------------------------------------------------------------
# Stereo audio: two channels, then convert WAV -> FLAC in memory.
# ---------------------------------------------------------------------

heading("Stereo: a chord split across left and right")
note(
    "soundfile represents stereo audio as a 2D array of shape "
    "(frames, channels). Here we put a 220 Hz tone in the left "
    "channel and a 330 Hz tone in the right (a perfect fifth)."
)

samplerate = 22_050
duration_seconds = 1.5
time_axis = np.linspace(
    0, duration_seconds,
    int(samplerate * duration_seconds),
    endpoint=False,
)

left = 0.3 * np.sin(2 * np.pi * 220.0 * time_axis)
right = 0.3 * np.sin(2 * np.pi * 330.0 * time_axis)
stereo = np.column_stack([left, right])

note(f"Stereo array shape: <code>{stereo.shape}</code> (frames, channels).")

# Write as 16-bit PCM WAV in memory.
wav_buffer = io.BytesIO()
wav_buffer.name = "chord.wav"
sf.write(wav_buffer, stereo, samplerate, subtype="PCM_16")

# soundfile uses libsndfile, which supports many formats. We can
# transcode by reading one buffer and writing into another with a
# different filename suffix. FLAC is lossless and typically smaller
# than uncompressed WAV.
wav_buffer.seek(0)
data, sr = sf.read(wav_buffer)

flac_buffer = io.BytesIO()
flac_buffer.name = "chord.flac"
sf.write(flac_buffer, data, sr)

wav_size = len(wav_buffer.getvalue())
flac_size = len(flac_buffer.getvalue())
note(
    f"WAV size: <strong>{wav_size}</strong> bytes, "
    f"FLAC size: <strong>{flac_size}</strong> bytes "
    f"({100 * flac_size / wav_size:.1f}% of the WAV)."
)

# Confirm the FLAC round-trips losslessly.
flac_buffer.seek(0)
flac_data, flac_sr = sf.read(flac_buffer)
max_diff = np.max(np.abs(flac_data - data))
note(
    f"FLAC round-trip max sample difference: "
    f"<code>{max_diff:.2e}</code> (lossless within 16-bit quantization)."
)

# Plot the two channels side by side over a few cycles.
fig, (ax_left, ax_right) = plt.subplots(2, 1, figsize=(8, 4), sharex=True)
preview = int(0.02 * sr)  # first 20 ms
ax_left.plot(time_axis[:preview] * 1000, flac_data[:preview, 0],
             color="crimson")
ax_left.set_ylabel("Left (220 Hz)")
ax_left.grid(True, alpha=0.3)
ax_right.plot(time_axis[:preview] * 1000, flac_data[:preview, 1],
              color="steelblue")
ax_right.set_ylabel("Right (330 Hz)")
ax_right.set_xlabel("Time (ms)")
ax_right.grid(True, alpha=0.3)
fig.suptitle("Stereo channels decoded from FLAC")
fig.tight_layout()
display(fig, append=True)
