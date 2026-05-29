# ---------------------------------------------------------------------
# Channel manipulation, sample-rate conversion, and companding.
# ---------------------------------------------------------------------

heading("Stereo split, downsample, and a µ-law round trip")
note(
    "audioop can split stereo into mono with <code>tomono</code>, "
    "build stereo from mono with <code>tostereo</code>, change the "
    "sample rate with <code>ratecv</code>, and compand 16-bit PCM "
    "to 8-bit µ-law (the classic telephone codec) with "
    "<code>lin2ulaw</code> / <code>ulaw2lin</code>."
)

# Build a stereo buffer: left = 300 Hz, right = 500 Hz, interleaved.
sample_rate = 16000
sample_width = 2
duration_seconds = 0.5
n = int(sample_rate * duration_seconds)
t = np.linspace(0, duration_seconds, n, endpoint=False)

left = (10000 * np.sin(2 * np.pi * 300 * t)).astype(np.int16)
right = (10000 * np.sin(2 * np.pi * 500 * t)).astype(np.int16)
stereo = np.empty(2 * n, dtype=np.int16)
stereo[0::2] = left
stereo[1::2] = right
stereo_bytes = stereo.tobytes()

# tomono mixes L and R with per-channel weights -> a mono buffer.
mono = audioop.tomono(stereo_bytes, sample_width, 0.5, 0.5)
note(
    f"Stereo input: {len(stereo_bytes)} bytes. "
    f"Mono mix: {len(mono)} bytes "
    f"({len(mono) // sample_width} frames)."
)

# ratecv resamples. It's stateful: pass `None` as the initial state,
# and it returns (converted_bytes, new_state) so you can chain calls.
target_rate = 8000
downsampled, _state = audioop.ratecv(
    mono, sample_width, 1, sample_rate, target_rate, None,
)
note(
    f"Resampled from {sample_rate} Hz to {target_rate} Hz: "
    f"{len(downsampled) // sample_width} frames "
    f"(RMS {audioop.rms(downsampled, sample_width)})."
)

# Round-trip through µ-law: 16-bit -> 8-bit µ-law -> 16-bit.
ulaw = audioop.lin2ulaw(downsampled, sample_width)
restored = audioop.ulaw2lin(ulaw, sample_width)
note(
    f"µ-law encoded size: {len(ulaw)} bytes "
    f"(half the linear size, as expected). "
    f"Decoded RMS: {audioop.rms(restored, sample_width)}."
)

# Visualise the original mono vs the µ-law round trip to see the
# small quantisation error introduced by 8-bit companding.
original = np.frombuffer(downsampled, dtype=np.int16)
roundtrip = np.frombuffer(restored, dtype=np.int16)
visible = 200

fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(original[:visible], color="steelblue", label="Linear PCM")
ax.plot(
    roundtrip[:visible], color="crimson", linestyle="--",
    label="After µ-law round trip",
)
ax.set_title("µ-law companding loses a little precision")
ax.set_xlabel("Frame index")
ax.set_ylabel("Sample value")
ax.legend()
fig.tight_layout()
display(fig, append=True)
