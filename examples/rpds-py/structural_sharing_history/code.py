# ---------------------------------------------------------------------
# Undo history with persistent maps: every edit becomes a snapshot.
# ---------------------------------------------------------------------
from rpds import HashTrieMap, HashTrieSet, List


heading("Document edits as a timeline of HashTrieMaps")
note(
    "Imagine a tiny key/value document being edited. Each edit "
    "returns a new map, and we keep every previous version in a "
    "<code>List</code> as our undo history. Because the maps share "
    "structure internally, this is cheap, even if the document is large."
)

# Start with an empty document and an empty history.
document = HashTrieMap()
history = List([document])

# Apply a sequence of edits, recording each new version.
edits = [
    ("title", "Persistent Data Structures"),
    ("author", "A. Reader"),
    ("draft", True),
    ("title", "Persistent Data Structures in Python"),  # a revision
    ("draft", False),
]

for key, value in edits:
    document = document.insert(key, value)
    history = history.push_front(document)

note(f"Number of snapshots in history: {len(list(history))}")
note("Latest version of the document:")
display(HTML(f"<pre>{dict(document)}</pre>"), append=True)

heading("Walking back through time")
note(
    "<code>history</code> stores newest-first. Peel off snapshots with "
    "<code>.first</code> and <code>.rest</code> to inspect each step."
)

cursor = history
step = 0
while len(list(cursor)) > 0:
    snapshot = cursor.first
    display(HTML(
        f"<pre>step -{step}: {dict(snapshot)}</pre>"
    ), append=True)
    cursor = cursor.rest
    step += 1

heading("Diffing two snapshots with HashTrieSet")
note(
    "We can compare any two snapshots by turning their keys into "
    "persistent sets and asking which keys appeared or disappeared."
)

# history is newest-first: index 0 is final, index -1 is empty start.
versions = list(history)
final_keys = HashTrieSet(versions[0])
initial_keys = HashTrieSet(versions[-1])

added = set(final_keys) - set(initial_keys)
removed = set(initial_keys) - set(final_keys)

note(f"Keys added across the whole edit session: {added}")
note(f"Keys removed across the whole edit session: {removed or '(none)'}")
note(
    "The original empty <code>document</code> and every intermediate "
    "version are still valid values you can return to at any time."
)
