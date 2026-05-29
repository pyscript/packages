# ---------------------------------------------------------------------
# Partial JSON: parsing a stream that hasn't finished arriving.
# ---------------------------------------------------------------------

heading("Parsing partial JSON as it streams in")
note(
    "When you're reading JSON from a network response (think: an LLM "
    "token stream), you often want to render what you have so far. "
    "jiter's <code>partial_mode</code> handles a truncated payload "
    "without raising."
)

# Imagine these are progressively longer prefixes of a single response
# arriving over the wire, one chunk at a time.
full_response = (
    b'{"model": "demo-1", "choices": ['
    b'{"role": "assistant", "content": "Hello, traveller! Welcome to jiter."}'
    b']}'
)
checkpoints = [full_response[:n] for n in (20, 55, 95, len(full_response))]

heading("Default: incomplete input is an error", level=3)
try:
    jiter.from_json(checkpoints[1])
except ValueError as exc:
    note(f"Got <code>ValueError</code>: {exc}")

heading("partial_mode=True: drop the trailing incomplete value", level=3)
note(
    "Useful when you want a clean, fully-formed object so far. The "
    "still-arriving last field is silently omitted."
)
for i, chunk in enumerate(checkpoints, start=1):
    parsed = jiter.from_json(chunk, partial_mode=True)
    display(HTML(f"<strong>After chunk {i} ({len(chunk)} bytes):</strong>"), append=True)
    display(parsed, append=True)

heading('partial_mode="trailing-strings": keep the in-flight string', level=3)
note(
    "Perfect for showing a token-by-token assistant reply: the "
    "partially-received string is included as-is."
)
for i, chunk in enumerate(checkpoints, start=1):
    parsed = jiter.from_json(chunk, partial_mode="trailing-strings")
    display(HTML(f"<strong>After chunk {i}:</strong>"), append=True)
    display(parsed, append=True)
