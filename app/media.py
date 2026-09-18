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
    fonts = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    ]

    for font in fonts:
        if Path(font).exists():
            return ImageFont.truetype(font, size)

    return ImageFont.load_default()


def create_voice(text, output_file="output/voice.mp3"):
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

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    async def generate():
        communicator = edge_tts.Communicate(
            text=text,
            voice="hi-IN-SwaraNeural"
        )
        await communicator.save(str(output_path))

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


def split_story(script, maximum=30):
    text = re.sub(r"\s+", " ", script).strip()

    if not text:
        return []

    parts = re.split(r"(?<=[।.!?])\s+", text)

    parts = [
        part.strip()
        for part in parts
        if len(part.strip()) > 15
    ]

    if not parts:
        return [text]

    if len(parts) <= maximum:
        return parts

    group_size = max(
        1,
        math.ceil(len(parts) / maximum)
    )

    scenes = []

    for i in range(0, len(parts), group_size):
        chunk = " ".join(
            parts[i:i + group_size]
        )

        if chunk:
            scenes.append(chunk)

        if len(scenes) >= maximum:
            break

    return scenes


def detect_scene(text):
    t = text.lower()

    if any(x in t for x in [
        "जंगल", "वन", "शेर", "भालू",
        "हाथी", "जानवर", "पेड़"
    ]):
        return "forest"

    if any(x in t for x in [
        "गांव", "गाँव", "किसान",
        "खेत", "गरीब", "घर"
    ]):
        return "village"

    if any(x in t for x in [
        "शहर", "बाजार", "सड़क",
        "कार", "बस", "दुकान"
    ]):
        return "city"

    if any(x in t for x in [
        "रात", "अंधेरा", "भूत",
        "डर", "रहस्य", "सुनसान"
    ]):
        return "night"

    if any(x in t for x in [
        "स्कूल", "पढ़ाई", "किताब",
        "अध्यापक", "मास्टर"
    ]):
        return "school"

    if any(x in t for x in [
        "राजा", "रानी", "महल",
        "राजकुमार", "राजकुमारी"
    ]):
        return "palace"

    if any(x in t for x in [
        "नदी", "तालाब", "समुद्र",
        "बारिश", "नाव"
    ]):
        return "water"

    if any(x in t for x in [
        "पहाड़", "पर्वत", "यात्रा", "सफर"
    ]):
        return "mountain"

    return "village"


def draw_background(draw, width, height, scene):
    sky = {
        "forest": (100, 180, 225),
        "village": (120, 195, 235),
        "city": (110, 170, 220),
        "night": (25, 35, 75),
        "school": (120, 195, 235),
        "palace": (130, 180, 230),
        "water": (100, 190, 230),
        "mountain": (125, 190, 235),
    }.get(scene, (120, 195, 235))

    ground = {
        "forest": (45, 125, 60),
        "village": (110, 160, 70),
        "city": (75, 80, 90),
        "night": (30, 45, 50),
        "school": (100, 155, 75),
        "palace": (110, 150, 75),
        "water": (40, 130, 175),
        "mountain": (80, 125, 90),
    }.get(scene, (110, 160, 70))

    draw.rectangle(
        [0, 0, width, height],
        fill=sky
    )

    if scene == "night":
        sun_color = (245, 240, 190)
    else:
        sun_color = (255, 220, 80)

    draw.ellipse(
        [
            int(width * 0.74),
            int(height * 0.08),
            int(width * 0.84),
            int(height * 0.18)
        ],
        fill=sun_color
    )

    if scene in ["mountain", "village", "water"]:
        points = [
            (0, int(height * 0.63)),
            (int(width * 0.18), int(height * 0.38)),
            (int(width * 0.32), int(height * 0.62)),
            (int(width * 0.48), int(height * 0.30)),
            (int(width * 0.68), int(height * 0.62)),
            (int(width * 0.84), int(height * 0.40)),
            (width, int(height * 0.63)),
        ]

        draw.polygon(
            points,
            fill=(85, 115, 125)
        )

    draw.rectangle(
        [
            0,
            int(height * 0.62),
            width,
            height
        ],
        fill=ground
    )


