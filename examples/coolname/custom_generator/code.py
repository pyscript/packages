# Build your own generator with bespoke vocabulary. Useful when you
# want names that match a theme -- here, fanciful tea blends for a
# fictional cafe's daily specials.
#
# Customization guide:
# https://coolname.readthedocs.io/en/latest/customization.html

heading("A themed generator: tea blends of the day")
note(
    "We define three word lists -- moods, flavors, and bases -- and "
    "tell coolname to combine one from each via a 'cartesian' rule. "
    "The result is a small, focused namespace that always sounds on-brand."
)

tea_generator = RandomGenerator({
    "all": {
        "type": "cartesian",
        "lists": ["mood", "flavor", "base"],
    },
    "mood": {
        "type": "words",
        "words": ["tranquil", "spirited", "drowsy", "radiant", "brisk"],
    },
    "flavor": {
        "type": "words",
        "words": ["citrus", "honey", "vanilla", "ginger", "rose", "smoke"],
    },
    "base": {
        "type": "words",
        "words": ["chai", "matcha", "oolong", "rooibos", "earl-grey"],
    },
})

note("This week's daily specials:")
specials = [tea_generator.generate_slug() for _ in range(7)]
display(
    HTML("<ol>" + "".join(f"<li><code>{s}</code></li>" for s in specials) + "</ol>"),
    append=True,
)

# get_combinations_count() works on any RandomGenerator instance,
# so we can advertise just how varied the menu can be.
total_blends = tea_generator.get_combinations_count()
note(
    f"With this vocabulary the cafe can mint "
    f"<strong>{total_blends}</strong> distinct blend names "
    "before having to repeat itself."
)

# Calling generate() (without _slug) returns the token list, which
# you can re-style for menus, posters, or filenames.
tokens = tea_generator.generate()
note(
    f"Raw tokens for one blend: <code>{tokens}</code> &rarr; "
    f"<em>{' '.join(w.title() for w in tokens)}</em>"
)
