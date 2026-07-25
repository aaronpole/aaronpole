"""
Cleans a portrait photo before it gets turned into ASCII art:
  1. Removes the background with rembg
  2. Evens out lighting with CLAHE (adaptive histogram equalization)
  3. Composites the result onto a solid white canvas

Usage (Windows, from the repo root, with the art venv active):
    python tools\\clean_photo.py my-photo.jpg

Writes:
    assets\\photo-ready.png
"""
import io
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def clean_photo(input_path: str, output_path: str = "assets/photo-ready.png") -> None:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # 1. Remove background -> RGBA image with a transparent background
    input_bytes = Path(input_path).read_bytes()
    output_bytes = remove(input_bytes)
    rgba = Image.open(io.BytesIO(output_bytes)).convert("RGBA")

    # 2. Even out lighting on the L (lightness) channel only, keep the alpha mask
    rgb = np.array(rgba.convert("RGB"))
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    l_channel = clahe.apply(l_channel)
    lab = cv2.merge((l_channel, a_channel, b_channel))
    rgb_equalized = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

    equalized = Image.fromarray(rgb_equalized).convert("RGBA")
    equalized.putalpha(rgba.split()[-1])  # restore the original cutout mask

    # 3. Composite onto a solid white canvas so the background reads as "light"
    canvas = Image.new("RGBA", equalized.size, (255, 255, 255, 255))
    canvas.paste(equalized, (0, 0), equalized)
    canvas.convert("RGB").save(output_path)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools\\clean_photo.py <path-to-photo>")
        sys.exit(1)
    clean_photo(sys.argv[1])
