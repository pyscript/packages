"""
A first taste of Deep-Fried Marshmallow.

Deep-Fried Marshmallow speeds up Marshmallow's serialization with a
runtime JIT. The simplest way to opt in is to inherit from `JitSchema`
instead of `marshmallow.Schema`. Everything else looks and behaves
exactly like normal Marshmallow.

Docs: https://github.com/mLupine/DeepFriedMarshmallow
"""
from IPython.core.display import display, HTML

# Example-specific imports.
from datetime import date
from marshmallow import fields
from deepfriedmarshmallow import JitSchema



# Two related schemas: an artist, and an album that nests one artist.
class ArtistSchema(JitSchema):
    name = fields.Str()
    country = fields.Str()


class AlbumSchema(JitSchema):
    title = fields.Str()
    release_date = fields.Date()
    tracks = fields.Int()
    artist = fields.Nested(ArtistSchema())


heading("Dumping a Python object to a dict")
note(
    "We build a small album record and let the JIT-backed schema "
    "serialize it. The API is identical to plain Marshmallow."
)

album = {
    "title": "Kind of Blue",
    "release_date": date(1959, 8, 17),
    "tracks": 5,
    "artist": {"name": "Miles Davis", "country": "USA"},
}

# IMPORTANT: reuse the schema instance. The JIT generates code on first
# use and caches it on the instance, so creating one per call defeats
# the optimization.
album_schema = AlbumSchema()

dumped = album_schema.dump(album)
note("Serialized output:")
display(dumped, append=True)

heading("Loading a dict back into validated Python data")
incoming = {
    "title": "Blue Train",
    "release_date": "1958-01-15",
    "tracks": 5,
    "artist": {"name": "John Coltrane", "country": "USA"},
}
loaded = album_schema.load(incoming)
note("Deserialized (note the parsed `release_date`):")
display(loaded, append=True)
