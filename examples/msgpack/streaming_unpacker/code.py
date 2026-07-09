# ---------------------------------------------------------------------
# Streaming: many small messages concatenated into one byte stream.
# ---------------------------------------------------------------------
import msgpack
from io import BytesIO


heading("Streaming unpack: a log of trades")
note(
    "Real systems often append many MessagePack messages back-to-back "
    "into a file or socket. msgpack.Unpacker reads them one at a time, "
    "either from a file-like object or via its feed() method."
)

# A small ledger of trades. We pack each row independently and write
# the bytes into one buffer, the way a log file would grow over time.
trades = [
    {"id": 1001, "symbol": "ACME", "qty": 50, "price": 12.40},
    {"id": 1002, "symbol": "GLOBO", "qty": 10, "price": 88.10},
    {"id": 1003, "symbol": "ACME", "qty": 25, "price": 12.55},
    {"id": 1004, "symbol": "INITECH", "qty": 5, "price": 305.00},
    {"id": 1005, "symbol": "GLOBO", "qty": 40, "price": 87.95},
]

buffer = BytesIO()
for trade in trades:
    buffer.write(msgpack.packb(trade))

note(f"Total stream size: <strong>{buffer.tell()} bytes</strong> "
     f"for {len(trades)} messages.")

# Iterate the Unpacker like a generator: each iteration yields the
# next fully-decoded message from the stream.
buffer.seek(0)
unpacker = msgpack.Unpacker(buffer, raw=False)

decoded = []
for trade in unpacker:
    decoded.append(trade)

note("Decoded trades, one message at a time:")
display(decoded, append=True)

heading("Feeding bytes incrementally")
note(
    "When bytes arrive in chunks (a network socket, a slow file), "
    "feed() lets you push partial data and pull whole messages out "
    "as they become available."
)

# Simulate a chunked arrival by splitting the buffer at an arbitrary
# midpoint that probably falls inside a message.
all_bytes = buffer.getvalue()
split = len(all_bytes) // 2
chunks = [all_bytes[:split], all_bytes[split:]]

incremental = msgpack.Unpacker(raw=False)
results = []
for i, chunk in enumerate(chunks, start=1):
    incremental.feed(chunk)
    # Drain any complete messages that the new chunk made available.
    for msg in incremental:
        results.append((f"after chunk {i}", msg["id"], msg["symbol"]))

note("Messages surfaced as each chunk was fed in:")
display(results, append=True)
