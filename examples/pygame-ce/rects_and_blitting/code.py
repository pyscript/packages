# ---------------------------------------------------------------------
# Rects, sprites, and blitting one Surface onto another.
# ---------------------------------------------------------------------

import pygame
pygame.init()


def show_surface(surface, caption=""):
    buffer = io.BytesIO()
    pygame.image.save(surface, buffer, "PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    label = f"<div><em>{caption}</em></div>" if caption else ""
    display(
        HTML(
            f'{label}<img src="data:image/png;base64,{encoded}" '
            f'style="image-rendering: pixelated; max-width: 100%;">'
        ),
        append=True,
    )


heading("Rects: the workhorse of pygame")
note(
    "A pygame.Rect describes a rectangular area: position and size. "
    "Almost every game uses Rects for positioning sprites, "
    "detecting collisions, and clipping draw operations."
)

# Build a small "sprite" Surface with per-pixel alpha so its
# transparent areas don't show when we blit it later.
def make_token(color, label):
    """Make a 64x64 round token with a letter on it."""
    token = pygame.Surface((64, 64), pygame.SRCALPHA)
    pygame.draw.circle(token, color, (32, 32), 30)
    pygame.draw.circle(token, "white", (32, 32), 30, width=3)
    font = pygame.font.SysFont(None, 40)
    text = font.render(label, True, "white")
    token.blit(text, text.get_rect(center=(32, 32)))
    return token

red_token = make_token("crimson", "R")
blue_token = make_token("steelblue", "B")

# A board to blit them onto.
board = pygame.Surface((480, 320))
board.fill((20, 80, 40))  # felt-table green

# Draw a grid of guide lines using Rect for the playfield.
play_area = pygame.Rect(20, 20, 440, 280)
pygame.draw.rect(board, (10, 50, 25), play_area)
pygame.draw.rect(board, "white", play_area, width=2)

# Place the tokens. Surface.get_rect() gives us a Rect we can move
# around with helpers like .center, .move(), and .colliderect().
red_rect = red_token.get_rect(center=(140, 160))
blue_rect = blue_token.get_rect(center=(180, 170))

# blit() copies one Surface onto another at the rect's top-left.
board.blit(red_token, red_rect)
board.blit(blue_token, blue_rect)

# Rects can detect overlap, useful for collision checks.
overlapping = red_rect.colliderect(blue_rect)
note(f"Do the two tokens overlap? <strong>{overlapping}</strong>")

show_surface(board, caption="Two tokens blitted onto a board")

heading("Animating a Rect across frames")
note(
    "A game loop usually updates positions then redraws. Here we "
    "render a few frames of a token sliding across the board and "
    "show them as a strip so you can see the motion."
)

frames = []
slider = make_token("gold", "G")
slider_rect = slider.get_rect(center=(60, 160))

for step in range(5):
    frame = board.copy()
    # Move the rect 90 pixels to the right each frame.
    slider_rect = slider_rect.move(90, 0)
    frame.blit(slider, slider_rect)
    frames.append(frame)

# Compose all frames into one tall image.
strip = pygame.Surface((480, 320 * len(frames)))
for index, frame in enumerate(frames):
    strip.blit(frame, (0, index * 320))

show_surface(strip, caption="Five frames of a sliding token")
