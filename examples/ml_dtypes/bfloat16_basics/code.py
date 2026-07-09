"""
A first look at ml_dtypes: the bfloat16 dtype.

ml_dtypes provides NumPy dtype extensions used widely in machine
learning (bfloat16, several float8 variants, sub-byte ints, etc.).
Importing the package also registers the dtypes with NumPy, so you
can use them anywhere a regular dtype is accepted.

Docs: https://github.com/jax-ml/ml_dtypes
"""
import numpy as np
from ml_dtypes import bfloat16
from IPython.core.display import display, HTML

heading("1. Creating a bfloat16 array")
note(
    "bfloat16 is a 16-bit float with the same exponent range as "
    "float32 (8 bits) but only 7 mantissa bits. It trades precision "
    "for range, which suits ML workloads."
)

# Construct a bfloat16 array. Once ml_dtypes is imported, NumPy
# also recognizes the dtype by string name.
weights_f32 = rng.normal(size=8).astype(np.float32)
weights_bf16 = weights_f32.astype(bfloat16)

note("The same eight values, side by side at different precisions:")
comparison = np.empty(
    (3, 8),
    dtype=object,
)
comparison[0] = [f"{x:.6f}" for x in weights_f32]
comparison[1] = [f"{x:.6f}" for x in weights_bf16.astype(np.float32)]
comparison[2] = [f"{float(a) - float(b):+.2e}"
                 for a, b in zip(weights_f32, weights_bf16.astype(np.float32))]
rows = "".join(
    "<tr>" + f"<th>{label}</th>" +
    "".join(f"<td>{cell}</td>" for cell in comparison[i]) + "</tr>"
    for i, label in enumerate(["float32", "bfloat16", "delta"])
)
display(HTML(f"<table>{rows}</table>"), append=True)

heading("2. Memory savings")
note(
    f"float32 uses {weights_f32.nbytes} bytes for 8 values; "
    f"bfloat16 uses {weights_bf16.nbytes}. Half the memory, "
    "same exponent range."
)

heading("3. dtype is registered with NumPy")
# After importing ml_dtypes, np.dtype('bfloat16') resolves.
note(f"np.dtype('bfloat16') -> <code>{np.dtype('bfloat16')}</code>")
note(f"itemsize: <code>{np.dtype('bfloat16').itemsize}</code> bytes")
