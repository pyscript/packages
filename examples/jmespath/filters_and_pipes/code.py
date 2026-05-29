# Filter expressions narrow a projection to items matching a predicate,
# and pipes (|) let you chain expressions left-to-right.

# A small catalog of secondhand books at a fictional shop.
catalog = {
    "books": [
        {"title": "Tide Tables",        "genre": "reference", "price": 4.50, "stock": 2},
        {"title": "The Lantern Keeper", "genre": "fiction",   "price": 8.25, "stock": 5},
        {"title": "Foraging the Fens",  "genre": "nature",    "price": 12.0, "stock": 1},
        {"title": "Quiet Astronomy",    "genre": "science",   "price": 15.5, "stock": 3},
        {"title": "Marsh Birds",        "genre": "nature",    "price": 9.75, "stock": 0},
        {"title": "Letters Home",       "genre": "fiction",   "price": 6.00, "stock": 4},
    ],
}

heading("Filtering with [?...]")
note(
    "A filter expression keeps only the elements that satisfy a "
    "predicate. Backticks denote literal JSON values."
)

# Books still in stock and under £10.
affordable = jmespath.search(
    "books[?stock > `0` && price < `10`].title",
    catalog,
)
note(f"In stock and under £10: <strong>{affordable}</strong>")

# Just the nature books.
nature_titles = jmespath.search(
    "books[?genre == 'nature'].title",
    catalog,
)
note(f"Nature titles: <strong>{nature_titles}</strong>")

heading("Pipes and built-in functions")
note(
    "JMESPath ships with built-ins like <code>length</code>, "
    "<code>sort_by</code>, <code>max_by</code>, and <code>sum</code>. "
    "The <code>|</code> operator pipes the left-hand result into the "
    "right-hand expression."
)

# How many distinct titles are in the catalog?
title_count = jmespath.search("length(books)", catalog)
note(f"Total titles: <strong>{title_count}</strong>")

# The priciest book overall.
priciest = jmespath.search("max_by(books, &price).title", catalog)
note(f"Priciest title: <strong>{priciest}</strong>")

# Sort fiction by price ascending, then take just the titles.
cheap_fiction = jmespath.search(
    "books[?genre == 'fiction'] | sort_by(@, &price)[*].title",
    catalog,
)
note(f"Fiction, cheapest first: <strong>{cheap_fiction}</strong>")
