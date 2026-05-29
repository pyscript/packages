# ---------------------------------------------------------------------
# Simulating the Happy Eyeballs race
# ---------------------------------------------------------------------
#
# In production you'd hand a list of addrinfos to
# `aiohappyeyeballs.start_connection(...)` along with an event loop, and
# it would race connection attempts across address families, staggering
# each new attempt by `happy_eyeballs_delay` seconds (default 0.25s per
# RFC 8305) until one succeeds.
#
# We can't open real sockets here, but we can simulate the race itself
# to build intuition for what the algorithm does. Each "address" gets a
# pretend connect-time and success flag; we then schedule attempts using
# the same staggered pattern that start_connection uses internally.

heading("A scenario: one slow IPv6 address, one fast IPv4 address")
note(
    "Imagine the first IPv6 address is slow to respond (perhaps the route "
    "is congested) but the IPv4 fallback is quick. We'll order the addrinfos "
    "the way getaddrinfo typically does — IPv6 first — and let Happy Eyeballs "
    "race them."
)

# Each entry: (family, type, proto, canonname, sockaddr, connect_seconds, will_succeed)
scenario = [
    (socket.AF_INET6, socket.SOCK_STREAM, 6, "", ("2001:db8::1", 80, 0, 0), 1.20, True),
    (socket.AF_INET6, socket.SOCK_STREAM, 6, "", ("2001:db8::2", 80, 0, 0), 1.30, True),
    (socket.AF_INET,  socket.SOCK_STREAM, 6, "", ("203.0.113.10", 80),        0.40, True),
    (socket.AF_INET,  socket.SOCK_STREAM, 6, "", ("203.0.113.11", 80),        0.45, True),
]
addr_infos = [row[:5] for row in scenario]
connect_times = {row[4]: row[5] for row in scenario}
will_succeed = {row[4]: row[6] for row in scenario}


async def simulate_happy_eyeballs(addr_infos, delay=0.25):
    """Race fake connect() calls with a staggered start, like RFC 8305."""
    loop = asyncio.get_event_loop()
    started_at = loop.time()
    log = []  # (sockaddr, start, end, outcome)
    winner = None

    async def fake_connect(sockaddr):
        start = loop.time() - started_at
        try:
            await asyncio.sleep(connect_times[sockaddr])
        except asyncio.CancelledError:
            log.append((sockaddr, start, loop.time() - started_at, "cancelled"))
            raise
        end = loop.time() - started_at
        if not will_succeed[sockaddr]:
            log.append((sockaddr, start, end, "failed"))
            raise OSError("simulated failure")
        log.append((sockaddr, start, end, "won"))
        return sockaddr

    tasks = []
    for _family, _type, _proto, _canon, sockaddr in addr_infos:
        tasks.append(asyncio.create_task(fake_connect(sockaddr)))
        try:
            # Give this attempt a head start before launching the next.
            await asyncio.wait_for(asyncio.shield(tasks[-1]), timeout=delay)
            winner = tasks[-1].result()
            break
        except asyncio.TimeoutError:
            continue  # stagger: launch the next address
        except OSError:
            continue  # this attempt failed early; move on

    if winner is None:
        # Nothing won during staggering; wait for the first to finish.
        done, pending = await asyncio.wait(
            tasks, return_when=asyncio.FIRST_COMPLETED
        )
        for task in done:
            if not task.cancelled() and task.exception() is None:
                winner = task.result()
                break
        for task in pending:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

    return winner, log


winner, log = await simulate_happy_eyeballs(addr_infos, delay=0.25)
note(f"Winning address: <code>{winner}</code>")

# Visualise the race as a Gantt-style chart.
fig, ax = plt.subplots(figsize=(9, 3.5))
colors = {"won": "seagreen", "cancelled": "lightgray", "failed": "indianred"}
for i, (sockaddr, start, end, outcome) in enumerate(log):
    ax.barh(i, end - start, left=start, color=colors[outcome],
            edgecolor="black", linewidth=0.5)
    ax.text(end + 0.02, i, outcome, va="center", fontsize=9)
ax.set_yticks(range(len(log)))
ax.set_yticklabels([str(entry[0]) for entry in log], fontsize=9)
ax.set_xlabel("Time since start (seconds)")
ax.set_title("Happy Eyeballs race: staggered connection attempts")
ax.invert_yaxis()
fig.tight_layout()
display(fig, append=True)

heading("Pruning a flaky address before the next attempt")
note(
    "If your application learns that an address is unhealthy, you can clean "
    "the addrinfo list before reusing it. Here we drop the slow IPv6 address "
    "and reorder so the IPv4 fallback is tried first."
)
pruned = list(addr_infos)
remove_addr_infos(pruned, "2001:db8::1")
pop_addr_infos_interleave(pruned, 0)  # no-op example: keeps ordering intact
note("Cleaned addrinfo list:")
for entry in pruned:
    display(HTML(f"<code>{entry}</code>"), append=True)
