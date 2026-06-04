"""
A first look at frozenlist.

`FrozenList` behaves like a regular list, but once you call
`freeze()` on it, any further mutation raises `RuntimeError`.
This is handy when you want to assemble a collection during
setup and then guarantee it won't be modified afterwards.

Docs: https://frozenlist.aio-libs.org
"""
from IPython.core.display import display, HTML

# Package import for this example.
from frozenlist import FrozenList


# Build a playlist mutably, the same way you'd build a regular list.
playlist = FrozenList()
playlist.append("Take Five")
playlist.append("So What")
playlist.append("Blue in Green")
playlist.extend(["All Blues", "Freddie Freeloader"])

heading("Building the playlist")
note(
    "Before freezing, the FrozenList accepts all the usual "
    "MutableSequence operations: append, extend, insert, "
    "__setitem__, and so on."
)
note(f"Tracks so far: {list(playlist)}")
note(f"Frozen? <strong>{playlist.frozen}</strong>")

# Lock it down. There is no thaw -- this is a one-way trip.
playlist.freeze()

heading("After freeze()")
note(f"Frozen? <strong>{playlist.frozen}</strong>")

# Read access still works perfectly.
note(f"First track: <em>{playlist[0]}</em>")
note(f"Number of tracks: {len(playlist)}")
note(f"Contains 'So What'? {'So What' in playlist}")

# Any attempt to mutate now raises RuntimeError.
heading("Mutation is now an error")
try:
    playlist.append("Milestones")
except RuntimeError as exc:
    note(f"playlist.append(...) raised: <code>{exc}</code>")

try:
    playlist[0] = "Kind of Blue"
except RuntimeError as exc:
    note(f"playlist[0] = ... raised: <code>{exc}</code>")
