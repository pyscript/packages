# ---------------------------------------------------------------------
# Block-by-block processing: compute RMS energy of a fading signal
# without ever holding the whole file in memory.
# ---------------------------------------------------------------------

heading("Block processing: RMS energy of a fading chirp")
note(
    "soundfile.blocks() yields chunks of audio one at a time, which is "
    "ideal for streaming computations on long files. Here we synthesize "
    "a 4-second linear chirp that fades out, write it to an in-memory "
    "WAV file, and use blocks() to compute its short-time RMS energy."
)

samplerate = 16_000
duration_seconds = 4.0
n_frames = int(samplerate * duration_seconds)
time_axis = np.linspace(0, duration_seconds, n_frames, endpoint=False)

# Linear chirp from 200 Hz to 2000 Hz with a slow exponential fade.
start_hz, end_hz = 200.0, 2000.0
instant_phase = 2 * np.pi * (
    start_hz * time_axis
    + 0.5 * (end_hz - start_hz) / duration_seconds * time_axis ** 2
)
envelope = np.exp(-time_axis / 1.5)
chirp = (0.6 * envelope * np.sin(instant_phase)).astype(np.float32)

audio_buffer = io.BytesIO()
audio_buffer.name = "chirp.wav"
sf.write(audio_buffer, chirp, samplerate, subtype="FLOAT")

# Stream the file back in 50 ms blocks and compute RMS per block.
audio_buffer.seek(0)
block_size = int(0.05 * samplerate)  # 50 ms
rms_values = []
block_times = []
frame_cursor = 0
for block in sf.blocks(audio_buffer, blocksize=block_size, dtype="float32"):
    rms_values.append(float(np.sqrt(np.mean(block ** 2))))
    block_times.append(frame_cursor / samplerate)
    frame_cursor += len(block)

note(
    f"Processed <strong>{len(rms_values)}</strong> blocks of "
    f"{block_size} frames ({1000 * block_size / samplerate:.0f} ms each)."
)

# Random access with a SoundFile object: reopen, seek to 1.0 s,
# and read 200 ms.
audio_buffer.seek(0)
with sf.SoundFile(audio_buffer) as snd:
    note(
        f"Opened SoundFile: {snd.frames} frames, {snd.channels} channel(s), "
        f"samplerate {snd.samplerate} Hz, format {snd.format}/{snd.subtype}."
    )
    snd.seek(int(1.0 * snd.samplerate))
    excerpt = snd.read(int(0.2 * snd.samplerate))
note(
    f"Read a 200 ms excerpt starting at t=1.0 s "
    f"(shape <code>{excerpt.shape}</code>, peak "
    f"<code>{np.max(np.abs(excerpt)):.3f}</code>)."
)

# Plot the waveform alongside the per-block RMS envelope.
fig, ax = plt.subplots(figsize=(9, 3.5))
ax.plot(time_axis, chirp, color="lightgray", linewidth=0.6,
        label="Waveform")
ax.plot(block_times, rms_values, color="darkorange", linewidth=2,
        label="RMS per 50 ms block")
ax.set_title("Fading chirp: waveform and short-time RMS")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Amplitude")
ax.legend(loc="upper right")
ax.grid(True, alpha=0.3)
fig.tight_layout()
display(fig, append=True)
