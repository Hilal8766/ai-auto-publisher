import os
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import asyncio

try:
    import edge_tts
except ImportError:
    edge_tts = None


OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_resolution():
    resolution = os.getenv("VIDEO_RESOLUTION", "4k").lower()

    if resolution == "8k":
        return 7680, 4320

    if resolution == "1080p":
        return 1920, 1080

    return 3840, 2160


def create_voice(
    text: str,
    output_file: str = "output/voice.mp3"
):
    """
    Hindi AI voice generation.
    """

    output_path = Path(output_file)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if not text:
        return {
            "status": "error",
            "message": "Script is empty."
        }

    if edge_tts is None:
        return {
            "status": "error",
            "message": "edge-tts is not installed."
        }

    async def generate():
        voice = "hi-IN-SwaraNeural"

        communicator = edge_tts.Communicate(
            text,
            voice
        )

        await communicator.save(
            str(output_path)
        )

    try:
        asyncio.run(generate())

        return {
            "status": "success",
            "file": str(output_path)
        }

    except Exception as error:
        return {
            "status": "error",
            "message": str(error)
        }


def create_visual(
    title: str,
    output_file: str = "output/background.jpg"
):
    """
    Non-black visual background.
    """

    width, height = get_resolution()

    image = Image.new(
        "RGB",
        (width, height)
    )

    pixels = image.load()

    for y in range(height):
        ratio = y / max(height - 1, 1)

        r = int(20 + 60 * ratio)
        g = int(40 + 50 * ratio)
        b = int(90 + 80 * ratio)

        for x in range(width):
            pixels[x, y] = (
                r,
                g,
                b
            )

    draw = ImageDraw.Draw(image)

    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    ]

    font = None

    for path in font_paths:
        if os.path.exists(path):
            font = ImageFont.truetype(
                path,
                max(50, width // 35)
            )
            break

    if font is None:
        font = ImageFont.load_default()

    text = title[:120]

    bbox = draw.textbbox(
        (0, 0),
        text,
        font=font
    )

    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (width - text_width) // 2
    y = (height - text_height) // 2

    draw.text(
        (x + 5, y + 5),
        text,
        font=font,
        fill=(0, 0, 0)
    )

    draw.text(
        (x, y),
        text,
        font=font,
        fill=(255, 255, 255)
    )

    image.save(
        output_file,
        quality=95
    )

    return {
        "status": "success",
        "file": output_file,
        "resolution": f"{width}x{height}"
    }


def render_video(
    voice_file: str,
    visual_file: str,
    output_file: str = "output/video.mp4"
):
    """
    Creates a real MP4 video using FFmpeg.
    """

    output_path = Path(output_file)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if not os.path.exists(voice_file):
        return {
            "status": "error",
            "message": "Voice file not found."
        }

    if not os.path.exists(visual_file):
        return {
            "status": "error",
            "message": "Visual file not found."
        }

    width, height = get_resolution()

    command = [
        "ffmpeg",
        "-y",

        "-loop",
        "1",

        "-i",
        visual_file,

        "-i",
        voice_file,

        "-vf",
        f"scale={width}:{height}:"
        "force_original_aspect_ratio=increase,"
        f"crop={width}:{height}",

        "-c:v",
        "libx264",

        "-preset",
        "veryfast",

        "-crf",
        "20",

        "-pix_fmt",
        "yuv420p",

        "-c:a",
        "aac",

        "-b:a",
        "192k",

        "-shortest",

        "-movflags",
        "+faststart",

        output_file
    ]

    try:

        subprocess.run(
            command,
            check=True
        )

        return {
            "status": "success",
            "file": output_file,
            "resolution": f"{width}x{height}"
        }

    except Exception as error:

        return {
            "status": "error",
            "message": str(error)
        }


def create_thumbnail(
    text: str,
    output_file: str = "output/thumbnail.jpg"
):
    """
    Creates a real thumbnail image.
    """

    width = 1280
    height = 720

    image = Image.new(
        "RGB",
        (width, height),
        (30, 30, 60)
    )

    draw = ImageDraw.Draw(image)

    font_path = (
        "/usr/share/fonts/truetype/dejavu/"
        "DejaVuSans-Bold.ttf"
    )

    if os.path.exists(font_path):

        font = ImageFont.truetype(
            font_path,
            70
        )

    else:

        font = ImageFont.load_default()

    title = text[:70]

    bbox = draw.textbbox(
        (0, 0),
        title,
        font=font
    )

    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (width - text_width) // 2
    y = (height - text_height) // 2

    draw.text(
        (x + 5, y + 5),
        title,
        font=font,
        fill=(0, 0, 0)
    )

    draw.text(
        (x, y),
        title,
        font=font,
        fill=(255, 255, 255)
    )

    image.save(
        output_file,
        quality=95
    )

    return {
        "status": "success",
        "file": output_file
    }


def prepare_media(
    script: str,
    title: str
):
    """
    Complete media generation:
    Voice → Visual → Video → Thumbnail
    """

    voice = create_voice(
        script,
        "output/voice.mp3"
    )

    if voice.get("status") != "success":
        return {
            "voice": voice,
            "status": "error"
        }

    visual = create_visual(
        title,
        "output/background.jpg"
    )

    video = render_video(
        voice_file=voice["file"],
        visual_file=visual["file"],
        output_file="output/video.mp4"
    )

    thumbnail = create_thumbnail(
        title,
        "output/thumbnail.jpg"
    )

    return {
        "status": "success",
        "voice": voice,
        "visual": visual,
        "video": video,
        "thumbnail": thumbnail
    }
