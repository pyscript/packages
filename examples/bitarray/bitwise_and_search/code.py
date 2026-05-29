# ---------------------------------------------------------------------
# Bitwise operators, fast slice fills, and substring search.
# ---------------------------------------------------------------------

heading("A tiny permissions model with bitwise ops")
note(
    "Imagine eight feature flags per user. We'll combine flags "
    "for two users with AND/OR/XOR, just like flag bytes in C."
)

#                  RWX RWX RW
#                  abc def gh
alice = bitarray("1110 1010 11")
bob   = bitarray("1010 1110 01")

note(f"alice & bob = {(alice & bob)!r}  (shared permissions)")
note(f"alice | bob = {(alice | bob)!r}  (combined permissions)")
note(f"alice ^ bob = {(alice ^ bob)!r}  (where they differ)")
note(f"~alice      = {(~alice)!r}  (inverted)")

# count_xor is the Hamming distance between two equal-length bitarrays,
# computed without creating an intermediate bitarray.
note(f"Hamming distance (alice, bob) = {count_xor(alice, bob)}")

heading("Slice assignment to a boolean")
note(
    "Assigning a single boolean to a slice fills that whole slice. "
    "This is faster than building a temporary bitarray of all 1s. "
    "Here we mark every 5th day in a 60-day calendar as 'busy'."
)

calendar = bitarray(60)
calendar.setall(0)
calendar[4::5] = True            # bool-to-slice fill
calendar[10:14] = True           # set a contiguous range
note(f"calendar = {calendar.to01(group=10)!r}")
note(f"busy days: {calendar.count(1)} of {len(calendar)}")

heading("Searching for a bit pattern")
note(
    "search() returns an iterator over every starting index where "
    "a sub-bitarray occurs (non-overlapping, left-to-right by default)."
)

stream = bitarray("0010 1101 0010 0010 1101 0010 1101")
needle = bitarray("1101")
hits = list(stream.search(needle))
note(f"stream = {stream!r}")
note(f"positions of {needle!r}: {hits}")
note(f"count of {needle!r} (non-overlapping): {stream.count(needle)}")

heading("Storing big numbers as bits")
note(
    "Bitarrays are a compact way to play with arbitrary-width "
    "integers. Here we add two 32-bit numbers via int2ba/ba2int."
)

a, b = 0x1234_5678, 0x0FED_CBA9
total = ba2int(int2ba(a, 32)) + ba2int(int2ba(b, 32))
note(f"0x{a:08X} + 0x{b:08X} = 0x{total:08X}")
