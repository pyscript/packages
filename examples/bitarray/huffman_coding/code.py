# ---------------------------------------------------------------------
# Use bitarray's prefix-code machinery to build a working Huffman codec.
# ---------------------------------------------------------------------

from collections import Counter
from bitarray import bitarray, decodetree
from bitarray.util import huffman_code


heading("Counting symbol frequencies")
note(
    "Huffman coding gives shorter codes to more common symbols. "
    "We'll compress a short message by counting its character "
    "frequencies, then asking bitarray.util to build a code for us."
)

message = (
    "the quick brown fox jumps over the lazy dog. "
    "the dog was not amused, but the fox was delighted."
)
freq = Counter(message)
note(f"Message length: {len(message)} characters, "
     f"{len(freq)} unique symbols.")

# huffman_code() takes a {symbol: frequency} mapping and returns a
# {symbol: bitarray} prefix code.
codebook = huffman_code(freq)

# Show the shortest few codes (most frequent symbols).
sample = sorted(codebook.items(), key=lambda kv: len(kv[1]))[:6]
rows = "".join(
    f"<tr><td><code>{repr(sym)}</code></td>"
    f"<td>{freq[sym]}</td>"
    f"<td><code>{bits.to01()}</code></td></tr>"
    for sym, bits in sample
)
display(HTML(
    "<table><thead><tr><th>symbol</th><th>count</th>"
    f"<th>code</th></tr></thead><tbody>{rows}</tbody></table>"
), append=True)

heading("Encoding")
note(
    "encode() walks the iterable of symbols and extends the bitarray "
    "with the matching code for each one."
)

encoded = bitarray()
encoded.encode(codebook, message)

raw_bits = len(message) * 8
note(
    f"Raw size:      <strong>{raw_bits}</strong> bits "
    f"({len(message)} bytes)."
)
note(
    f"Encoded size:  <strong>{len(encoded)}</strong> bits "
    f"(~{len(encoded) / 8:.1f} bytes)."
)
note(
    f"Compression ratio: "
    f"<strong>{len(encoded) / raw_bits:.2%}</strong> of the original."
)

heading("Decoding via a decodetree")
note(
    "For repeated decoding, wrap the codebook in a decodetree once. "
    "It precomputes the binary search tree so decode() is fast."
)

tree = decodetree(codebook)
decoded = "".join(encoded.decode(tree))

note(f"First 60 chars decoded: <code>{decoded[:60]!r}</code>")
note(f"Round-trip successful: <strong>{decoded == message}</strong>")
