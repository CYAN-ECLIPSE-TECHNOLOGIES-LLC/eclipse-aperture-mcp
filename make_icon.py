#!/usr/bin/env python3
"""Generate icon-512.png — brand system §6: eclipse motif on the navy
field (#0d1b2a), one per-product glyph. Aperture's glyph is the camera
aperture itself: six blades forming the hexagonal opening inside the
eclipse ring — the light a visual platform lets in. PIL only."""
import math

from PIL import Image, ImageDraw

S = 512
NAVY = (13, 27, 42, 255)
STOPS = [(15, 246, 247), (0, 212, 255), (123, 44, 191)]  # cyan->blue->purple


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3)) + (255,)


def grad(t):
    return lerp(STOPS[0], STOPS[1], t * 2) if t < 0.5 else \
        lerp(STOPS[1], STOPS[2], (t - 0.5) * 2)


def main():
    img = Image.new("RGBA", (S, S), NAVY)
    d = ImageDraw.Draw(img)
    cx, cy, r_out = 256, 256, 168
    box = [cx - r_out, cy - r_out, cx + r_out, cy + r_out]
    for i in range(90):
        t = i / 90
        d.arc(box, start=i * 4, end=i * 4 + 5, fill=grad(t), width=15)
    # Six aperture blades: chords from rim points to the inner hexagon.
    r_in = 74
    rim, inner = [], []
    for k in range(6):
        a = math.radians(60 * k - 90)
        rim.append((cx + r_out * 0.94 * math.cos(a),
                    cy + r_out * 0.94 * math.sin(a)))
        a2 = math.radians(60 * k - 30)
        inner.append((cx + r_in * math.cos(a2),
                      cy + r_in * math.sin(a2)))
    for k in range(6):
        d.line([rim[k], inner[k]], fill=grad(k / 6.0), width=11)
    for k in range(6):
        x0, y0 = inner[k]
        x1, y1 = inner[(k + 1) % 6]
        d.line([(x0, y0), (x1, y1)], fill=grad(0.55 + k * 0.07), width=9)
    img.save("icon-512.png")
    print("wrote icon-512.png", img.size, img.mode)


if __name__ == "__main__":
    main()
