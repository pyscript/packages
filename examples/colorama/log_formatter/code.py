# Building a tiny colored log formatter on top of colorama.
#
# This is a common real-world use case: tag log lines by severity
# with color so the eye can scan them quickly. On Windows, calling
# `just_fix_windows_console()` once at program start is enough to
# make these ANSI sequences render correctly in the console.

# Recommended one-liner for cross-platform support. On non-Windows
# platforms, and inside this browser sandbox, it's a harmless no-op.
just_fix_windows_console()


# Map severity to a (foreground, style) pair. We keep the styling
# table separate from the formatting logic so it's easy to tweak.
SEVERITY_STYLES = {
    "DEBUG":    (Fore.LIGHTBLACK_EX, Style.DIM),
    "INFO":     (Fore.CYAN,          Style.NORMAL),
    "WARNING":  (Fore.YELLOW,        Style.BRIGHT),
    "ERROR":    (Fore.RED,           Style.BRIGHT),
    "CRITICAL": (Fore.WHITE + Back.RED, Style.BRIGHT),
}


def format_log(timestamp, level, message):
    """Return a colored log line. Always end with Style.RESET_ALL."""
    color, weight = SEVERITY_STYLES.get(level, (Fore.WHITE, Style.NORMAL))
    return (
        Style.DIM + timestamp + Style.RESET_ALL
        + " "
        + color + weight + f"{level:<8}" + Style.RESET_ALL
        + " " + message
    )


sample_events = [
    ("08:00:01", "INFO",     "Service started on port 8080"),
    ("08:00:02", "DEBUG",    "Loaded 42 routes from config"),
    ("08:00:15", "INFO",     "User 'ada' signed in"),
    ("08:01:03", "WARNING",  "Cache miss rate above 30%"),
    ("08:01:47", "ERROR",    "Database query timed out after 5s"),
    ("08:02:00", "CRITICAL", "Disk usage at 99% — failing over"),
]

heading("A colored log stream")
note(
    "Each line is plain text plus a few colorama escape codes. "
    "The format function stays simple; styling lives in a table."
)

log_text = "\n".join(
    format_log(ts, level, msg) for ts, level, msg in sample_events
)
display(HTML(ansi_to_html(log_text)), append=True)

heading("Tip: autoreset")
note(
    "If you find yourself appending Style.RESET_ALL after every print, "
    "call <code>colorama.init(autoreset=True)</code> once at program "
    "start, and colorama will append a reset to each print for you."
)
