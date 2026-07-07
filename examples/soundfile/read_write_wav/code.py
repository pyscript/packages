"""
A first look at python-soundfile.

soundfile reads and writes audio files using libsndfile, exchanging
audio data as NumPy arrays. Here we synthesize a short tone, write
it to an in-memory WAV file, then read it back and inspect what
soundfile tells us about the file.

Docs: https://python-soundfile.readthedocs.io/
"""
from IPython.core.display import display, HTML

import io
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt


heading("A short A4 tone (440 Hz)")
note(
    "We'll generate one second of a 440 Hz sine wave at 22,050 Hz "
    "sample rate, write it to an in-memory WAV buffer, and read it "
    "back with soundfile."
)

samplerate = 22_050
duration_seconds = 1.0
frequency_hz = 440.0

time_axis = np.linspace(
    0, duration_seconds,
    int(samplerate * duration_seconds),
    endpoint=False,
)
tone = 0.3 * np.sin(2 * np.pi * frequency_hz * time_axis)

# soundfile.write accepts any file-like object. We give the buffer a
# .name attribute so libsndfile can infer the format from the suffix.
wav_buffer = io.BytesIO()
wav_buffer.name = "tone.wav"
sf.write(wav_buffer, tone, samplerate, subtype="PCM_16")

note(f"Encoded WAV size: <strong>{len(wav_buffer.getvalue())}</strong> bytes.")

# sf.info inspects a file's metadata without loading the audio.
wav_buffer.seek(0)
info = sf.info(wav_buffer)
note(
    f"Format: {info.format} ({info.subtype}), "
    f"channels: {info.channels}, frames: {info.frames}, "
    f"samplerate: {info.samplerate} Hz, "
    f"duration: {info.duration:.3f} s."
)

# Read the audio back. Returns (data, samplerate).
wav_buffer.seek(0)
data, sr = sf.read(wav_buffer)
note(
    f"Read back <strong>{data.shape[0]}</strong> frames at "
    f"{sr} Hz. dtype: <code>{data.dtype}</code>."
)

# Plot the first few milliseconds so we can see the waveform.
fig, ax = plt.subplots(figsize=(8, 3))
preview_samples = int(0.01 * sr)  # first 10 ms
ax.plot(time_axis[:preview_samples] * 1000, data[:preview_samples],
        color="steelblue")
ax.set_title("First 10 ms of the decoded tone")
ax.set_xlabel("Time (ms)")
ax.set_ylabel("Amplitude")
ax.grid(True, alpha=0.3)
fig.tight_layout()
display(fig, append=True)
