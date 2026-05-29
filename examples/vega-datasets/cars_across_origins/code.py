# ---------------------------------------------------------------------
# Comparing fuel economy across regions using the bundled cars dataset.
# ---------------------------------------------------------------------

heading("Cars: a tidy dataset ready to plot")
note(
    "The <code>cars</code> dataset is bundled locally and contains "
    "specs for 400+ cars from the 1970s and 1980s, with their region "
    "of origin. It's a perfect playground for groupby and plotting."
)

cars = data.cars()
note(f"Loaded {len(cars)} rows. Columns:")
display(HTML("<code>" + ", ".join(cars.columns) + "</code>"),
        append=True)
display(cars.head(), append=True)

heading("Average fuel economy by origin, over time")
# Year is a datetime column; pull out the year as an integer.
cars = cars.dropna(subset=["Miles_per_Gallon", "Year"]).copy()
cars["year"] = pd.to_datetime(cars["Year"]).dt.year

mpg_by_year = (
    cars.groupby(["year", "Origin"])["Miles_per_Gallon"]
    .mean()
    .unstack("Origin")
    .round(2)
)
display(mpg_by_year, append=True)

fig, ax = plt.subplots(figsize=(9, 4))
mpg_by_year.plot(ax=ax, marker="o")
ax.set_title("Average miles per gallon by region of origin")
ax.set_ylabel("Miles per gallon")
ax.set_xlabel("Model year")
ax.legend(title="Origin")
fig.tight_layout()
display(fig, append=True)

heading("Horsepower vs. weight, colored by origin")
note(
    "A scatter plot brings out the trade-off between weight and "
    "horsepower, with clear clusters by region."
)

fig, ax = plt.subplots(figsize=(8, 5))
colors = {"USA": "crimson", "Europe": "steelblue", "Japan": "darkorange"}
for origin, group in cars.groupby("Origin"):
    ax.scatter(
        group["Weight_in_lbs"], group["Horsepower"],
        s=18, alpha=0.7, color=colors.get(origin, "gray"),
        label=origin,
    )
ax.set_xlabel("Weight (lbs)")
ax.set_ylabel("Horsepower")
ax.set_title("Horsepower vs. weight by origin")
ax.legend(title="Origin")
fig.tight_layout()
display(fig, append=True)
