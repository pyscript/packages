"""
Sniffio is a tiny library with a single job: tell you which async
framework is currently running your coroutine. This matters when
you're writing library code that wants to support multiple async
runtimes (asyncio, trio, curio, ...) without forcing the caller to
configure anything.

Docs: https://sniffio.readthedocs.io
"""
from IPython.core.display import display, HTML

heading("1. Sniffing from inside a running coroutine")
note(
    "Inside an async function we can ask sniffio which library is "
    "currently driving the event loop. Here we run under asyncio, "
    "so that's what it reports."
)


async def whats_running():
    library = current_async_library()
    return library


detected = asyncio.run(whats_running())
display(HTML(f"<p>Detected async library: <strong>{detected}</strong></p>"), append=True)


heading("2. Sniffing outside of any async context")
note(
    "If no async library is running, sniffio raises "
    "AsyncLibraryNotFoundError. This is how you'd notice that you "
    "were called from plain synchronous code."
)

try:
    current_async_library()
except AsyncLibraryNotFoundError as exc:
    note(f"Got expected error: <code>{type(exc).__name__}: {exc}</code>")
