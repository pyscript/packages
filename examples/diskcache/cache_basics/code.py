"""
A first look at diskcache.

`diskcache.Cache` behaves a lot like a dictionary, but every key/value
pair is persisted to a SQLite database and a directory of files. That
makes it ideal for caching expensive computations, API responses, or
any other data you want to keep around across runs.

See the tutorial: http://www.grantjenks.com/docs/diskcache/tutorial.html
"""
from IPython.core.display import display, HTML
import time
import diskcache as dc


# A `Cache` is backed by a directory. Here we use an in-memory path
# inside the Pyodide virtual filesystem -- on a normal machine you'd
# pass something like "/var/cache/myapp".
cache = dc.Cache("/tmp/intro_cache")
cache.clear()

heading("1. Set, get, and dict-style access")
note(
    "A cache supports both an explicit API (<code>cache.set</code>, "
    "<code>cache.get</code>) and Python's mapping syntax."
)

# Mapping syntax: just like a dict.
cache["greeting"] = "hello, disk"
cache["visits"] = 0

# Explicit API: lets you pass extras like an expiry time, in seconds.
cache.set("session_token", "abc-123", expire=60)

note(f"Stored greeting: <code>{cache['greeting']!r}</code>")
note(f"Visit count starts at: <code>{cache['visits']}</code>")
note(f"Token (expires in 60s): <code>{cache.get('session_token')!r}</code>")

heading("2. Atomic increments")
note(
    "<code>cache.incr</code> performs an atomic read-modify-write, "
    "which is safe across threads and processes."
)

for _ in range(5):
    cache.incr("visits")

note(f"Visits after five increments: <code>{cache['visits']}</code>")

heading("3. Caching an expensive computation")
note(
    "We pretend <code>slow_square</code> is expensive. The first call "
    "computes and stores the result; the second hits the cache."
)


def slow_square(n):
    """Pretend this is an expensive computation."""
    time.sleep(0.05)
    return n * n


def cached_square(n):
    key = ("square", n)
    if key in cache:
        return cache[key], "cache hit"
    value = slow_square(n)
    cache[key] = value
    return value, "computed"


rows = []
for n in [7, 11, 7, 11, 13]:
    started = time.perf_counter()
    value, source = cached_square(n)
    elapsed_ms = (time.perf_counter() - started) * 1000
    rows.append(f"<tr><td>{n}</td><td>{value}</td>"
                f"<td>{source}</td><td>{elapsed_ms:.1f} ms</td></tr>")

display(HTML(
    "<table border='1' cellpadding='4' style='border-collapse:collapse'>"
    "<tr><th>n</th><th>n²</th><th>source</th><th>elapsed</th></tr>"
    + "".join(rows) + "</table>"
), append=True)

note(f"Cache currently holds <strong>{len(cache)}</strong> keys.")
cache.close()
