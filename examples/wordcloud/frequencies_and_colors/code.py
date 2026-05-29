# ---------------------------------------------------------------------
# Build a cloud from a frequency dict and theme it with a custom palette.
# ---------------------------------------------------------------------

heading("Word cloud from raw frequencies")
note(
    "Sometimes you already have counts (think: survey tags, log "
    "categories, song genres). Use generate_from_frequencies to skip "
    "tokenization and feed the layout directly."
)

# Imagine a small music festival asked attendees to tag their favorite
# set with a single word. Here are the tag counts.
festival_tags = {
    "indie": 142,
    "jazz": 88,
    "electronic": 165,
    "folk": 54,
    "rock": 121,
    "ambient": 37,
    "hiphop": 99,
    "soul": 46,
    "punk": 28,
    "synthwave": 71,
    "blues": 33,
    "metal": 19,
}

# A color function receives metadata about each word and returns a CSS
# color string. Here we map word frequency to a warm-to-cool palette.
def warm_cool_color(word, font_size, position, orientation,
                    random_state=None, **kwargs):
    # font_size correlates with frequency; bigger -> warmer.
    if font_size > 60:
        return "hsl(15, 80%, 50%)"   # warm red-orange
    if font_size > 35:
        return "hsl(40, 75%, 50%)"   # amber
    if font_size > 20:
        return "hsl(170, 55%, 40%)"  # teal
    return "hsl(220, 50%, 45%)"      # cool blue


cloud = WordCloud(
    width=700,
    height=350,
    background_color="white",
    prefer_horizontal=0.9,
    color_func=warm_cool_color,
    random_state=7,
).generate_from_frequencies(festival_tags)

fig, ax = plt.subplots(figsize=(9, 4.5))
ax.imshow(cloud, interpolation="bilinear")
ax.axis("off")
ax.set_title("Festival set tags, sized by attendee votes")
fig.tight_layout()
display(fig, append=True)

note(
    "Tip: any callable matching the color_func signature works, so you "
    "can drive colors from external metadata, not just font size."
)
