# ---------------------------------------------------------------------
# Partition, rank, and replace: shaping arrays without a full sort.
# ---------------------------------------------------------------------

heading("Top-k scores without sorting the whole array")
note(
    "<code>bn.partition</code> rearranges an array so the k smallest "
    "values sit (unordered) at the front. It's faster than a full "
    "sort when you only care about the extremes."
)

# Final exam scores for 20 students, on a 0-100 scale.
scores = rng.integers(40, 100, size=20).astype(float)
note("Raw scores:")
display(scores, append=True)

# Place the 5 lowest scores at the start of the array (in any order),
# then read them off. To get the top 5, partition the *negated* array.
k = 5
lowest_first = bn.partition(scores, kth=k - 1)
top_first = -bn.partition(-scores, kth=k - 1)

note(f"Five lowest scores (unordered): {lowest_first[:k]}")
note(f"Five highest scores (unordered): {top_first[:k]}")

# `argpartition` returns indices instead of values -- useful when you
# want to look up matching records in a parallel array.
student_names = np.array([f"student_{i:02d}" for i in range(len(scores))])
top_idx = bn.argpartition(-scores, kth=k - 1)[:k]
note("Top-5 students by index, with their scores:")
for i in top_idx:
    note(f"&nbsp;&nbsp;{student_names[i]} &rarr; {scores[i]:.0f}")

# ---------------------------------------------------------------------
heading("Ranking values, with NaN-awareness")
note(
    "<code>rankdata</code> assigns ranks (averaging ties), and "
    "<code>nanrankdata</code> does the same while skipping NaN."
)

readings = np.array([3.2, 1.0, np.nan, 3.2, 5.5, 2.1, np.nan, 4.0])
note(f"Readings: {readings}")
note(f"Ranks (NaN-aware): {bn.nanrankdata(readings)}")

# ---------------------------------------------------------------------
heading("Replacing sentinel values in place")
note(
    "<code>bn.replace</code> rewrites an array in place, swapping one "
    "value for another. A common use is turning a sentinel like -999 "
    "into NaN so the <code>nan*</code> functions can ignore it."
)

raw = np.array([12.0, -999.0, 14.5, -999.0, 13.1, 15.0])
note(f"Before: {raw}")
bn.replace(raw, -999.0, np.nan)
note(f"After replace(-999, NaN): {raw}")
note(f"Now <code>bn.nanmean</code> works cleanly: {bn.nanmean(raw):.3f}")
