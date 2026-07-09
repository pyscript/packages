# Touring the colorama palette: Fore, Back, and Style.

heading("The standard foreground colors")
note(
    "Fore.<NAME> sets the text color. The eight standard colors are "
    "BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, and WHITE."
)

standard_fg = ["BLACK", "RED", "GREEN", "YELLOW",
               "BLUE", "MAGENTA", "CYAN", "WHITE"]

lines = []
for name in standard_fg:
    color = getattr(Fore, name)
    lines.append(f"{color}Fore.{name:<8}{Style.RESET_ALL}  the quick brown fox")

display(HTML(ansi_to_html("\n".join(lines))), append=True)


heading("Background colors and brightness")
note(
    "Back.<NAME> sets the background. Style.BRIGHT, Style.DIM, and "
    "Style.NORMAL adjust intensity. Combine freely; remember to reset."
)

combos = [
    Back.RED + Fore.WHITE + Style.BRIGHT + " ALERT  " + Style.RESET_ALL,
    Back.YELLOW + Fore.BLACK + " WARNING " + Style.RESET_ALL,
    Back.GREEN + Fore.BLACK + Style.BRIGHT + "  OK    " + Style.RESET_ALL,
    Back.BLUE + Fore.WHITE + "  INFO   " + Style.RESET_ALL,
    Style.DIM + Fore.WHITE + " (dim debug trace) " + Style.RESET_ALL,
]
display(HTML(ansi_to_html("  ".join(combos))), append=True)


heading("The LIGHT_EX variants")
note(
    "Beyond the eight standard colors, colorama also exposes "
    "LIGHTRED_EX, LIGHTGREEN_EX, and friends for brighter tones."
)

light_fg = ["LIGHTBLACK_EX", "LIGHTRED_EX", "LIGHTGREEN_EX",
            "LIGHTYELLOW_EX", "LIGHTBLUE_EX", "LIGHTMAGENTA_EX",
            "LIGHTCYAN_EX", "LIGHTWHITE_EX"]

lines = []
for name in light_fg:
    color = getattr(Fore, name)
    lines.append(f"{color}Fore.{name:<15}{Style.RESET_ALL}  shine on")

display(HTML(ansi_to_html("\n".join(lines))), append=True)
