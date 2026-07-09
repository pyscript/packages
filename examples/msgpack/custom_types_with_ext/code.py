# ---------------------------------------------------------------------
# Teaching msgpack about types it doesn't know natively.
# ---------------------------------------------------------------------
import msgpack
from decimal import Decimal
from fractions import Fraction


heading("Custom types: Decimal and Fraction via ExtType")
note(
    "MessagePack natively handles ints, floats, strings, bytes, lists, "
    "and maps. For other types we register two callbacks: <code>default</code> "
    "translates unknown objects to ExtType on the way out, and "
    "<code>ext_hook</code> rebuilds them on the way back in. Each ExtType "
    "carries a small integer code so we can tell types apart."
)

# Pick stable codes for our two custom types. Codes 0..127 are free
# for application use.
CODE_DECIMAL = 1
CODE_FRACTION = 2


def encode_custom(obj):
    """Serialize unknown objects into ExtType bytes."""
    if isinstance(obj, Decimal):
        return msgpack.ExtType(CODE_DECIMAL, str(obj).encode("utf-8"))
    if isinstance(obj, Fraction):
        payload = f"{obj.numerator}/{obj.denominator}".encode("utf-8")
        return msgpack.ExtType(CODE_FRACTION, payload)
    raise TypeError(f"Cannot serialize {type(obj).__name__}")


def decode_custom(code, data):
    """Rebuild objects from their ExtType representation."""
    if code == CODE_DECIMAL:
        return Decimal(data.decode("utf-8"))
    if code == CODE_FRACTION:
        numerator, denominator = data.decode("utf-8").split("/")
        return Fraction(int(numerator), int(denominator))
    # Unknown codes: hand the raw ExtType back so callers can inspect it.
    return msgpack.ExtType(code, data)


# An invoice mixing native types with our custom numeric types.
invoice = {
    "invoice_no": "INV-2026-0042",
    "subtotal": Decimal("199.95"),
    "tax_rate": Fraction(1, 5),    # exactly 20%, no float drift
    "total": Decimal("239.94"),
    "paid": False,
}

packed = msgpack.packb(invoice, default=encode_custom)
note(f"Packed size: <strong>{len(packed)} bytes</strong>.")

restored = msgpack.unpackb(packed, ext_hook=decode_custom, raw=False)

note("Restored invoice (note that types are preserved exactly):")
display(restored, append=True)

types_seen = {key: type(value).__name__ for key, value in restored.items()}
note("Types after round-trip:")
display(types_seen, append=True)

heading("Sanity check")
note(
    "Decimal and Fraction came back as themselves, not as floats or "
    "strings, so arithmetic still works as intended."
)
tax_as_decimal = Decimal(restored['tax_rate'].numerator) / Decimal(restored['tax_rate'].denominator)
display(HTML(
    f"<pre>subtotal * tax_rate = "
    f"{restored['subtotal'] * tax_as_decimal}</pre>"
), append=True)
