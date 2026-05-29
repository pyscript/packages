# ---------------------------------------------------------------------
# Teaching sniffio about a brand-new async library.
# ---------------------------------------------------------------------

heading("Making your own coroutine runner discoverable")
note(
    "If you build a new async runtime, you can make sniffio "
    "report it by setting <code>sniffio.thread_local.name</code> "
    "to your library's name while a coroutine is running. "
    "Sniffio checks this thread-local first, before any built-in "
    "detection. We'll simulate a tiny runtime called "
    "<em>tinyloop</em> to show the idea."
)


def tinyloop_run(coro):
    """A toy coroutine driver that announces itself to sniffio."""
    previous = thread_local.name
    thread_local.name = "tinyloop"
    try:
        # Step the coroutine to completion. A real event loop would
        # schedule callbacks here; we just send None until it stops.
        try:
            while True:
                coro.send(None)
        except StopIteration as stop:
            return stop.value
    finally:
        thread_local.name = previous


async def report():
    return current_async_library()


detected = tinyloop_run(report())
display(HTML(f"<p>While running under tinyloop, sniffio reports: "
             f"<strong>{detected}</strong></p>"), append=True)

note(
    "After <code>tinyloop_run</code> returns, the thread-local is "
    "restored, so subsequent code outside any runtime sees the "
    "original state again."
)

display(HTML(f"<p>Current thread_local.name after run: "
             f"<code>{thread_local.name!r}</code></p>"), append=True)
