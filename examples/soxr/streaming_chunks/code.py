# ---------------------------------------------------------------------
# Streaming: feed audio in chunks, like you would in a live pipeline.
# ---------------------------------------------------------------------

heading("Streaming resampling with ResampleStream")
note(
    "For long signals or real-time audio, use <code>ResampleStream</code>. "
    "You feed it chunks of input and call <code>resample_chunk</code> "
    "for each one, marking the final chunk with <code>last=True</code> "
    "to flush the internal filter. Output chunk sizes vary — that's "
    "expected."
)

source_rate = 44_100
target_rate = 16_000
total_seconds = 2.0
chunk_size = 1024  # input frames per call

# A two-tone test signal so we can verify the output sounds right.
n_total = int(source_rate * total_seconds)
t = np.arange(n_total) / source_rate
signal = (
    0.6 * np.sin(2 * np.pi * 220 * t)
    + 0.4 * np.sin(2 * np.pi * 880 * t)
).astype(np.float32)

stream = soxr.ResampleStream(
    source_rate, target_rate, num_channels=1, dtype="float32"
)

output_chunks = []
chunk_lengths = []
position = 0
while position < n_total:
    end = min(position + chunk_size, n_total)
    is_last = end == n_total
    in_chunk = signal[position:end]
    out_chunk = stream.resample_chunk(in_chunk, last=is_last)
    output_chunks.append(out_chunk)
    chunk_lengths.append(len(out_chunk))
    position = end

resampled = np.concatenate(output_chunks)

note(
    f"Fed {len(chunk_lengths)} input chunks of "
    f"{chunk_size} frames each.<br>"
    f"First ten output chunk sizes: "
    f"<code>{chunk_lengths[:10]}</code><br>"
    f"Total output: {len(resampled)} frames @ {target_rate} Hz "
    f"(~{len(resampled) / target_rate:.3f} s)"
)

# Compare against a one-shot resample for sanity.
oneshot = soxr.resample(signal, source_rate, target_rate)
length_diff = abs(len(resampled) - len(oneshot))
note(
    f"One-shot output: {len(oneshot)} frames. "
    f"Difference vs. streamed output: {length_diff} frame(s)."
)

# Plot a small window of the streamed result.
fig, ax = plt.subplots(figsize=(9, 3.5))
window_ms = 20
n_show = int(target_rate * window_ms / 1000)
ms_axis = np.arange(n_show) / target_rate * 1000
ax.plot(ms_axis, resampled[:n_show], color="steelblue")
ax.set_xlabel("Time (ms)")
ax.set_ylabel("Amplitude")
ax.set_title(
    f"First {window_ms} ms of streamed output @ {target_rate} Hz"
)
fig.tight_layout()
display(fig, append=True)
