# ---------------------------------------------------------------------
# transform() lets you update deeply nested immutable structures with
# a path + a transformation. Paths can include literal keys/indices,
# the `ny` matcher (any element), and callable predicates.
# ---------------------------------------------------------------------
from pyrsistent import freeze, thaw, ny, discard, inc

heading("1. A nested newspaper")
note(
    "We freeze a plain Python dict into nested PMaps and PVectors so "
    "we can demonstrate path-based updates."
)

newspaper = freeze({
    "edition": "2026-03-15",
    "articles": [
        {"author": "Sara",  "views": 120, "content": "A short article"},
        {"author": "Steve", "views": 45,
         "content": "A slightly longer article about the weather"},
        {"author": "Joan",  "views": 300,
         "content": "Front page scoop with all the details"},
    ],
    "weather": {"temperature": "11C", "wind": "5m/s"},
})

note(f"Original first article: {newspaper['articles'][0]}")

heading("2. Update by path with ny and a transform function")
note(
    "ny matches every element in a collection. inc is a built-in "
    "transform that adds 1. Custom transforms are just functions "
    "from old value to new value."
)

# Bump the view count of every article by 1.
bumped = newspaper.transform(["articles", ny, "views"], inc)
note(f"Views after bump: "
     f"{[a['views'] for a in bumped['articles']]}")

# Truncate any content longer than 25 characters.
def truncate(text):
    return text if len(text) <= 25 else text[:22] + "..."

shortened = newspaper.transform(
    ["articles", ny, "content"], truncate,
)
for article in shortened["articles"]:
    note(f"- {article['author']}: {article['content']!r}")

heading("3. Callable predicates and the discard sentinel")
note(
    "A callable in a path is a key matcher: pyrsistent passes it "
    "each <em>key</em> of the current structure and keeps those for "
    "which it returns True. For a PVector, the keys are integer "
    "indices -- not the elements -- so a predicate that needs to "
    "inspect element contents must look the element up itself. "
    "The discard sentinel removes the matched element entirely."
)

# Anonymize authors whose names start with 'S'. Because the predicate
# receives an *index* (not the article), we close over `articles` to
# look up the element. This is a real pyrsistent gotcha worth knowing.
articles = newspaper["articles"]
anonymized = newspaper.transform(
    ["articles", lambda i: articles[i]["author"].startswith("S"), "author"],
    "anonymous",
)
for article in anonymized["articles"]:
    note(f"- {article['author']} ({article['views']} views)")

# Drop the weather block and every article's content in one call.
trimmed = newspaper.transform(
    ["weather"], discard,
    ["articles", ny, "content"], discard,
)
note(f"Trimmed structure: {thaw(trimmed)}")

heading("4. Structural sharing")
note(
    "When a sub-structure isn't touched, the new value reuses the "
    "old object identity -- no copy is made. Touched sub-structures "
    "get new objects, but their untouched siblings stay shared."
)

note(f"First article is a new object after bump? "
     f"{bumped['articles'][0] is not newspaper['articles'][0]} "
     f"(views changed, so a new article PMap was created)")
note(f"Weather is shared with bumped? "
     f"{bumped['weather'] is newspaper['weather']} "
     f"(weather wasn't touched, so the same PMap is reused)")