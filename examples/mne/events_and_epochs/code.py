# ---------------------------------------------------------------------
# Cutting continuous data into epochs around stimulus events and
# averaging them into an evoked response.
# ---------------------------------------------------------------------

heading("From continuous data to evoked responses")
note(
    "Most M/EEG analysis revolves around three structures: Raw "
    "(continuous), Epochs (segments around events), and Evoked "
    "(epoch averages). Here we simulate an experiment with two "
    "conditions and walk through that pipeline."
)

# Build continuous data with a brief positive deflection 200 ms after
# each 'target' event and a smaller deflection after each 'standard'.
sampling_freq = 500.0
duration_s = 60.0
n_samples = int(sampling_freq * duration_s)

# One event every ~2 seconds, alternating standard/target.
event_samples = np.arange(500, n_samples - 500, 1000)
event_codes = np.where(np.arange(len(event_samples)) % 2 == 0, 1, 2)

def response_kernel(amplitude):
    # 300 ms Gaussian bump, peak around sample 100 (= 200 ms post event).
    t = np.arange(150)
    return amplitude * np.exp(-((t - 100) ** 2) / (2 * 20 ** 2))

signal = rng.normal(0, 0.3, size=n_samples)
for sample, code in zip(event_samples, event_codes):
    amp = 2.0 if code == 2 else 0.6  # targets evoke a bigger response
    end = sample + 150
    signal[sample:end] += response_kernel(amp)

# In MNE, an events array has shape (n_events, 3): sample, prev id, id.
events = np.column_stack([
    event_samples,
    np.zeros_like(event_samples),
    event_codes,
]).astype(int)
event_id = {"standard": 1, "target": 2}

info = mne.create_info(ch_names=["Cz"], sfreq=sampling_freq, ch_types="eeg")
raw = mne.io.RawArray(signal[np.newaxis, :] * 1e-6, info)

note(f"Generated {len(events)} events ({np.sum(event_codes == 2)} targets).")

# `Epochs` slices Raw into windows aligned to events. `tmin`/`tmax` are
# relative to each event (in seconds). `baseline` subtracts the mean of
# the pre-stimulus interval from each epoch.
epochs = mne.Epochs(
    raw,
    events,
    event_id=event_id,
    tmin=-0.1,
    tmax=0.5,
    baseline=(-0.1, 0.0),
    preload=True,
)

note("Epochs object summary:")
display(HTML(f"<pre>{epochs}</pre>"), append=True)

# Indexing by condition name returns the matching subset; `.average()`
# collapses across trials to produce an Evoked response.
evoked_standard = epochs["standard"].average()
evoked_target = epochs["target"].average()

heading("Evoked waveforms")
note(
    "Averaging across many noisy trials reveals the stereotyped "
    "response. Targets show a clear peak ~200 ms after the event; "
    "standards show a smaller one."
)

fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(
    evoked_standard.times * 1000,
    evoked_standard.data[0] * 1e6,
    label="Standard",
    color="steelblue",
    linewidth=2,
)
ax.plot(
    evoked_target.times * 1000,
    evoked_target.data[0] * 1e6,
    label="Target",
    color="crimson",
    linewidth=2,
)
ax.axvline(0, color="black", linestyle="--", linewidth=0.8)
ax.axhline(0, color="gray", linewidth=0.5)
ax.set_xlabel("Time relative to event (ms)")
ax.set_ylabel("Amplitude (µV)")
ax.set_title("Average evoked response at Cz")
ax.legend()
fig.tight_layout()
display(fig, append=True)
