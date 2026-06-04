# ---------------------------------------------------------------------
# Reading just the columns you need, and decoding low-cardinality
# string columns as pandas Categoricals for memory savings.
# ---------------------------------------------------------------------

heading("Selective column reads")
note(
    "Parquet's columnar layout means you can read just the columns "
    "you need without scanning the rest. We'll write a wider dataset "
    "and then load only two of its columns."
)

# A wider table: orders from a fictional online bookshop.
n_orders = 2000
genres = ["Fiction", "Non-fiction", "Poetry", "Science", "History"]
countries = ["UK", "US", "DE", "FR", "JP", "BR"]

orders = pd.DataFrame({
    "order_id": np.arange(n_orders),
    "genre": pd.Categorical(rng.choice(genres, size=n_orders), categories=genres),
    "country": rng.choice(countries, size=n_orders),
    "price": rng.uniform(5, 35, size=n_orders).round(2),
    "quantity": rng.integers(1, 6, size=n_orders),
    "discount": rng.uniform(0, 0.4, size=n_orders).round(3),
    "shipping": rng.uniform(0, 8, size=n_orders).round(2),
})

write("/tmp/orders.parq", orders, compression="SNAPPY")
parquet_file = ParquetFile("/tmp/orders.parq")

note(f"All columns in the file: <code>{parquet_file.columns}</code>")

# Load only two columns, and treat 'genre' as a categorical.
slim = parquet_file.to_pandas(
    columns=["genre", "price"],
    categories=["genre"],
)

note("Loaded only <code>genre</code> and <code>price</code>:")
display(slim.head(), append=True)
note(
    f"<code>genre</code> dtype is "
    f"<strong>{slim['genre'].dtype}</strong> "
    f"with categories <code>{list(slim['genre'].cat.categories)}</code>."
)

# A quick aggregate and bar chart from the slim frame.
avg_by_genre = slim.groupby("genre", observed=True)["price"].mean().sort_values()

fig, ax = plt.subplots(figsize=(8, 4))
avg_by_genre.plot(kind="barh", ax=ax, color="teal")
ax.set_title("Average book price by genre")
ax.set_xlabel("Average price ($)")
fig.tight_layout()
display(fig, append=True)
