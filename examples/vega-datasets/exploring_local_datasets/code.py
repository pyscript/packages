"""
A first look at vega_datasets.

The package gives you instant, mostly-offline access to the well-known
Vega example datasets, returned as pandas DataFrames. It's a great
source of small, tidy data for prototyping plots and demos.

Docs: https://github.com/altair-viz/vega_datasets
"""
from IPython.core.display import display, HTML

# Package imports for this example.
import pandas as pd
from vega_datasets import data, local_data


heading("The classic iris dataset")
note(
    "Calling an attribute on the <code>data</code> object loads that "
    "dataset as a pandas DataFrame. The iris dataset is bundled with "
    "the package, so it loads instantly and works offline."
)

iris = data.iris()
note(f"iris is a {type(iris).__name__} with shape {iris.shape}.")
display(iris.head(), append=True)

heading("What's this dataset about?")
note(
    "Every dataset attribute carries metadata: a human-readable "
    "description and the canonical URL of the source file."
)
note(f"<strong>Description:</strong> {data.iris.description}")
note(f"<strong>Source URL:</strong> <code>{data.iris.url}</code>")

heading("Quick summary by species")
# A natural pandas follow-up: average measurements per species.
by_species = iris.groupby("species").mean(numeric_only=True).round(2)
display(by_species, append=True)

heading("Datasets bundled for offline use")
note(
    "Most Vega datasets are fetched from the network on demand, but "
    "a curated subset is shipped inside the package itself. Use "
    "<code>local_data</code> to discover and load only those."
)
bundled = local_data.list_datasets()
note(f"There are <strong>{len(bundled)}</strong> local datasets:")
display(HTML("<ul>" + "".join(f"<li><code>{name}</code></li>"
                              for name in bundled) + "</ul>"),
        append=True)
