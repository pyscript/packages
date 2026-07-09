"""
First look at joblib: cache expensive function results to disk
(in Pyodide, an in-memory virtual file system) so repeated calls
return instantly.

See https://joblib.readthedocs.io/en/stable/memory.html
"""
from IPython.core.display import display, HTML

import time
import numpy as np
from joblib import Memory


# A Memory object is the entry point for caching. The `location`
# is a directory where results are persisted; in Pyodide this is
# the in-browser virtual file system, so caches survive within a
# session.
memory = Memory(location="./joblib_cache", verbose=0)


@memory.cache
def slow_square_sum(n):
    """Pretend-expensive computation: sum of squares up to n."""
    # Simulate a costly step so the cache benefit is obvious.
    time.sleep(0.5)
    arr = np.arange(n, dtype=np.int64)
    return int((arr * arr).sum())


heading("Caching with joblib.Memory")
note(
    "We decorate <code>slow_square_sum</code> with "
    "<code>@memory.cache</code>. The first call computes and "
    "stores the result; later calls with the same argument are "
    "served from the cache."
)

# First call: actually computes (and writes to the cache).
start = time.perf_counter()
result_first = slow_square_sum(200_000)
first_elapsed = time.perf_counter() - start

# Second call with the same input: hits the cache.
start = time.perf_counter()
result_cached = slow_square_sum(200_000)
cached_elapsed = time.perf_counter() - start

# Different input: computes again, populating a new cache entry.
start = time.perf_counter()
result_other = slow_square_sum(50_000)
other_elapsed = time.perf_counter() - start

note(
    f"First call (n=200,000): result={result_first:,}, "
    f"took <strong>{first_elapsed:.3f}s</strong>."
)
note(
    f"Repeat call (n=200,000): result={result_cached:,}, "
    f"took <strong>{cached_elapsed:.3f}s</strong> (cache hit)."
)
note(
    f"New input (n=50,000): result={result_other:,}, "
    f"took <strong>{other_elapsed:.3f}s</strong>."
)

# You can wipe the cache when you want to force recomputation.
memory.clear(warn=False)
note("Called <code>memory.clear()</code> to remove all cached entries.")
