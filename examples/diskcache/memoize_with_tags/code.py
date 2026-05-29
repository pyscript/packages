# ---------------------------------------------------------------------
# Memoize a function and group results with tags for selective eviction.
# ---------------------------------------------------------------------

heading("Memoize a function with @cache.memoize")
note(
    "<code>@cache.memoize</code> turns any deterministic function into "
    "a cached one. We tag entries by category so we can evict a whole "
    "group at once with <code>cache.evict(tag)</code>."
)

cache = dc.Cache("/tmp/memoize_cache")
cache.clear()


@cache.memoize(tag="reports", expire=3600)
def quarterly_report(region, quarter):
    """Pretend this query hits a slow analytics warehouse."""
    time.sleep(0.05)
    base = sum(ord(c) for c in region)
    return {"region": region, "quarter": quarter, "revenue": base * quarter}


@cache.memoize(tag="forecasts")
def forecast(region):
    """A second 'expensive' function, tagged differently."""
    time.sleep(0.05)
    return f"{region}: outlook stable"


# Call each function a few times. Repeats should be much faster.
calls = [
    ("reports", lambda: quarterly_report("North", 1)),
    ("reports", lambda: quarterly_report("North", 1)),  # cached
    ("reports", lambda: quarterly_report("South", 2)),
    ("forecasts", lambda: forecast("North")),
    ("forecasts", lambda: forecast("North")),           # cached
]

rows = []
for label, fn in calls:
    started = time.perf_counter()
    result = fn()
    elapsed_ms = (time.perf_counter() - started) * 1000
    rows.append(
        f"<tr><td>{label}</td><td><code>{result}</code></td>"
        f"<td>{elapsed_ms:.1f} ms</td></tr>"
    )

display(HTML(
    "<table border='1' cellpadding='4' style='border-collapse:collapse'>"
    "<tr><th>tag</th><th>result</th><th>elapsed</th></tr>"
    + "".join(rows) + "</table>"
), append=True)

note(f"Total cached entries: <strong>{len(cache)}</strong>")

# Evict only the "reports" group. Forecasts stay cached.
evicted = cache.evict("reports")
note(
    f"Evicted <strong>{evicted}</strong> entries tagged 'reports'. "
    f"Remaining entries: <strong>{len(cache)}</strong> "
    "(the forecasts survived)."
)

# A subsequent reports call recomputes; a forecast call still hits cache.
started = time.perf_counter()
quarterly_report("North", 1)
report_ms = (time.perf_counter() - started) * 1000

started = time.perf_counter()
forecast("North")
forecast_ms = (time.perf_counter() - started) * 1000

note(
    f"After eviction: report recomputed in <strong>{report_ms:.1f} ms</strong>, "
    f"forecast served from cache in <strong>{forecast_ms:.1f} ms</strong>."
)
cache.close()
