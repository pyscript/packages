# ---------------------------------------------------------------------
# Watch validation loss during training and let XGBoost stop early.
# ---------------------------------------------------------------------

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import xgboost as xgb
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

rng = np.random.default_rng(0)


heading("Early stopping with an evaluation set")
note(
    "Boosting too long can overfit. By passing an eval_set and "
    "early_stopping_rounds, XGBoost monitors validation loss and "
    "stops when it stops improving."
)

X, y = make_classification(
    n_samples=3000,
    n_features=12,
    n_informative=6,
    random_state=1,
)
X_train, X_valid, y_train, y_valid = train_test_split(
    X, y, test_size=0.3, random_state=1, stratify=y,
)

model = xgb.XGBClassifier(
    n_estimators=500,
    max_depth=5,
    learning_rate=0.05,
    objective="binary:logistic",
    eval_metric="logloss",
    early_stopping_rounds=20,
    random_state=1,
)
model.fit(
    X_train, y_train,
    eval_set=[(X_train, y_train), (X_valid, y_valid)],
    verbose=False,
)

note(
    f"Best iteration: <strong>{model.best_iteration}</strong> "
    f"(out of 500 requested). "
    f"Best validation logloss: "
    f"<strong>{model.best_score:.4f}</strong>"
)

# evals_result_ holds the per-round metric values for each eval set.
history = model.evals_result()
train_loss = history["validation_0"]["logloss"]
valid_loss = history["validation_1"]["logloss"]

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(train_loss, label="train", color="steelblue")
ax.plot(valid_loss, label="validation", color="crimson")
ax.axvline(
    model.best_iteration, color="green", linestyle="--",
    linewidth=1, label=f"best iter ({model.best_iteration})",
)
ax.set_xlabel("Boosting round")
ax.set_ylabel("Log loss")
ax.set_title("XGBoost learning curve")
ax.legend()
fig.tight_layout()
display(fig, append=True)
