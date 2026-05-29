"""
A first look at colorama: cross-platform colored terminal text.

Colorama provides three handy namespaces of ANSI escape constants:
`Fore` for foreground color, `Back` for background color, and
`Style` for brightness. Concatenate them with strings, then print
or capture as usual.
"""
from IPython.core.display import display, HTML

heading("A colorful greeting")
note(
    "Each colorama constant is just a short ANSI escape string. "
    "Add them to your text, then add Style.RESET_ALL to return "
    "to the terminal's defaults."
)

# Build a styled message. In a real terminal, you'd just print this.
greeting = (
    Fore.GREEN + "Hello"
    + Style.RESET_ALL + ", "
    + Fore.RED + Back.YELLOW + Style.BRIGHT + " world! "
    + Style.RESET_ALL
)

# Show what colorama actually produced (escape codes are visible).
note("The raw string contains ANSI escape sequences:")
display(repr(greeting), append=True)

# Render it as it would appear in a terminal.
note("And here's how a terminal would render it:")
display(HTML(ansi_to_html(greeting)), append=True)
