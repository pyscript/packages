"""
First steps with audioop: build a raw PCM tone in memory and use
audioop's analysis functions to measure it.

audioop operates on raw byte strings of signed integer PCM samples.
The `width` argument is the number of bytes per sample
(1 = 8-bit, 2 = 16-bit, 4 = 32-bit). Most audio is 16-bit.

Docs: https://docs.python.org/3.12/library/audioop.html
"""
from IPython.core.display import display, HTML

# A short 440 Hz sine wave (concert A), as 16-bit signed PCM.
sample_rate = 8000          # samples per second
duration_seconds = 0.5
frequency_hz = 440
sample_width = 2            # bytes per sample (16-bit)

t = np.linspace(
    0, duration_seconds,
    int(sample_rate * duration_seconds),
    endpoint=False,
)
amplitude = 12000           # well below the 16-bit max of 32767
samples = (amplitude * np.sin(2 * np.pi * frequency_hz * t)).astype(np.int16)

# audioop wants a bytes-like object of raw PCM frames.
tone = samples.tobytes()

heading("A 440 Hz tone, measured by audioop")
note(
    f"Generated {len(tone)} bytes of 16-bit PCM "
    f"({len(tone) // sample_width} frames at {sample_rate} Hz)."
)

# audioop.max returns the peak absolute sample value.
# audioop.rms returns the root-mean-square (a loudness proxy).
# audioop.avg returns the mean sample value (≈ 0 for a centered tone).
peak = audioop.max(tone, sample_width)
rms = audioop.rms(tone, sample_width)
mean = audioop.avg(tone, sample_width)

note(
    f"Peak amplitude: <strong>{peak}</strong><br>"
    f"RMS: <strong>{rms}</strong> "
    f"(theory says ~{int(amplitude / np.sqrt(2))})<br>"
    f"Mean sample value: <strong>{mean}</strong>"
)

# Plot the first few cycles so we can see what audioop just measured.
fig, ax = plt.subplots(figsize=(8, 3))
visible = int(sample_rate * 0.01)   # 10 ms
ax.plot(t[:visible] * 1000, samples[:visible], color="steelblue")
ax.set_title("First 10 ms of the tone")
ax.set_xlabel("Time (ms)")
ax.set_ylabel("Amplitude (int16)")
fig.tight_layout()
display(fig, append=True)
