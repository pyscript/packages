"""
A first look at the `wordcloud` package: turn a chunk of prose into
a colorful image where the most frequent words appear largest.

Docs: https://amueller.github.io/word_cloud/
"""
from IPython.core.display import display, HTML

# Package imports for this example.
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS


# A short, made-up review of an imaginary coffee shop. The repetition of
# certain words ("coffee", "pastries", "cozy") will make them stand out
# in the cloud.
review = """
The little corner coffee shop is cozy and bright. The coffee is rich,
the pastries are flaky, and the staff are warm and welcoming. I love
the coffee, I love the pastries, and I especially love the cozy nook
by the window. Cozy mornings, good coffee, fresh pastries, friendly
faces. The coffee shop has become my favorite spot to read and write.
Highly recommend the coffee, the pastries, and the atmosphere.
"""

heading("A word cloud from a coffee shop review")
note(
    "The WordCloud class tokenizes text, removes common stopwords, "
    "and lays out the remaining words sized by frequency."
)

# `STOPWORDS` is a built-in set of common English words to skip
# (the, and, is, ...). You can extend it with your own words.
custom_stopwords = set(STOPWORDS) | {"shop"}

cloud = WordCloud(
    width=600,
    height=300,
    background_color="white",
    stopwords=custom_stopwords,
    random_state=42,
).generate(review)

# WordCloud renders to a PIL image; matplotlib is the easiest way to
# show it in a notebook-style flow.
fig, ax = plt.subplots(figsize=(8, 4))
ax.imshow(cloud, interpolation="bilinear")
ax.axis("off")
fig.tight_layout()
display(fig, append=True)

note(
    "The top words and their relative weights, straight from the layout:"
)
top_words = sorted(
    cloud.words_.items(), key=lambda kv: kv[1], reverse=True
)[:8]
rows = "".join(
    f"<tr><td>{w}</td><td>{weight:.2f}</td></tr>"
    for w, weight in top_words
)
display(
    HTML(
        "<table><tr><th>word</th><th>relative weight</th></tr>"
        + rows
        + "</table>"
    ),
    append=True,
)
