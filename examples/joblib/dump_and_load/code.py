# ---------------------------------------------------------------------
# joblib.dump / joblib.load: serialize Python objects (especially
# ones containing large NumPy arrays) to a single file. This is the
# canonical way to save trained models or precomputed datasets.
#
# See https://joblib.readthedocs.io/en/stable/persistence.html
# ---------------------------------------------------------------------

import os
import numpy as np
import joblib

rng = np.random.default_rng(7)


heading("Serializing objects with joblib.dump and joblib.load")
note(
    "We'll build a small dictionary holding metadata and a couple "
    "of NumPy arrays, save it to a file, then load it back and "
    "compare. <code>joblib.dump</code> handles large arrays "
    "efficiently and supports compression."
)

# A made-up "model artifact": some metadata plus learned parameters.
artifact = {
    "name": "linear-regressor",
    "version": 3,
    "feature_names": ["temperature", "humidity", "wind_speed"],
    "weights": rng.normal(size=(3,)),
    "training_samples": rng.normal(size=(1000, 3)),
}

# Save uncompressed and with compression to compare file sizes.
joblib.dump(artifact, "artifact.joblib")
joblib.dump(artifact, "artifact.joblib.gz", compress=("gzip", 3))

uncompressed_size = os.path.getsize("artifact.joblib")
compressed_size = os.path.getsize("artifact.joblib.gz")
note(
    f"Uncompressed file: <strong>{uncompressed_size:,}</strong> bytes. "
    f"Gzip-compressed (level 3): <strong>{compressed_size:,}</strong> bytes."
)

# Load the artifact back. joblib auto-detects the compression.
restored = joblib.load("artifact.joblib.gz")

note(
    f"Restored name: <code>{restored['name']}</code>, "
    f"version <code>{restored['version']}</code>, "
    f"features: <code>{restored['feature_names']}</code>."
)

weights_match = np.array_equal(restored["weights"], artifact["weights"])
samples_match = np.array_equal(
    restored["training_samples"], artifact["training_samples"],
)
note(
    f"Weights round-tripped exactly: <strong>{weights_match}</strong>. "
    f"Training samples round-tripped exactly: "
    f"<strong>{samples_match}</strong>."
)

# joblib.hash gives a stable fingerprint for arbitrary Python objects,
# which is handy for cache keys and equality checks across processes.
fingerprint = joblib.hash(artifact)
note(f"Stable fingerprint of the artifact: <code>{fingerprint}</code>.")
