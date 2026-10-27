# minimal-ascii

A minimalist tool for creating beautiful ASCII art.

Convert images to ASCII with proper aspect ratio, gradient mapping, and optional ANSI color. Includes procedural generators for wave interference, mandalas, and gradient fields.

## Install

```bash
pip install Pillow numpy
```

## Usage

### Image → ASCII

```bash
# Basic conversion
python ascii_art.py photo.png

# Custom width
python ascii_art.py photo.png -w 120

# ANSI truecolor output
python ascii_art.py photo.png --color

# Invert for dark terminals
python ascii_art.py photo.png --invert

# Detailed ramp (70 characters) for photographic detail
python ascii_art.py photo.png --detailed

# Block-character ramp
python ascii_art.py photo.png --blocks

# Render output to PNG for sharing
python ascii_art.py photo.png --render output.png
```

### Procedural Generators

```bash
# Wave interference pattern
python ascii_art.py --wave -w 100

# Radial mandala
python ascii_art.py --mandala -w 120

# Gradient field
python ascii_art.py --gradient -w 100
```

## Character Ramps

| Ramp | Characters | Best For |
|------|-----------|----------|
| Standard | ` .:-=+*#%@` | General purpose, clean look |
| Detailed | 70-char gradient | Photographic images, fine detail |
| Blocks | ` ░▒▓█` | High contrast, modern terminals |

## How It Works

**Aspect ratio correction** — Terminal characters are roughly 2× taller than wide. The tool halves the output height so images don't appear stretched vertically.

**Auto-contrast** — Histogram stretching maps the image's actual brightness range to the full 0-255 spectrum, maximizing detail. Disable with `--no-contrast`.

**Gradient mapping** — Each pixel's brightness is normalized to an index into the character ramp. Darker pixels map to heavier characters (`@`, `#`), lighter pixels to lighter ones (`.`, ` `).

**Procedural generation** — The wave generator sums three sine functions at different frequencies to create organic interference patterns. The mandala uses polar coordinates with harmonic petal functions, with the grid sized 2:1 to compensate for character aspect ratio.

## Python API

```python
from ascii_art import image_to_ascii, generate_wave, generate_mandala

# Convert an image
art = image_to_ascii("photo.png", width=100, color=False)

# Generate procedural art
wave = generate_wave(width=100)
mandala = generate_mandala(width=120)

# Render to PNG
from ascii_art import ascii_to_image
ascii_to_image(art, "output.png")
```

## Requirements

- Python 3.8+
- Pillow
- NumPy
