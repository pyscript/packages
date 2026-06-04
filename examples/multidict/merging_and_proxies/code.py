# ---------------------------------------------------------------------
# extend, update, merge, and read-only proxies.
# ---------------------------------------------------------------------
from multidict import MultiDict, MultiDictProxy


heading("Building a query string piece by piece")
note(
    "Three methods grow a multidict in different ways: "
    "<code>extend</code> appends, <code>update</code> replaces by key, "
    "and <code>merge</code> only adds keys that aren't already present."
)

# Start with a base set of search filters.
filters = MultiDict([("category", "books"), ("tag", "python")])

# extend() appends every pair, even if the key already exists.
filters.extend([("tag", "async"), ("tag", "web")])
note("After <code>extend</code> with two more tags:")
display(list(filters.items()), append=True)

# update() removes any prior values for each given key, then adds the new ones.
filters.update([("category", "tutorials"), ("category", "guides")])
note(
    "After <code>update</code> with two new categories, the original "
    "'books' is gone and both new categories are present:"
)
display(list(filters.items()), append=True)

# merge() only fills in keys that don't yet exist; existing keys are untouched.
filters.merge([("tag", "ignored"), ("sort", "recent"), ("page", "1")])
note(
    "After <code>merge</code>: 'tag' was untouched (already present), "
    "but 'sort' and 'page' were added:"
)
display(list(filters.items()), append=True)

# ---------------------------------------------------------------------
# MultiDictProxy: a read-only live view onto a multidict.
# ---------------------------------------------------------------------

heading("Read-only views with MultiDictProxy")
note(
    "Wrap a multidict in a <code>MultiDictProxy</code> to share it "
    "without letting callers mutate it. The proxy is a live view: "
    "changes to the underlying multidict show up immediately."
)

view = MultiDictProxy(filters)
note(f"Proxy sees <strong>{len(view)}</strong> pairs.")
note(f"All tags via the proxy: <code>{view.getall('tag')}</code>")

# Mutating through the proxy is not allowed.
try:
    view["tag"] = "nope"
except TypeError as exc:
    note(f"Assigning through the proxy raises <code>TypeError: {exc}</code>")

# But mutating the underlying multidict is reflected in the proxy.
filters.add("tag", "advanced")
note(
    "After adding a tag to the underlying multidict, the proxy "
    f"sees the new value: <code>{view.getall('tag')}</code>"
)

# Build a final query-string-like representation.
heading("Rendering as a query string")
rendered = "&".join(f"{k}={v}" for k, v in filters.items())
display(HTML(f"<pre>?{rendered}</pre>"), append=True)
