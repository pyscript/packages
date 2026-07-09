# ---------------------------------------------------------------------
# The native xgboost.train API uses DMatrix objects directly. This is
# the lower-level interface that mirrors the Java/JVM tutorial style,
# and gives you the most control over training.
# ---------------------------------------------------------------------

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import xgboost as xgb
from sklearn.model_selection import train_test_split

rng = np.random.default_rng(7)


heading("Predicting house prices with xgboost.train")
note(
    "We'll synthesise a small housing dataset (size, age, rooms, "
    "neighborhood quality) and predict price using the native "
    "XGBoost training API and a DMatrix."
)

n = 1500
size_m2 = rng.uniform(40, 220, size=n)
age_years = rng.integers(0, 80, size=n)
rooms = rng.integers(1, 7, size=n)
quality = rng.uniform(0, 1, size=n)  # neighborhood quality score

# A noisy nonlinear "true" price function.
price_k = (
    1.8 * size_m2
    + 25 * rooms
    - 0.6 * age_years
    + 220 * quality
    + 0.05 * size_m2 * quality
    + rng.normal(0, 25, size=n)
)

houses = pd.DataFrame({
    "size_m2": size_m2.round(1),
    "age_years": age_years,
    "rooms": rooms,
    "quality": quality.round(3),
    "price_k": price_k.round(1),
})
display(houses.head(), append=True)

X = houses.drop(columns=["price_k"])
y = houses["price_k"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=7,
)

# Build DMatrix objects. DMatrix is XGBoost's optimized data container
# and accepts numpy arrays, pandas DataFrames, and more.
dtrain = xgb.DMatrix(X_train, label=y_train)
dtest = xgb.DMatrix(X_test, label=y_test)

# Parameters dict, just like the JVM tutorial.
params = {
    "objective": "reg:squarederror",
    "eval_metric": "rmse",
    "max_depth": 5,
    "eta": 0.08,
    "subsample": 0.9,
    "seed": 7,
}

# Train with a watchlist; evals_result captures metrics per round.
evals_result = {}
booster = xgb.train(
    params,
    dtrain,
    num_boost_round=300,
    evals=[(dtrain, "train"), (dtest, "test")],
    early_stopping_rounds=15,
    evals_result=evals_result,
    verbose_eval=False,
)

note(
    f"Stopped at round <strong>{booster.best_iteration}</strong>, "
    f"best test RMSE: <strong>{booster.best_score:.2f}k</strong>"
)

# Predict on the test set and plot predicted vs. actual.
y_pred = booster.predict(dtest)

fig, ax = plt.subplots(figsize=(6, 6))
ax.scatter(y_test, y_pred, alpha=0.4, color="steelblue", s=18)
lims = [min(y_test.min(), y_pred.min()), max(y_test.max(), y_pred.max())]
ax.plot(lims, lims, color="crimson", linestyle="--", label="perfect")
ax.set_xlabel("Actual price (k)")
ax.set_ylabel("Predicted price (k)")
ax.set_title("XGBoost regression: predicted vs. actual")
ax.legend()
fig.tight_layout()
display(fig, append=True)
