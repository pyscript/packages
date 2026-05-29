"""
Deferred construction with `lazy_object_proxy.Proxy`.

A `Proxy` wraps a zero-argument callable (the "factory") and looks
and feels like the eventual return value, but the factory is only
invoked the first time the proxy is actually used. After that the
result is cached and the proxy transparently forwards every
attribute access, method call, and operator to the real object.

Docs: https://python-lazy-object-proxy.readthedocs.io/
"""
from IPython.core.display import display, HTML

heading("A proxy that pretends to be an expensive report")
note(
    "Imagine loading a large report from disk or the network. We "
    "don't want to pay that cost unless someone actually reads it."
)

# A counter we can inspect to see when (and how often) the factory runs.
build_calls = {"count": 0}


def build_quarterly_report():
    """Pretend to do expensive work and return a dict 'report'."""
    build_calls["count"] += 1
    return {
        "quarter": "Q3",
        "revenue": 184_500.00,
        "top_product": "Aurora Notebook",
        "units_sold": 1273,
    }


# Wrap the factory. No work happens here.
report = lazy_object_proxy.Proxy(build_quarterly_report)

note(
    f"Proxy created. Factory call count so far: "
    f"<strong>{build_calls['count']}</strong>"
)

# `__resolved__` tells us whether the factory has been called yet.
note(f"Has the proxy been resolved? <strong>{report.__resolved__}</strong>")

# First real use: indexing triggers the factory exactly once.
heading("First touch triggers the factory", level=3)
note(f"Top product: <strong>{report['top_product']}</strong>")
note(
    f"Factory call count after first use: "
    f"<strong>{build_calls['count']}</strong>"
)
note(f"Resolved now? <strong>{report.__resolved__}</strong>")

# Subsequent uses reuse the cached object; the factory is NOT called again.
heading("Subsequent uses reuse the cached value", level=3)
note(f"Revenue: <strong>${report['revenue']:,.2f}</strong>")
note(f"Units sold: <strong>{report['units_sold']}</strong>")
note(
    f"Factory call count after several uses: "
    f"<strong>{build_calls['count']}</strong> (still 1)"
)

# The proxy is indistinguishable from the underlying dict for most purposes.
note(f"isinstance(report, dict)? <strong>{isinstance(report, dict)}</strong>")
