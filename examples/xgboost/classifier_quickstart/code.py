"""
A first taste of XGBoost: training a gradient-boosted classifier with
the scikit-learn-style API.

XGBoost is a fast, regularized gradient boosting library widely used
for tabular machine learning. Docs: https://xgboost.readthedocs.io
"""
from IPython.core.display import display, HTML

# Example-specific imports.
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

rng = np.random.default_rng(0)


# Build a synthetic two-class problem: imagine predicting whether a
# loan applicant will repay, based on 8 anonymous features.
X, y = make_classification(
    n_samples=2000,
    n_features=8,
    n_informative=5,
    n_redundant=1,
    weights=[0.6, 0.4],
    random_state=0,
)
feature_names = [f"feat_{i}" for i in range(X.shape[1])]
X = pd.DataFrame(X, columns=feature_names)
y = pd.Series(y, name="repaid")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=0, stratify=y,
)

heading("1. Train an XGBClassifier")
note(
    "XGBoost's scikit-learn-compatible classes work with pandas "
    "DataFrames and Series. We'll train a small ensemble of 200 "
    "shallow trees."
)

model = xgb.XGBClassifier(
    n_estimators=200,
    max_depth=4,
    learning_rate=0.1,
    objective="binary:logistic",
    eval_metric="logloss",
    random_state=0,
)
model.fit(X_train, y_train)

heading("2. Evaluate on held-out data")
preds = model.predict(X_test)
probs = model.predict_proba(X_test)[:, 1]
note(f"Accuracy: <strong>{accuracy_score(y_test, preds):.3f}</strong>")

# Show the first few predictions side by side with the true labels.
preview = pd.DataFrame({
    "true": y_test.values[:8],
    "predicted": preds[:8],
    "p(repaid=1)": probs[:8].round(3),
})
display(preview, append=True)

heading("3. Which features matter most?")
note(
    "XGBoost reports a feature importance score per input column. "
    "Higher means the feature was used more often (and more "
    "effectively) for splitting trees."
)
importances = pd.Series(
    model.feature_importances_, index=feature_names,
).sort_values(ascending=False).round(3)
display(importances.to_frame("importance"), append=True)
