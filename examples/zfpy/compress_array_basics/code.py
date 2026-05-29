"""
Compressing floating-point arrays with zfpy.

zfp is a fast, lossy (or optionally lossless) compressor designed for
multidimensional numerical arrays. The Python bindings expose two
top-level functions: `compress_numpy` and `decompress_numpy`. They
accept any contiguous NumPy array of supported dtype (float32,
float64, int32, int64) and return / consume a `bytes` buffer.

See https://zfp.readthedocs.io/en/release1.0.1/python.html for the
full API.
"""
from IPython.core.display import display, HTML

heading("A smooth 3D field is highly compressible")
note(
    "We build a 64x64x64 grid of a smooth analytic function. "
    "Smooth data compresses dramatically with zfp because nearby "
    "values are highly correlated."
)

# A smooth scalar field on a regular 3D grid -- the kind of data zfp
# was designed for (think simulation output, volumetric scans, etc.).
size = 64
axis = np.linspace(-3.0, 3.0, size, dtype=np.float64)
x, y, z = np.meshgrid(axis, axis, axis, indexing="ij")
field = np.sin(x) * np.cos(y) + 0.5 * np.exp(-(x**2 + y**2 + z**2) / 4)

original_bytes = field.nbytes

# Lossless mode: bit-for-bit reversible. Call with no tolerance / rate
# / precision arguments to get reversible compression.
lossless = zfpy.compress_numpy(field, write_header=True)
restored = zfpy.decompress_numpy(lossless)

note(
    f"Original size: <strong>{original_bytes:,} bytes</strong> "
    f"({field.dtype}, shape {field.shape})."
)
note(
    f"Lossless compressed size: <strong>{len(lossless):,} bytes</strong> "
    f"&mdash; ratio {original_bytes / len(lossless):.2f}x. "
    f"Exact round trip: <strong>{np.array_equal(field, restored)}</strong>."
)

# Lossy mode with an absolute error tolerance. zfp will compress more
# aggressively, guaranteeing |original - decompressed| <= tolerance
# (in most cases).
tolerance = 1e-3
lossy = zfpy.compress_numpy(field, tolerance=tolerance, write_header=True)
lossy_restored = zfpy.decompress_numpy(lossy)
max_err = np.max(np.abs(field - lossy_restored))

note(
    f"Lossy (tolerance={tolerance}): "
    f"<strong>{len(lossy):,} bytes</strong> &mdash; "
    f"ratio {original_bytes / len(lossy):.1f}x, "
    f"observed max error {max_err:.2e}."
)
