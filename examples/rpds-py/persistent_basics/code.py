"""
A first look at rpds-py: Python bindings to Rust's persistent data
structures.

Persistent data structures are immutable: every "modification" returns
a brand-new structure that shares as much memory as possible with the
original. This makes them safe to share across functions, threads, or
"timelines" in your program without defensive copying.

See: https://rpds.readthedocs.io/
"""
from IPython.core.display import display, HTML

from rpds import HashTrieMap, HashTrieSet, List


heading("HashTrieMap: an immutable dictionary")
note(
    "We track the inventory of a small bookshop. Inserting or removing "
    "a title returns a new map; the original is untouched."
)

inventory = HashTrieMap({
    "The Left Hand of Darkness": 3,
    "A Wizard of Earthsea": 5,
    "Dune": 2,
})

after_restock = inventory.insert("Hyperion", 4)
after_sale = inventory.remove("Dune")

display(HTML(
    f"<pre>original:    {dict(inventory)}\n"
    f"after_restock: {dict(after_restock)}\n"
    f"after_sale:    {dict(after_sale)}</pre>"
), append=True)
note(
    "Notice that <code>inventory</code> still has Dune and no Hyperion. "
    "Each operation produced a new map without mutating the old one."
)

heading("HashTrieSet: an immutable set")
note(
    "Tags on a blog post. <code>insert</code> and <code>remove</code> "
    "return fresh sets."
)

tags = HashTrieSet({"python", "rust", "data-structures"})
with_extra = tags.insert("immutability")
without_rust = tags.remove("rust")

display(HTML(
    f"<pre>tags:         {set(tags)}\n"
    f"with_extra:   {set(with_extra)}\n"
    f"without_rust: {set(without_rust)}</pre>"
), append=True)

heading("List: an immutable singly-linked list")
note(
    "rpds <code>List</code> is a cons-style list. "
    "<code>push_front</code> prepends; <code>.first</code> and "
    "<code>.rest</code> peel off the head."
)

primes = List([2, 3, 5, 7, 11])
extended = primes.push_front(1)

note(f"primes.first = {primes.first}, primes.rest = {list(primes.rest)}")
note(f"extended = {list(extended)}")
note(f"primes is unchanged: {list(primes)}")
