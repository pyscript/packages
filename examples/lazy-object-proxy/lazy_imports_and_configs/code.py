# ---------------------------------------------------------------------
# Two practical patterns: lazy imports and a lazy settings registry.
# ---------------------------------------------------------------------

import lazy_object_proxy


heading("Pattern 1: lazy imports")
note(
    "Wrap a module import in a Proxy so the cost of importing is "
    "paid only when the module is first touched. Useful for heavy "
    "optional dependencies."
)


def _import_json():
    """Factory that imports and returns the json module."""
    import json
    return json


# `json_lazy` looks and behaves like the json module, but isn't loaded yet.
json_lazy = lazy_object_proxy.Proxy(_import_json)

note(f"Resolved before use? <strong>{json_lazy.__resolved__}</strong>")

payload = {"city": "Lisbon", "temp_c": 21, "skies": "clear"}
encoded = json_lazy.dumps(payload)  # triggers the import
note(f"Encoded payload: <code>{encoded}</code>")
note(f"Resolved after use?  <strong>{json_lazy.__resolved__}</strong>")


heading("Pattern 2: a registry of lazily-built settings")
note(
    "Each entry is a Proxy wrapping a builder. Iterating the "
    "registry's keys is cheap; only the entries you read get built."
)

build_log = []


def make_builder(name, value):
    """Return a zero-arg factory that 'builds' a settings record."""
    def _build():
        build_log.append(name)
        return {"name": name, "value": value, "ready": True}
    return _build


settings = {
    "database": lazy_object_proxy.Proxy(
        make_builder("database", "postgres://example/db")
    ),
    "cache": lazy_object_proxy.Proxy(
        make_builder("cache", "redis://example/0")
    ),
    "search": lazy_object_proxy.Proxy(
        make_builder("search", "https://search.example/api")
    ),
}

note(f"Registry keys (no builders run yet): {list(settings)}")
note(f"Builders run so far: <strong>{build_log}</strong>")

# Touch only the 'cache' entry. The other two stay un-built.
cache_value = settings["cache"]["value"]
note(f"cache value: <code>{cache_value}</code>")
note(f"Builders run after reading 'cache': <strong>{build_log}</strong>")

# Reading 'cache' again does not rebuild; the proxy caches its result.
_ = settings["cache"]["ready"]
note(f"Builders run after re-reading 'cache': <strong>{build_log}</strong>")

# Now touch 'database'; 'search' remains untouched.
note(f"database url: <code>{settings['database']['value']}</code>")
note(f"Final build log: <strong>{build_log}</strong>")

resolved = {k: v.__resolved__ for k, v in settings.items()}
note(f"Per-entry resolved status: <strong>{resolved}</strong>")
