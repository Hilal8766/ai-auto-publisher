import os
import subprocess
from pathlib import Path

from .config import settings


OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def create_voice(
    text: str,
    output_file: str = "output/voice.mp3"
):
    """
    Voice generation hook.
    Actual TTS provider baad mein connect kiya ja sakta hai.
    """

    output_path = Path(output_file)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # TTS provider connect hone tak placeholder.
    return {
        "status": "pending",
        "file": str(output_path),
        "message": "TTS provider not connected yet."
    }


def render_video(
    voice_file: str,
    output_file: str = "output/video_4k.mp4",
    width: int = 3840,
    height: int = 2160
):
    """
    FFmpeg ke through 4K video render karta hai.
    """

    output_path = Path(output_file)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if not os.path.exists(voice_file):
        return {
            "status": "error",
            "message": "Voice file not found.",
            "file": str(output_path)
        }

    command = [
        "ffmpeg",
        "-y",

        "-i",
        voice_file,

        "-vf",
        (
            f"scale={width}:{height}:"
            "force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"
        ),

        "-c:v",
        "libx264",

        "-preset",
        "medium",

        "-crf",
        "18",

        "-c:a",
        "aac",

        "-b:a",
        "192k",

        "-movflags",
        "+faststart",

        str(output_path)
    ]

    try:

        subprocess.run(
            command,
            check=True
        )

        return {
            "status": "success",
            "file": str(output_path),
            "resolution": "3840x2160"
        }

    except FileNotFoundError:

        return {
            "status": "error",
            "message": "FFmpeg is not installed.",
            "file": str(output_path)
        }

    except subprocess.CalledProcessError as error:

        return {
            "status": "error",
            "message": str(error),
            "file": str(output_path)
        }


def create_thumbnail(
    text: str,
    output_file: str = "output/thumbnail.txt"
):
    """
    Thumbnail generation hook.
    Actual image-generation service baad mein connect hoga.
    """

    output_path = Path(output_file)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path.write_text(
        text[:100],
        encoding="utf-8"
    )

    return {
        "status": "success",
        "file": str(output_path),
        "text": text[:100]
    }


def prepare_media(
    script: str,
    title: str
):
    """
    Complete media preparation flow.
    """

    voice = create_voice(script)

    thumbnail = create_thumbnail(
        title
    )

    return {
        "voice": voice,
        "thumbnail": thumbnail
  }
