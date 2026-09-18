import os
import re
import math
import asyncio
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

try:
    import edge_tts
except ImportError:
    edge_tts = None


OUTPUT_DIR = Path("output")
SCENE_DIR = OUTPUT_DIR / "scenes"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SCENE_DIR.mkdir(parents=True, exist_ok=True)


def get_resolution():
    value = os.getenv("VIDEO_RESOLUTION", "4k").lower()

    if value == "8k":
        return 7680, 4320

    if value == "1080p":
        return 1920, 1080

    return 3840, 2160


def get_font(size):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    ]

    for font in candidates:
        if Path(font).exists():
            return ImageFont.truetype(font, size)

    return ImageFont.load_default()
