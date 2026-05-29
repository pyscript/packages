# ---------------------------------------------------------------------
# PRecord: like a PMap, but with declared fields, types, and invariants.
# Great for modeling domain entities you want to keep honest.
# ---------------------------------------------------------------------

heading("1. Declaring a record with typed fields")
note(
    "A Book has a title, a positive page count, and a list of tags. "
    "Field declarations enforce types and simple invariants."
)


class Book(PRecord):
    title = field(type=str, mandatory=True)
    pages = field(
        type=int,
        invariant=lambda n: (n > 0, "pages must be positive"),
    )
    tags = pvector_field(str)


hobbit = Book(title="The Hobbit", pages=310, tags=v("fantasy", "classic"))
note(f"Created: {hobbit}")
note(f"Field access: hobbit.title = {hobbit.title!r}, "
     f"pages = {hobbit.pages}")

# "Mutation" returns a new record; the original is untouched.
revised = hobbit.set(pages=320)
note(f"Revised:  {revised}")
note(f"Original still has {hobbit.pages} pages.")

heading("2. Type and invariant enforcement")
note("Bad data is rejected at construction or update time.")

try:
    Book(title="Bad", pages=-5)
except InvariantException as exc:
    note(f"InvariantException: {exc.invariant_errors}")

try:
    hobbit.set(pages="three hundred")
except PTypeError as exc:
    note(f"PTypeError: {exc}")

heading("3. Nested records and the create() factory")
note(
    "PRecord.create() builds a record (and any nested records) from "
    "plain Python data -- handy for parsing JSON-like input."
)


class Library(PRecord):
    name = field(type=str)
    books_by_id = pmap_field(str, Book)


raw_data = {
    "name": "Riverside Branch",
    "books_by_id": {
        "B001": {"title": "The Hobbit", "pages": 310,
                 "tags": ["fantasy", "classic"]},
        "B002": {"title": "Dune", "pages": 688,
                 "tags": ["sci-fi"]},
    },
}

library = Library.create(raw_data)
note(f"Library name: {library.name}")
note(f"Book B002: {library.books_by_id['B002']}")

# Records serialize cleanly back to plain Python dicts.
note(f"Round-trip via thaw(): {thaw(library.books_by_id['B001'])}")
