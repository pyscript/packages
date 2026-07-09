# ---------------------------------------------------------------------
# DefaultMunch and DefaultFactoryMunch: graceful handling of missing keys.
# ---------------------------------------------------------------------
from munch import Munch, DefaultMunch, DefaultFactoryMunch


heading("DefaultMunch: a sentinel for missing attributes")
note(
    "A regular Munch raises AttributeError for unknown keys. "
    "DefaultMunch instead returns a value of your choosing, which is "
    "perfect for optional configuration fields."
)

# A common pattern: use a sentinel object so you can tell "missing" apart
# from a legitimate None value.
MISSING = object()

config = DefaultMunch.fromDict(
    {
        "host": "localhost",
        "port": 5432,
        "database": {"name": "shop", "user": "ada"},
    },
    MISSING,
)

note(f"config.host &rarr; <strong>{config.host}</strong>")
note(f"config.database.user &rarr; <strong>{config.database.user}</strong>")
note(f"config.database.password is MISSING &rarr; {config.database.password is MISSING}")
note(f"config.tls_cert is MISSING &rarr; {config.tls_cert is MISSING}")

heading("DefaultFactoryMunch: build values on demand")
note(
    "When you'd rather create a fresh value for each missing key (think "
    "collections.defaultdict), reach for DefaultFactoryMunch. Below we "
    "tally word frequencies in a tiny corpus."
)

word_counts = DefaultFactoryMunch(int)
poem = (
    "the sea the sky the gull "
    "the wind the wave the gull"
)
for word in poem.split():
    word_counts[word] += 1

# Attribute-style access works on accumulated keys.
note(f"word_counts.the &rarr; <strong>{word_counts.the}</strong>")
note(f"word_counts.gull &rarr; <strong>{word_counts.gull}</strong>")
note(f"Unseen word starts at zero: word_counts.dolphin = {word_counts.dolphin}")

display(dict(word_counts), append=True)

# A factory can be any zero-argument callable. Here, lists for grouping.
inbox = DefaultFactoryMunch(list)
messages = [
    ("ada", "lunch?"),
    ("grace", "shipped the build"),
    ("ada", "see you at 1"),
    ("linus", "patch attached"),
]
for sender, body in messages:
    inbox[sender].append(body)

note("Messages grouped by sender:")
display(dict(inbox), append=True)