def draw_tree(draw, x, y, scale=1.0):
    trunk_w = int(45 * scale)
    trunk_h = int(150 * scale)

    draw.rectangle(
        [x, y, x + trunk_w, y + trunk_h],
        fill=(105, 65, 35)
    )

    for dx, dy, radius in [
        (0, 0, 90),
        (65, -35, 80),
        (-55, -25, 75),
        (30, -85, 70),
    ]:
        draw.ellipse(
            [
                int(x + dx - radius),
                int(y + dy - radius),
                int(x + dx + radius),
                int(y + dy + radius),
            ],
            fill=(40, 135, 60)
        )


def draw_house(draw, width, height):
    x = int(width * 0.12)
    y = int(height * 0.42)

    w = int(width * 0.30)
    h = int(height * 0.25)

    draw.rectangle(
        [x, y, x + w, y + h],
        fill=(225, 165, 105)
    )

    draw.polygon(
        [
            (x - 35, y),
            (x + w // 2, int(y - h * 0.55)),
            (x + w + 35, y),
        ],
        fill=(150, 60, 45)
    )

    draw.rectangle(
        [
            x + int(w * 0.42),
            y + int(h * 0.50),
            x + int(w * 0.62),
            y + h,
        ],
        fill=(90, 60, 45)
    )


def draw_city(draw, width, height):
    for i in range(8):
        x = int(width * (0.02 + i * 0.13))
        h = int(height * (0.20 + (i % 4) * 0.08))

        draw.rectangle(
            [
                x,
                int(height * 0.62) - h,
                x + int(width * 0.09),
                int(height * 0.62),
            ],
            fill=(70, 75, 100)
        )


def draw_school(draw, width, height):
    left = int(width * 0.10)
    top = int(height * 0.36)
    right = int(width * 0.48)
    bottom = int(height * 0.64)

    draw.rectangle(
        [left, top, right, bottom],
        fill=(235, 190, 90)
    )

    draw.polygon(
        [
            (int(width * 0.06), top),
            (int(width * 0.29), int(height * 0.18)),
            (int(width * 0.52), top),
        ],
        fill=(150, 70, 50)
    )

    for i in range(3):
        x = int(width * (0.16 + i * 0.09))

        draw.rectangle(
            [
                x,
                int(height * 0.43),
                x + int(width * 0.05),
                int(height * 0.54),
            ],
            fill=(90, 160, 210)
        )


def draw_palace(draw, width, height):
    left = int(width * 0.18)
    top = int(height * 0.25)
    right = int(width * 0.72)
    bottom = int(height * 0.65)

    draw.rectangle(
        [left, top, right, bottom],
        fill=(220, 185, 105)
    )

    for x in [0.25, 0.42, 0.59]:
        cx = int(width * x)

        draw.rectangle(
            [
                cx,
                int(height * 0.10),
                cx + int(width * 0.07),
                bottom,
            ],
            fill=(205, 170, 90)
        )


def draw_character(draw, width, height, side=0, sad=False):
    if side == 0:
        cx = int(width * 0.62)
    else:
        cx = int(width * 0.76)

    cy = int(height * 0.49)

    # Face
    draw.ellipse(
        [
            cx - 75,
            cy - 185,
            cx + 75,
            cy - 35,
        ],
        fill=(245, 190, 145)
    )

    # Hair
    draw.ellipse(
        [
            cx - 80,
            cy - 205,
            cx + 80,
            cy - 100,
        ],
        fill=(55, 35, 25)
    )

    # Eyes
    draw.ellipse(
        [
            cx - 32,
            cy - 125,
            cx - 12,
            cy - 102,
        ],
        fill=(20, 20, 20)
    )

    draw.ellipse(
        [
            cx + 12,
            cy - 125,
            cx + 32,
            cy - 102,
        ],
        fill=(20, 20, 20)
    )

    shirt = (
        (60, 110, 190)
        if side == 0
        else (190, 75, 80)
    )

    # Body
    draw.rounded_rectangle(
        [
            cx - 90,
            cy - 35,
            cx + 90,
            cy + 200,
        ],
        radius=40,
        fill=shirt
    )

    # Arms
    draw.line(
        [
            cx - 65,
            cy + 5,
            cx - 155,
            cy + 100,
        ],
        fill=shirt,
        width=35
    )

    draw.line(
        [
            cx + 65,
            cy + 5,
            cx + 155,
            cy + 100,
        ],
        fill=shirt,
        width=35
    )

    # Legs
    draw.line(
        [
            cx - 35,
            cy + 190,
            cx - 65,
            cy + 340,
        ],
        fill=(45, 45, 65),
        width=45
    )

    draw.line(
        [
            cx + 35,
            cy + 190,
            cx + 65,
            cy + 340,
        ],
        fill=(45, 45, 65),
        width=45
    )

    # Mouth
    if sad:
        draw.arc(
            [
                cx - 30,
                cy - 75,
                cx + 30,
                cy - 30,
            ],
            200,
            340,
            fill=(80, 20, 20),
            width=8
        )
    else:
        draw.arc(
            [
                cx - 30,
                cy - 75,
                cx + 30,
                cy - 25,
            ],
            20,
            160,
            fill=(80, 20, 20),
            width=8
        )


def create_cartoon_scene(text, index, total, width, height):
    image = Image.new(
        "RGB",
        (width, height),
        (110, 180, 230)
    )

    draw = ImageDraw.Draw(image)

    scene = detect_scene(text)

    draw_background(
        draw,
        width,
        height,
        scene
    )

    if scene in ["forest", "village"]:
        draw_tree(
            draw,
            int(width * 0.08),
            int(height * 0.43),
            1.0
        )

        draw_tree(
            draw,
            int(width * 0.82),
            int(height * 0.41),
            0.9
        )

    if scene == "village":
        draw_house(
            draw,
            width,
            height
        )

    elif scene == "school":
        draw_school(
            draw,
            width,
            height
        )

    elif scene == "city":
        draw_city(
            draw,
            width,
            height
        )

    elif scene == "palace":
        draw_palace(
            draw,
            width,
            height
        )

    sad_words = [
        "दुख",
        "रोया",
        "रोने",
        "आंसू",
        "अकेला",
        "डर",
    ]

    sad = any(
        word in text
        for word in sad_words
    )

    draw_character(
        draw,
        width,
        height,
        side=index % 2,
        sad=sad
    )

    # Cinematic bars
    bar = int(height * 0.055)

    draw.rectangle(
        [0, 0, width, bar],
        fill=(10, 10, 15)
    )

    draw.rectangle(
        [0, height - bar, width, height],
        fill=(10, 10, 15)
    )

    # Scene number
    font = get_font(
        max(28, width // 70)
    )

    draw.text(
        [
            int(width * 0.04),
            int(height * 0.70)
        ],
        f"Scene {index + 1}",
        fill=(255, 255, 255),
        font=font
    )

    scene_file = (
        SCENE_DIR /
        f"scene_{index:03d}.jpg"
    )

    image.save(
        scene_file,
        "JPEG",
        quality=92
    )

    return scene_file


def get_audio_duration(audio_file):
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(audio_file),
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    try:
        return max(
            1.0,
            float(result.stdout.strip())
        )
    except Exception:
        return 60.0


def make_cinematic_video(
    scene_files,
    voice_file,
    output_file,
    width,
    height
):
    if not scene_files:
        return {
            "status": "error",
            "message": "No cartoon scenes were created."
        }

    duration = get_audio_duration(
        voice_file
    )

    scene_duration = 7.0

    required = max(
        1,
        math.ceil(
            duration / scene_duration
        )
    )

    list_file = (
        OUTPUT_DIR /
        "video_list.txt"
    )

    with open(
        list_file,
        "w",
        encoding="utf-8"
    ) as file:

        for i in range(required):
            scene = scene_files[
                i % len(scene_files)
            ]

            absolute_path = str(
                scene.resolve()
            )

            absolute_path = (
                absolute_path.replace(
                    "'",
                    "'\\''"
                )
            )

            file.write(
                f"file '{absolute_path}'\n"
            )

            file.write(
                f"duration {scene_duration}\n"
            )

        # Required by FFmpeg concat demuxer
        last_scene = scene_files[
            (required - 1) % len(scene_files)
        ]

        absolute_path = str(
            last_scene.resolve()
        ).replace(
            "'",
            "'\\''"
        )

        file.write(
            f"file '{absolute_path}'\n"
        )

    command = [
        "ffmpeg",
        "-y",

        "-f",
        "concat",

        "-safe",
        "0",

        "-i",
        str(list_file),

        "-i",
        str(voice_file),

        "-map",
        "0:v:0",

        "-map",
        "1:a:0",

        "-vf",
        (
            f"scale={width}:{height}:"
            "force_original_aspect_ratio=increase,"
            f"crop={width}:{height},"
            "format=yuv420p"
        ),

        "-r",
        "25",

        "-t",
        str(duration),

        "-c:v",
        "libx264",

        "-preset",
        "veryfast",

        "-crf",
        "21",

        "-pix_fmt",
        "yuv420p",

        "-c:a",
        "aac",

        "-b:a",
        "192k",

        "-movflags",
        "+faststart",

        output_file,
    ]

    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True
        )

        return {
            "status": "success",
            "file": output_file,
            "resolution": f"{width}x{height}",
            "duration_seconds": duration,
            "scenes": required,
        }

    except subprocess.CalledProcessError as error:
        return {
            "status": "error",
            "message": error.stderr[-4000:]
        }


def create_thumbnail(
    title,
    output_file="output/thumbnail.jpg"
):
    width = 1280
    height = 720

    image = Image.new(
        "RGB",
        (width, height),
        (45, 80, 135)
    )

    draw = ImageDraw.Draw(image)

    draw.ellipse(
        [850, 60, 1080, 290],
        fill=(255, 215, 90)
    )

    draw_character(
        draw,
        width,
        height,
        side=0
    )

    draw.rectangle(
        [30, 490, 1250, 690],
        fill=(15, 20, 30)
    )

    font = get_font(58)

    short_title = str(title)[:42]

    draw.text(
        [65, 545],
        short_title,
        fill=(255, 255, 255),
        font=font
    )

    image.save(
        output_file,
        "JPEG",
        quality=95
    )

    return {
        "status": "success",
        "file": output_file
    }


def prepare_media(
    script,
    title="Hindi Cartoon Story"
):
    width, height = get_resolution()

    # 1. Hindi voice
    voice = create_voice(
        script,
        "output/voice.mp3"
    )

    if voice.get("status") != "success":
        return {
            "status": "error",
            "voice": voice
        }

    # 2. Story scenes
    story_parts = split_story(
        script,
        maximum=30
    )

    if not story_parts:
        story_parts = [
            title,
            "कहानी की शुरुआत एक छोटे से गांव से होती है।",
            "लेकिन उस दिन कुछ ऐसा हुआ जिसने सबकी जिंदगी बदल दी।",
        ]

    # 3. Cartoon images
    scene_files = []

    for index, part in enumerate(
        story_parts
    ):
        scene = create_cartoon_scene(
            part,
            index,
            len(story_parts),
            width,
            height
        )

        scene_files.append(scene)

    # 4. Video
    video = make_cinematic_video(
        scene_files,
        Path("output/voice.mp3"),
        "output/video.mp4",
        width,
        height
    )

    # 5. Thumbnail
    thumbnail = create_thumbnail(
        title,
        "output/thumbnail.jpg"
    )

    return {
        "status": "success",

        "voice": voice,

        "visual": {
            "status": "success",
            "type": "cinematic_cartoon",
            "scenes": len(scene_files),
            "resolution": f"{width}x{height}",
        },

        "video": video,

        "thumbnail": thumbnail,
}
