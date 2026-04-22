"""
Core pandas with matplotlib use cases.

All of this code is running in your browser. See pyscript.net
for how we do this!

Each section builds a small synthetic dataset and displays both
tabular output and a matplotlib figure via PyScript's `display`
function (inspired by and interchangeable with IPython's
`display` capabilities).
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Allows us to show things in the web page.
from IPython.core.display import display, HTML


# Deterministic randomness so reloads show the same data. Feel free to
# change this seed or remove it to get different data on each reload!
rng = np.random.default_rng(42)

# Helper functions to emit HTML headings and notes, for visual separation
# of sections and to provide explanatory text. You can safely ignore
# these.

def heading(text, level=2):
    # Emit a simple HTML heading so sections are visually separated.
    display(HTML(f"<h{level}>{text}</h{level}>"), append=True)


def note(text):
    # Emit a short paragraph of explanatory prose.
    display(HTML(f"<p>{text}</p>"), append=True)


# ---------------------------------------------------------------------
# Section 1: DataFrame basics, describe, groupby, bar chart.
# ---------------------------------------------------------------------

heading("1. DataFrame basics: a bookshop's inventory")
note(
    "A made-up inventory of 200 books across five genres. "
    "We'll look at the first few rows, summary statistics, and "
    "revenue grouped by genre."
)

genres = ["Fiction", "Non-fiction", "Poetry", "Science", "History"]
n_books = 200

books = pd.DataFrame({
    "title": [f"Book {i:03d}" for i in range(n_books)],
    "genre": rng.choice(genres, size=n_books),
    "price": rng.uniform(5, 35, size=n_books).round(2),
    "copies_sold": rng.integers(1, 500, size=n_books),
})
books["revenue"] = (books["price"] * books["copies_sold"]).round(2)

note("First five rows:")
display(books.head(), append=True)

note("Summary statistics for the numeric columns:")
display(books.describe().round(2), append=True)

# Group by genre and aggregate several columns at once.
by_genre = books.groupby("genre").agg(
    titles=("title", "count"),
    avg_price=("price", "mean"),
    total_copies=("copies_sold", "sum"),
    total_revenue=("revenue", "sum"),
).round(2).sort_values("total_revenue", ascending=False)

note("Aggregates per genre, sorted by total revenue:")
display(by_genre, append=True)

# Bar chart of revenue by genre.
fig, ax = plt.subplots(figsize=(8, 4))
by_genre["total_revenue"].plot(kind="bar", ax=ax, color="steelblue")
ax.set_title("Total revenue by genre")
ax.set_ylabel("Revenue ($)")
ax.set_xlabel("Genre")
ax.tick_params(axis="x", rotation=0)
fig.tight_layout()
display(fig, append=True)
