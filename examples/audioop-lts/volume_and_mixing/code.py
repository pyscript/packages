# ---------------------------------------------------------------------
# audioop.mul, audioop.add, and audioop.minmax in action.
# ---------------------------------------------------------------------

heading("Mixing a quiet melody under a louder hum")
note(
    "We'll build two raw PCM buffers, scale them with "
    "<code>audioop.mul</code>, combine them with "
    "<code>audioop.add</code>, and then check the result."
)

sample_rate = 8000
sample_width = 2
duration_seconds = 1.0
n = int(sample_rate * duration_seconds)
t = np.linspace(0, duration_seconds, n, endpoint=False)

# A steady 120 Hz hum and a 660 Hz "melody" tone.
hum = (15000 * np.sin(2 * np.pi * 120 * t)).astype(np.int16).tobytes()
melody = (15000 * np.sin(2 * np.pi * 660 * t)).astype(np.int16).tobytes()

# Halve the melody, leave the hum at full volume, then add them.
quiet_melody = audioop.mul(melody, sample_width, 0.5)
mixed = audioop.add(hum, quiet_melody, sample_width)

# minmax returns (min_sample, max_sample) -- handy for clipping checks.
hum_range = audioop.minmax(hum, sample_width)
mixed_range = audioop.minmax(mixed, sample_width)

note(
    f"Hum sample range: <code>{hum_range}</code><br>"
    f"Mixed sample range: <code>{mixed_range}</code><br>"
    f"Mixed RMS: <strong>{audioop.rms(mixed, sample_width)}</strong>"
)

# Plot the three signals so the mixing is visible.
def to_array(pcm):
    return np.frombuffer(pcm, dtype=np.int16)


fig, axes = plt.subplots(3, 1, figsize=(9, 5), sharex=True)
window_ms = 25
visible = int(sample_rate * window_ms / 1000)
axes[0].plot(t[:visible] * 1000, to_array(hum)[:visible], color="gray")
axes[0].set_ylabel("Hum")
axes[1].plot(
    t[:visible] * 1000, to_array(quiet_melody)[:visible], color="steelblue",
)
axes[1].set_ylabel("Melody x0.5")
axes[2].plot(t[:visible] * 1000, to_array(mixed)[:visible], color="crimson")
axes[2].set_ylabel("Mixed")
axes[2].set_xlabel("Time (ms)")
fig.suptitle("Volume scaling and additive mixing")
fig.tight_layout()
display(fig, append=True)
