# ---------------------------------------------------------------------
# Picking an implementation at runtime based on the detected library.
# ---------------------------------------------------------------------

heading("Writing one API that adapts to multiple async runtimes")
note(
    "A common pattern: a library function that wants to call "
    "<code>asyncio.sleep</code> when it's running under asyncio, "
    "<code>trio.sleep</code> under trio, and so on. Sniffio lets "
    "you branch on the answer without your callers having to tell "
    "you anything."
)


async def portable_sleep(seconds):
    """Sleep using whichever async library is currently running."""
    library = current_async_library()
    if library == "asyncio":
        await asyncio.sleep(seconds)
        return f"slept {seconds}s via asyncio.sleep"
    elif library == "trio":
        # Imported lazily so we only pay for what we use.
        import trio
        await trio.sleep(seconds)
        return f"slept {seconds}s via trio.sleep"
    elif library == "curio":
        import curio
        await curio.sleep(seconds)
        return f"slept {seconds}s via curio.sleep"
    else:
        raise RuntimeError(f"Unsupported async library: {library}")


async def demo():
    note("Calling our portable helper from an asyncio task...")
    result = await portable_sleep(0.05)
    return result


outcome = asyncio.run(demo())
display(HTML(f"<p>Result: <strong>{outcome}</strong></p>"), append=True)

note(
    "The same <code>portable_sleep</code> function would work "
    "unchanged under <code>trio.run(...)</code> or "
    "<code>curio.run(...)</code>. That's the whole pitch: write "
    "the dispatch once, support every runtime."
)
