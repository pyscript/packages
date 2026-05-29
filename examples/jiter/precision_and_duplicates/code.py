# ---------------------------------------------------------------------
# Numeric precision and strict-mode options.
# ---------------------------------------------------------------------

heading("Decimals and duplicate-key detection")
note(
    "When JSON carries money or scientific values, the default "
    "<code>float</code> conversion can lose precision. jiter lets "
    "you opt into <code>Decimal</code> output. Separately, "
    "<code>catch_duplicate_keys</code> turns a silent overwrite "
    "into a loud error."
)

# A ledger entry whose amount has more digits than a 64-bit float
# can faithfully store.
ledger_entry = b'{"account": "ACME-001", "amount": 1234567890.1234567890}'

heading("Default: amount comes back as a float", level=3)
default_parse = jiter.from_json(ledger_entry)
display(default_parse, append=True)
note(
    f"Type: <code>{type(default_parse['amount']).__name__}</code>. "
    f"Notice the trailing digits have been rounded."
)

heading('float_mode="decimal": exact decimal arithmetic', level=3)
decimal_parse = jiter.from_json(ledger_entry, float_mode="decimal")
display(decimal_parse, append=True)
note(
    f"Type: <code>{type(decimal_parse['amount']).__name__}</code>. "
    f"Now we can sum many of these without drift."
)

# Add up 1000 copies to show Decimal stays exact.
total = sum(
    jiter.from_json(ledger_entry, float_mode="decimal")["amount"]
    for _ in range(1000)
)
note(f"Sum of 1000 entries (Decimal): <code>{total}</code>")

heading("Catching duplicate keys", level=3)
note(
    "By default, JSON parsers silently let later keys win. That can "
    "hide bugs in upstream data. Pass <code>catch_duplicate_keys=True</code> "
    "to fail fast instead."
)

suspect_payload = b'{"user_id": 1, "user_id": 2, "name": "Robin"}'

permissive = jiter.from_json(suspect_payload)
note(f"Permissive parse (last value wins): <code>{permissive}</code>")

try:
    jiter.from_json(suspect_payload, catch_duplicate_keys=True)
except ValueError as exc:
    note(f"Strict parse raised <code>ValueError</code>: {exc}")
