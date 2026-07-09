"""
A first look at MNE-Python: build a synthetic multi-channel EEG
recording, wrap it in an MNE Raw object, and inspect it.

MNE-Python (https://mne.tools/) is the de facto toolkit for
M/EEG analysis. Its central data structures are `Info` (metadata
about channels and sampling) and `Raw` (continuous time series).
Here we build both from scratch using NumPy arrays.
"""
from IPython.core.display import display, HTML
import numpy as np
import matplotlib.pyplot as plt
import mne

# Quiet MNE's default INFO chatter so the example output stays focused.
mne.set_log_level("WARNING")

rng = np.random.default_rng(7)


heading("1. Building a synthetic EEG recording")
note(
    "We'll simulate 60 seconds of data on five EEG channels at "
    "250 Hz: a noisy background with an alpha-band (10 Hz) "
    "oscillation that is stronger over the occipital channels."
)

sampling_freq = 250.0  # Hz
duration_s = 60.0
n_samples = int(sampling_freq * duration_s)
times = np.arange(n_samples) / sampling_freq

channel_names = ["Fz", "Cz", "Pz", "O1", "O2"]
# Occipital channels (O1, O2) get a stronger 10 Hz alpha rhythm.
alpha_gain = np.array([0.2, 0.4, 0.8, 1.5, 1.5])

alpha = np.sin(2 * np.pi * 10.0 * times)
background = rng.normal(0, 1.0, size=(len(channel_names), n_samples))
# MNE expects EEG signals in volts; scale to microvolt-range.
data = (alpha_gain[:, None] * alpha + background) * 1e-6

# `create_info` describes the channels; combined with the data array
# it yields a Raw object that behaves like a real recording.
info = mne.create_info(
    ch_names=channel_names,
    sfreq=sampling_freq,
    ch_types="eeg",
)
raw = mne.io.RawArray(data, info)

note("The Raw object summarizes the recording:")
display(HTML(f"<pre>{raw}</pre>"), append=True)
display(HTML(f"<pre>{raw.info}</pre>"), append=True)

heading("2. Plotting the first few seconds")
note("Pulling out the first 3 seconds and plotting each channel.")

window_data, window_times = raw[:, : int(3 * sampling_freq)]

fig, ax = plt.subplots(figsize=(9, 4))
offset = 6e-6  # vertical spacing between channels, in volts
for i, name in enumerate(channel_names):
    ax.plot(
        window_times,
        window_data[i] + i * offset,
        linewidth=0.8,
        label=name,
    )
ax.set_yticks([i * offset for i in range(len(channel_names))])
ax.set_yticklabels(channel_names)
ax.set_xlabel("Time (s)")
ax.set_title("Synthetic EEG: first 3 seconds")
fig.tight_layout()
display(fig, append=True)
