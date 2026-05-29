"""
A first look at cloudpickle.

The standard library's `pickle` module can't serialize lambdas or
functions defined interactively. `cloudpickle` extends pickling to
cover these cases, which makes it the go-to tool for shipping Python
code to remote workers (Dask, Ray, Spark, multiprocessing pools, etc.).

Docs: https://github.com/cloudpipe/cloudpickle
"""
from IPython.core.display import display, HTML

heading("1. Serializing a lambda")
note(
    "Plain <code>pickle</code> refuses to serialize a lambda. "
    "<code>cloudpickle.dumps</code> handles it without complaint, "
    "and the bytes can be loaded back with the standard "
    "<code>pickle.loads</code>."
)

squared = lambda x: x ** 2

# Show that stdlib pickle fails on a lambda.
try:
    pickle.dumps(squared)
    pickle_result = "pickle succeeded (unexpected!)"
except (pickle.PicklingError, AttributeError) as exc:
    pickle_result = f"pickle.dumps raised: {type(exc).__name__}: {exc}"

note(f"Stdlib behavior: <code>{pickle_result}</code>")

# cloudpickle handles it.
payload = cloudpickle.dumps(squared)
note(f"cloudpickle produced <strong>{len(payload)}</strong> bytes.")

# The payload is normal pickle data; load it with stdlib pickle.
restored = pickle.loads(payload)
note(
    f"Restored function applied: "
    f"<code>restored(7) = {restored(7)}</code>, "
    f"<code>restored(12) = {restored(12)}</code>."
)

heading("2. Closures travel with the function")
note(
    "Functions defined here in the editor live in <code>__main__</code>, "
    "which stdlib pickle can't reach by reference. cloudpickle "
    "serializes them <em>by value</em>, including any variables they "
    "close over."
)

TAX_RATE = 0.2

def gross_to_net(amount):
    """Apply a closed-over tax rate to a gross amount."""
    return round(amount * (1 - TAX_RATE), 2)

shipped = cloudpickle.dumps(gross_to_net)
arrived = pickle.loads(shipped)

note(
    f"After a round-trip through cloudpickle, "
    f"<code>arrived(100.0) = {arrived(100.0)}</code> "
    f"and <code>arrived(57.5) = {arrived(57.5)}</code>. "
    "The closure over <code>TAX_RATE</code> survived the trip."
)
