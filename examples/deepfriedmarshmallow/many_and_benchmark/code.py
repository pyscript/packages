# Bulk dumping with `many=True`, and a side-by-side timing comparison
# between a plain Marshmallow schema and a JIT-backed one.

heading("Serializing a list of records with many=True")
note(
    "Both vanilla Marshmallow and Deep-Fried Marshmallow support "
    "`many=True` to dump a sequence in one call. We'll build a small "
    "catalog of books and serialize them all at once."
)


class BookPlain(Schema):
    title = fields.Str()
    author = fields.Str()
    published = fields.Date()
    pages = fields.Int()


class BookJit(JitSchema):
    title = fields.Str()
    author = fields.Str()
    published = fields.Date()
    pages = fields.Int()


catalog = [
    {
        "title": f"Volume {i:03d}",
        "author": ["Ada", "Grace", "Linus", "Guido"][i % 4],
        "published": date(2000, 1, 1) + timedelta(days=i * 17),
        "pages": 120 + (i * 7) % 400,
    }
    for i in range(2000)
]

jit_schema = BookJit()
plain_schema = BookPlain()

# Show a few rows of the JIT output.
preview = jit_schema.dump(catalog[:3], many=True)
display(preview, append=True)

heading("Timing dump() on 2,000 records")
note(
    "Reuse the same schema instance across calls so the JIT's cached "
    "code can do its job. The first JIT call also pays a small "
    "warm-up cost while the optimized serializer is generated."
)

# Warm up the JIT so the timed run reflects steady-state performance.
jit_schema.dump(catalog, many=True)

t0 = perf_counter()
plain_schema.dump(catalog, many=True)
plain_seconds = perf_counter() - t0

t0 = perf_counter()
jit_schema.dump(catalog, many=True)
jit_seconds = perf_counter() - t0

speedup = plain_seconds / jit_seconds if jit_seconds else float("inf")

note(
    f"Plain Marshmallow: <strong>{plain_seconds * 1000:.1f} ms</strong><br>"
    f"Deep-Fried Marshmallow: <strong>{jit_seconds * 1000:.1f} ms</strong><br>"
    f"Speedup: <strong>{speedup:.2f}x</strong>"
)
