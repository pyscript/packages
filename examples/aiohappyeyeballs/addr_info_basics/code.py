"""
A first look at aiohappyeyeballs: shaping addrinfo lists.

The Happy Eyeballs algorithm (RFC 8305) races IPv6 and IPv4 connection
attempts so dual-stack clients fall back gracefully when one family is
slow or unreachable. The aiohappyeyeballs package provides the building
blocks asyncio uses to do this when you already have a list of resolved
addresses (rather than a hostname).

In this first example we'll skip the network entirely and focus on the
addrinfo helpers: the small list-manipulation utilities that let you
prepare and tidy the input to the Happy Eyeballs machinery.
"""
from IPython.core.display import display, HTML
import socket

heading("A handful of resolved addresses for example.org")
note(
    "Normally you'd get this list from <code>loop.getaddrinfo()</code> or a "
    "DNS cache. We'll build it by hand so we can see exactly what the helpers do."
)

# Each entry is the same 5-tuple shape that socket.getaddrinfo returns:
# (family, type, proto, canonname, sockaddr).
addr_infos = [
    (socket.AF_INET6, socket.SOCK_STREAM, 6, "", ("2606:2800:220:1::1", 80, 0, 0)),
    (socket.AF_INET6, socket.SOCK_STREAM, 6, "", ("2606:2800:220:1::2", 80, 0, 0)),
    (socket.AF_INET,  socket.SOCK_STREAM, 6, "", ("93.184.216.34", 80)),
    (socket.AF_INET,  socket.SOCK_STREAM, 6, "", ("93.184.216.35", 80)),
]
format_addr_infos(addr_infos)

heading("Adding a local bind address with addr_to_addr_infos")
note(
    "When you want to bind the outgoing socket to a specific local address, "
    "<code>start_connection</code> expects a full addrinfo list, not a tuple. "
    "<code>addr_to_addr_infos</code> does that conversion for you."
)
local_addr_infos = addr_to_addr_infos(("127.0.0.1", 0))
format_addr_infos(local_addr_infos)

heading("Interleaving families with pop_addr_infos_interleave")
note(
    "Happy Eyeballs prefers to alternate between IPv6 and IPv4. "
    "<code>pop_addr_infos_interleave(addr_infos, 1)</code> removes the first "
    "address of each family in place — handy after a successful attempt, to "
    "skip past addresses you already tried."
)
working = list(addr_infos)
pop_addr_infos_interleave(working, 1)
note("After popping one address per family:")
format_addr_infos(working)

heading("Pruning a known-bad address with remove_addr_infos")
note(
    "If you discover an address is unreachable (perhaps from a previous "
    "failure), <code>remove_addr_infos</code> strips every entry that matches."
)
working2 = list(addr_infos)
remove_addr_infos(working2, ("93.184.216.34", 80))
note("After removing 93.184.216.34:80")
format_addr_infos(working2)

note(f"aiohappyeyeballs version in use: <code>{aiohappyeyeballs.__version__}</code>")
