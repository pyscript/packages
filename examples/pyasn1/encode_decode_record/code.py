"""
A first look at pyasn1: defining an ASN.1 SEQUENCE, populating it,
encoding it to DER bytes, and decoding it back into a Python object.

The ASN.1 schema we model here is the classic introductory example:

    Record ::= SEQUENCE {
      id        INTEGER,
      room  [0] INTEGER OPTIONAL,
      house [1] INTEGER DEFAULT 0
    }

Docs: https://pyasn1.readthedocs.io/
"""
from IPython.core.display import display, HTML


# Define the Record schema as a Python class. Each named type maps to a
# field in the SEQUENCE; the context-specific implicit tags ([0], [1])
# are attached via .subtype(implicitTag=...).
class Record(Sequence):
    componentType = NamedTypes(
        NamedType("id", Integer()),
        OptionalNamedType(
            "room",
            Integer().subtype(
                implicitTag=Tag(tagClassContext, tagFormatSimple, 0)
            ),
        ),
        DefaultedNamedType(
            "house",
            Integer(0).subtype(
                implicitTag=Tag(tagClassContext, tagFormatSimple, 1)
            ),
        ),
    )


heading("Building a Record value")
note(
    "We populate the SEQUENCE much like a dict, then ask pyasn1 for "
    "its human-readable form via str()."
)

record = Record()
record["id"] = 123
record["room"] = 321

display(HTML(f"<pre>{str(record)}</pre>"), append=True)

heading("Encoding to DER")
note(
    "DER (Distinguished Encoding Rules) gives us a compact, canonical "
    "byte representation. Notice how the optional 'room' field is "
    "included but the defaulted 'house' field is omitted."
)

substrate = der_encode(record)
display(HTML(f"<pre>DER bytes: {hexdump(substrate)}</pre>"), append=True)
display(HTML(f"<pre>Length:    {len(substrate)} bytes</pre>"), append=True)

heading("Decoding DER back into a Record")
note(
    "Pass the schema (asn1Spec=Record()) so the decoder knows how to "
    "interpret the implicit tags. The defaulted 'house' field comes "
    "back as 0 even though it was not present in the bytes."
)

decoded, leftover = der_decode(substrate, asn1Spec=Record())
for field_name in ("id", "room", "house"):
    note(f"<code>{field_name}</code> = <strong>{int(decoded[field_name])}</strong>")

note(f"Leftover bytes after decoding: <code>{len(leftover)}</code>")
note(f"Round-trip equal? <strong>{record == decoded}</strong>")
