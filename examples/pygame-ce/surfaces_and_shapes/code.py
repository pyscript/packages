"""
A first look at pygame-ce: drawing on a Surface.

Pygame is a game library, and at its heart is the Surface, a 2D
pixel canvas you draw onto. In a normal pygame program you would
call pygame.display.set_mode(...) to get a window-backed Surface
and run a game loop. Here we work with offscreen Surfaces directly,
which is the same API minus the window, and show the result inline.

See https://pyga.me/docs/ for the full reference.
"""
from IPython.core.display import display, HTML

# pygame must be initialized before most subsystems will work.
pygame.init()

heading("Drawing shapes on a Surface")
note(
    "We create a 480x320 Surface, fill the background, and draw some "
    "shapes with pygame.draw. Colors can be given as RGB tuples or "
    "named CSS-style strings."
)

canvas = pygame.Surface((480, 320))
canvas.fill((30, 30, 60))  # deep navy background

# A row of filled circles, like balloons rising.
for index, color in enumerate(["tomato", "gold", "mediumseagreen", "skyblue"]):
    center = (80 + index * 110, 200)
    pygame.draw.circle(canvas, color, center, 36)
    pygame.draw.circle(canvas, "white", center, 36, width=3)

# A polygon (a simple house outline).
house = [(360, 260), (360, 180), (410, 140), (460, 180), (460, 260)]
pygame.draw.polygon(canvas, "khaki", house)
pygame.draw.polygon(canvas, "saddlebrown", house, width=4)

# Anti-aliased line across the sky.
pygame.draw.aaline(canvas, "white", (10, 40), (470, 80))

show_surface(canvas, caption="Hand-drawn scene on a 480x320 Surface")

note(
    "The Surface is just an in-memory image. The same drawing calls "
    "would render to the screen Surface returned by "
    "pygame.display.set_mode in a regular game."
)
