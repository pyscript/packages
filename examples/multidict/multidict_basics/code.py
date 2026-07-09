"""
A first look at multidict.

Most dict-like containers in Python allow only one value per key.
multidict.MultiDict is a dict-like collection where the same key can
appear multiple times, with insertion order preserved. It's the data
structure behind HTTP headers and URL query strings in libraries like
aiohttp and yarl.

Docs: https://multidict.aio-libs.org
"""
from IPython.core.display import display, HTML

from multidict import MultiDict


# Imagine the query string of a search URL:
#   ?tag=python&tag=async&tag=web&sort=recent
# A regular dict would lose two of the three tags. MultiDict keeps them all.
query = MultiDict([
    ("tag", "python"),
    ("tag", "async"),
    ("tag", "web"),
    ("sort", "recent"),
])

heading("A multidict from a list of pairs")
note("Notice that 'tag' appears three times, with insertion order preserved.")
display(list(query.items()), append=True)

# Indexing returns the FIRST value for the key, like a regular dict would.
note(f"query['tag'] returns the first match: <code>{query['tag']!r}</code>")

# To get all values for a key, use getall().
heading("Getting every value for a repeated key")
note("Use <code>getall(key)</code> to retrieve every value:")
display(query.getall("tag"), append=True)

# add() appends another value rather than replacing the existing one.
query.add("tag", "tutorial")
note("After <code>query.add('tag', 'tutorial')</code>:")
display(query.getall("tag"), append=True)

# Assignment with [] replaces all existing values for that key with one entry.
query["tag"] = "overview"
note("After <code>query['tag'] = 'overview'</code> all prior tags are replaced:")
display(list(query.items()), append=True)

# len() counts pairs, not unique keys.
heading("Length and iteration")
note(
    f"<code>len(query)</code> is <strong>{len(query)}</strong> "
    "(total pairs, not unique keys)."
)
note("Iterating over the multidict yields keys, with repeats:")
display(list(query), append=True)
