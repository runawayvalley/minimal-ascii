#!/usr/bin/env python3
"""
minimal-ascii — A minimalist tool for creating beautiful ASCII art.

Convert images to ASCII with proper aspect ratio, gradient mapping,
and optional ANSI color. Also includes procedural generators for
when you have no image to work with.

Usage:
    python ascii_art.py image.png                  # basic conversion
    python ascii_art.py image.png -w 120           # custom width
    python ascii_art.py image.png --color          # ANSI color output
    python ascii_art.py image.png --invert         # for dark terminals
    python ascii_art.py --wave                     # procedural wave pattern
    python ascii_art.py --mandala                  # procedural mandala
"""

import sys
import math
import argparse
from pathlib import Path

try:
    from PIL import Image
    import numpy as np
except ImportError:
    print("Requires: pip install Pillow numpy")
    sys.exit(1)


# ─── Character Ramps ───────────────────────────────────────────────
# Ordered from lightest (space) to darkest (@).
# The extended ramp gives finer gradation for photographic images.
RAMP_STANDARD = " .:-=+*#%@"
RAMP_DETAILED = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
RAMP_BLOCKS = " ░▒▓█"

# ANSI truecolor helpers
def _ansi_fg(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"

RESET = "\033[0m"


# ─── Core: Image → ASCII ──────────────────────────────────────────

def _auto_contrast(gray: np.ndarray) -> np.ndarray:
    """Stretch histogram to full 0-255 range for maximum detail."""
    lo, hi = gray.min(), gray.max()
    if hi - lo < 1:
        return gray
    return (gray - lo) / (hi - lo) * 255.0


def image_to_ascii(
    image_path: str,
    width: int = 100,
    ramp: str = RAMP_STANDARD,
    invert: bool = False,
    color: bool = False,
    contrast: bool = True,
) -> str:
    """
    Convert an image file to ASCII art.

    Aspect ratio correction: terminal characters are roughly 2× taller
    than wide, so we halve the output height to compensate.
    """
    img = Image.open(image_path)

    # Preserve aspect ratio with 2:1 char correction
    aspect = img.height / img.width
    height = max(1, int(width * aspect * 0.5))

    img = img.resize((width, height))
    gray = np.array(img.convert("L"), dtype=np.float64)

    if contrast:
        gray = _auto_contrast(gray)

    if invert:
        gray = 255.0 - gray

    # Normalize to ramp indices
    ramp_len = len(ramp)
    indices = (gray / 255.0 * (ramp_len - 1)).astype(int)

    lines = []
    if color:
        rgb = np.array(img.convert("RGB"), dtype=np.uint8)
        for row_idx in range(height):
            line_parts = []
            for col_idx in range(width):
                ch = ramp[indices[row_idx, col_idx]]
                r, g, b = rgb[row_idx, col_idx]
                line_parts.append(f"{_ansi_fg(r, g, b)}{ch}{RESET}")
            lines.append("".join(line_parts))
    else:
        for row_idx in range(height):
            line = "".join(ramp[indices[row_idx, c]] for c in range(width))
            lines.append(line)

    return "\n".join(lines)


# ─── Procedural Generators ────────────────────────────────────────

def generate_wave(width=100, height=40, ramp=RAMP_STANDARD) -> str:
    """
    Interference pattern from overlapping sine waves.
    Creates organic, flowing moiré-like structures.
    """
    lines = []
    for y in range(height):
        row = []
        for x in range(width):
            # Three overlapping waves at different frequencies
            v = (
                math.sin(x * 0.15 + y * 0.08)
                + math.sin(x * 0.05 - y * 0.12)
                + math.sin((x + y) * 0.06)
            )
            # Normalize [-3, 3] → [0, 1]
            normalized = (v + 3.0) / 6.0
            idx = int(normalized * (len(ramp) - 1))
            row.append(ramp[idx])
        lines.append("".join(row))
    return "\n".join(lines)


def generate_mandala(width=120, ramp=RAMP_STANDARD) -> str:
    """
    Radial mandala using polar coordinates and harmonic functions.
    Produces symmetric, meditative circular patterns.

    Accounts for the 2:1 terminal character aspect ratio — the grid
    is twice as wide as tall so the rendered result appears circular.
    """
    height = max(1, width // 2)
    cx, cy = width / 2, height / 2
    max_r = min(cx, cy)

    lines = []
    for y in range(height):
        row = []
        for x in range(width):
            dx, dy = x - cx, y - cy
            r = math.sqrt(dx * dx + dy * dy) / max_r
            theta = math.atan2(dy, dx)

            # Harmonic petals modulated by radius
            v = math.sin(theta * 8 + math.sin(r * math.pi * 3) * 3.0)
            v += math.sin(r * math.pi * 4) * 0.5
            normalized = (v + 1.5) / 3.0
            idx = int(max(0, min(len(ramp) - 1, normalized * (len(ramp) - 1))))
            row.append(ramp[idx])
        lines.append("".join(row))
    return "\n".join(lines)


def generate_gradient_field(width=100, height=30, ramp=RAMP_STANDARD) -> str:
    """
    Smooth diagonal gradient with subtle noise texture.
    Good for testing ramp fidelity and terminal rendering.
    """
    lines = []
    for y in range(height):
        row = []
        for x in range(width):
            # Diagonal gradient with sinusoidal ripple
            base = (x / width + y / height) / 2.0
            ripple = math.sin(x * 0.1) * math.cos(y * 0.15) * 0.05
            val = base + ripple
            val = max(0.0, min(1.0, val))
            idx = int(val * (len(ramp) - 1))
            row.append(ramp[idx])
        lines.append("".join(row))
    return "\n".join(lines)


# ─── Rendering to Image (for verification / export) ───────────────

def ascii_to_image(ascii_str: str, output_path: str, font_size: int = 14,
                   bg=(13, 17, 23), fg=(201, 209, 217)) -> str:
    """
    Render ASCII text to a PNG image for visual verification.
    Uses a monospace font with dark background.
    """
    from PIL import Image, ImageDraw, ImageFont

    lines = ascii_str.split("\n")
    char_w = font_size * 0.6  # monospace ratio
    line_h = int(font_size * 1.2)

    img_w = int(len(lines[0]) * char_w) + 20
    img_h = len(lines) * line_h + 20

    img = Image.new("RGB", (img_w, img_h), bg)
    draw = ImageDraw.Draw(img)

    # Try to load a monospace font, fall back to default
    font = None
    for font_path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        "/usr/share/fonts/TTF/DejaVuSansMono.ttf",
    ]:
        if Path(font_path).exists():
            font = ImageFont.truetype(font_path, font_size)
            break
    if font is None:
        font = ImageFont.load_default(size=font_size)

    y = 10
    for line in lines:
        draw.text((10, y), line, fill=fg, font=font)
        y += line_h

    img.save(output_path)
    return output_path


# ─── CLI ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Minimalist ASCII art generator"
    )
    parser.add_argument("image", nargs="?", help="Input image path")
    parser.add_argument("-w", "--width", type=int, default=100,
                        help="Output width in characters (default: 100)")
    parser.add_argument("--color", action="store_true",
                        help="Enable ANSI truecolor output")
    parser.add_argument("--invert", action="store_true",
                        help="Invert brightness (for dark terminals)")
    parser.add_argument("--detailed", action="store_true",
                        help="Use detailed character ramp (70 chars)")
    parser.add_argument("--blocks", action="store_true",
                        help="Use block-character ramp")
    parser.add_argument("--no-contrast", action="store_true",
                        help="Disable auto-contrast histogram stretching")
    parser.add_argument("--wave", action="store_true",
                        help="Generate procedural wave interference pattern")
    parser.add_argument("--mandala", action="store_true",
                        help="Generate procedural mandala pattern")
    parser.add_argument("--gradient", action="store_true",
                        help="Generate procedural gradient field")
    parser.add_argument("--render", type=str, metavar="PNG",
                        help="Render ASCII output to a PNG file")

    args = parser.parse_args()

    # Select ramp
    if args.detailed:
        ramp = RAMP_DETAILED
    elif args.blocks:
        ramp = RAMP_BLOCKS
    else:
        ramp = RAMP_STANDARD

    # Generate or convert
    if args.wave:
        art = generate_wave(width=args.width, ramp=ramp)
    elif args.mandala:
        art = generate_mandala(width=args.width, ramp=ramp)
    elif args.gradient:
        art = generate_gradient_field(width=args.width, ramp=ramp)
    elif args.image:
        if not Path(args.image).exists():
            print(f"Error: file not found: {args.image}")
            sys.exit(1)
        art = image_to_ascii(
            args.image,
            width=args.width,
            ramp=ramp,
            invert=args.invert,
            color=args.color,
            contrast=not args.no_contrast,
        )
    else:
        parser.print_help()
        sys.exit(0)

    print(art)

    if args.render:
        # Strip ANSI codes for image rendering
        import re
        clean = re.sub(r"\033\[[0-9;]*m", "", art)
        path = ascii_to_image(clean, args.render)
        print(f"\n[Rendered to {path}]", file=sys.stderr)


if __name__ == "__main__":
    main()
