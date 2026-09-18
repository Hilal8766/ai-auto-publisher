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


def create_voice(text, output_file="output/voice.mp3"):
    if not text:
        return {"status": "error", "message": "Script is empty."}

    if edge_tts is None:
        return {"status": "error", "message": "edge-tts is not installed."}

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    async def generate():
        voice = "hi-IN-SwaraNeural"
        communicator = edge_tts.Communicate(
            text=text,
            voice=voice
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

    parts = [p.strip() for p in parts if len(p.strip()) > 20]

    if len(parts) <= maximum:
        return parts

    step = max(1, len(parts) // maximum)

    scenes = []

    for i in range(0, len(parts), step):
        chunk = " ".join(parts[i:i + step])
        scenes.append(chunk)

        if len(scenes) >= maximum:
            break

    return scenes


def detect_scene(text):
    t = text.lower()

    if any(x in t for x in ["जंगल", "वन", "पेड़", "जानवर", "शेर", "भालू"]):
        return "forest"

    if any(x in t for x in ["गांव", "गाँव", "किसान", "खेत", "मिट्टी"]):
        return "village"

    if any(x in t for x in ["शहर", "बाजार", "सड़क", "कार", "बस"]):
        return "city"

    if any(x in t for x in ["रात", "अंधेरा", "भूत", "डर", "रहस्य"]):
        return "night"

    if any(x in t for x in ["स्कूल", "पढ़ाई", "किताब", "मास्टर"]):
        return "school"

    if any(x in t for x in ["महल", "राजा", "रानी", "राजकुमार"]):
        return "palace"

    if any(x in t for x in ["नदी", "समुद्र", "तालाब", "बारिश"]):
        return "water"

    if any(x in t for x in ["पहाड़", "पर्वत", "सफर", "यात्रा"]):
        return "mountain"

    return "village"


def draw_background(draw, width, height, scene):
    sky = {
        "forest": (105, 180, 225),
        "village": (120, 190, 235),
        "city": (125, 175, 220),
        "night": (25, 35, 75),
        "school": (120, 190, 230),
        "palace": (120, 175, 225),
        "water": (105, 190, 225),
        "mountain": (130, 195, 235),
    }.get(scene, (120, 190, 235))

    draw.rectangle([0, 0, width, height], fill=sky)

    # Sun / moon
    if scene == "night":
        draw.ellipse(
            [width * .72, height * .10,
             width * .82, height * .20],
            fill=(245, 240, 190)
        )
    else:
        draw.ellipse(
            [width * .72, height * .10,
             width * .82, height * .20],
            fill=(255, 220, 80)
        )

    # Ground
    ground = {
        "forest": (55, 125, 65),
        "village": (110, 155, 65),
        "city": (75, 80, 85),
        "night": (35, 50, 45),
        "school": (100, 150, 75),
        "palace": (110, 145, 75),
        "water": (45, 130, 170),
        "mountain": (80, 125, 90),
    }.get(scene, (100, 150, 75))

    draw.rectangle(
        [0, height * .62, width, height],
        fill=ground
    )

    # Mountains
    if scene in ["mountain", "village", "water"]:
        points = [
            (0, height * .62),
            (width * .18, height * .38),
            (width * .32, height * .60),
            (width * .48, height * .30),
            (width * .68, height * .60),
            (width * .84, height * .40),
            (width, height * .62),
        ]
        draw.polygon(points, fill=(85, 115, 125))


def draw_tree(draw, x, y, scale=1.0):
    trunk_w = int(35 * scale)
    trunk_h = int(130 * scale)

    draw.rectangle(
        [x, y, x + trunk_w, y + trunk_h],
        fill=(105, 65, 35)
    )

    for dx, dy, r in [
        (0, 0, 80),
        (55, -30, 75),
        (-45, -20, 70),
        (30, -75, 65),
    ]:
        draw.ellipse(
            [
                x + dx - r,
                y + dy - r,
                x + dx + r,
                y + dy + r
            ],
            fill=(40, 130, 60)
        )


def draw_house(draw, width, height):
    x = width * .15
    y = height * .42
    w = width * .28
    h = height * .25

    draw.rectangle(
        [x, y, x + w, y + h],
        fill=(225, 165, 105)
    )

    draw.polygon(
        [
            (x - 30, y),
            (x + w / 2, y - h * .55),
            (x + w + 30, y)
        ],
        fill=(150, 60, 45)
    )

    draw.rectangle(
        [x + w * .42, y + h * .52,
         x + w * .62, y + h],
        fill=(90, 60, 45)
    )


def draw_character(draw, width, height, side=0, emotion="happy"):
    cx = width * (0.58 if side == 0 else 0.72)
    cy = height * .50

    # Body
    draw.ellipse(
        [cx - 65, cy - 160, cx + 65, cy - 30],
        fill=(245, 190, 145)
    )

    # Hair
    draw.ellipse(
        [cx - 70, cy - 180, cx + 70, cy - 85],
        fill=(55, 35, 25)
    )

    # Eyes
    draw.ellipse(
        [cx - 30, cy - 115, cx - 12, cy - 95],
        fill=(20, 20, 20)
    )
    draw.ellipse(
        [cx + 12, cy - 115, cx + 30, cy - 95],
        fill=(20, 20, 20)
    )

    # Mouth / emotion
    if emotion == "sad":
        draw.arc(
            [cx - 25, cy - 70, cx + 25, cy - 35],
            200, 340,
            fill=(70, 20, 20),
            width=8
        )
    else:
        draw.arc(
            [cx - 25, cy - 70, cx + 25, cy - 30],
            20, 160,
            fill=(70, 20, 20),
            width=8
        )

    # Shirt
    shirt = (60, 110, 190) if side == 0 else (190, 75, 80)

    draw.rounded_rectangle(
        [cx - 85, cy - 35, cx + 85, cy + 190],
        radius=35,
        fill=shirt
    )

    # Arms
    draw.line(
        [cx - 65, cy + 10, cx - 145, cy + 90],
        fill=shirt,
        width=30
    )

    draw.line(
        [cx + 65, cy + 10, cx + 145, cy + 90],
        fill=shirt,
        width=30
    )

    # Legs
    draw.line(
        [cx - 35, cy + 185, cx - 60, cy + 330],
        fill=(45, 45, 65),
        width=40
    )

    draw.line(
        [cx + 35, cy + 185, cx + 60, cy + 330],
        fill=(45, 45, 65),
        width=40
    )


def create_cartoon_scene(text, index, total, width, height):
    image = Image.new("RGB", (width, height), (100, 170, 220))
    draw = ImageDraw.Draw(image)

    scene = detect_scene(text)

    draw_background(draw, width, height, scene)

    if scene in ["forest", "village"]:
        draw_tree(draw, int(width * .08), int(height * .43), 1.0)
        draw_tree(draw, int(width * .82), int(height * .40), .9)

    if scene == "village":
        draw_house(draw, width, height)

    if scene == "school":
        draw.rectangle(
            [width * .10, height * .35,
             width * .48, height * .63],
            fill=(235, 190, 90)
        )
        draw.polygon(
            [
                (width * .07, height * .35),
                (width * .29, height * .18),
                (width * .51, height * .35)
            ],
            fill=(150, 70, 50)
        )

    if scene == "palace":
        draw.rectangle(
            [width * .18, height * .25,
             width * .70, height * .65],
            fill=(220, 185, 105)
        )
        for x in [0.25, 0.42, 0.59]:
            draw.rectangle(
                [width * x, height * .08,
                 width * (x + .08), height * .65],
                fill=(205, 170, 90)
            )

    if scene == "city":
        for i in range(7):
            x = int(width * (.03 + i * .14))
            h = int(height * (.18 + (i % 3) * .08))
            draw.rectangle(
                [x, height * .62 - h,
                 x + width * .09, height * .62],
                fill=(75, 80, 105)
            )

    draw_character(
        draw,
        width,
        height,
        side=index % 2,
        emotion="sad" if "दुख" in text or "रो" in text else "happy"
    )

    # Cinematic title/subtitle
    font = get_font(max(32, width // 55))

    words = text[:100]

    # translucent-like dark panel
    draw.rectangle(
        [width * .04, height * .78,
         width * .96, height * .94],
        fill=(20, 25, 35)
    )

    draw.text(
        (width * .06, height * .80),
        words,
        fill=(255, 255, 255),
        font=font
    )

    scene_file = SCENE_DIR / f"scene_{index:03d}.jpg"
    image.save(scene_file, quality=92)

    return scene_file


def get_audio_duration(audio_file):
    command = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio_file)
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    try:
        return float(result.stdout.strip())
    except Exception:
        return 60.0


def make_cinematic_video(scene_files, voice_file, output_file, width, height):
    if not scene_files:
        return {
            "status": "error",
            "message": "No cartoon scenes were created."
        }

    duration = get_audio_duration(voice_file)

    # 7 seconds per scene
    scene_duration = 7

    inputs = []
    filters = []

    for i, scene in enumerate(scene_files):
        inputs.extend(["-loop", "1", "-i", str(scene)])

        zoom = 1.0 + (0.0008 * ((i % 5) + 1))

        filters.append(
            f"[{i}:v]"
            f"scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},"
            f"zoompan="
            f"z='min(zoom+{zoom-1:.5f},1.12)':"
            f"d={scene_duration * 25}:"
            f"s={width}x{height}:"
            f"fps=25,"
            f"fade=t=in:st=0:d=0.25,"
            f"fade=t=out:st={scene_duration-0.3}:d=0.3,"
            f"setpts=PTS-STARTPTS"
            f"[v{i}]"
        )

    concat_inputs = "".join(f"[v{i}]" for i in range(len(scene_files)))

    filters.append(
        f"{concat_inputs}"
        f"concat=n={len(scene_files)}:v=1:a=0,"
        f"setpts=PTS-STARTPTS,"
        f"tpad=stop_mode=clone:stop_duration={duration}"
        f"[video]"
    )

    filter_complex = ";".join(filters)

    command = [
        "ffmpeg",
        "-y",
        *inputs,
        "-i", str(voice_file),
        "-filter_complex", filter_complex,
        "-map", "[video]",
        "-map", f"{len(scene_files)}:a",
        "-t", str(duration),
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        output_file
    ]

    try:
        subprocess.run(
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
            "scenes": len(scene_files)
        }

    except subprocess.CalledProcessError as error:
        return {
            "status": "error",
            "message": error.stderr[-3000:]
        }


def create_thumbnail(title, output_file="output/thumbnail.jpg"):
    width, height = 1280, 720

    image = Image.new(
        "RGB",
        (width, height),
        (35, 70, 120)
    )

    draw = ImageDraw.Draw(image)

    draw.ellipse(
        [850, 80, 1120, 350],
        fill=(255, 210, 80)
    )

    draw_character(
        draw,
        width,
        height,
        side=0,
        emotion="happy"
    )

    font = get_font(70)

    title = title[:45]

    draw.rectangle(
        [40, 500, 1240, 680],
        fill=(15, 20, 30)
    )

    draw.text(
        (70, 535),
        title,
        fill=(255, 255, 255),
        font=font
    )

    image.save(output_file, quality=95)

    return {
        "status": "success",
        "file": output_file
    }


def prepare_media(script, title="Hindi Cartoon Story"):
    width, height = get_resolution()

    # Voice
    voice = create_voice(
        script,
        "output/voice.mp3"
    )

    if voice.get("status") != "success":
        return {
            "status": "error",
            "voice": voice
        }

    # Story scenes
    story_parts = split_story(
        script,
        maximum=30
    )

    if not story_parts:
        story_parts = [
            title,
            "कहानी की शुरुआत एक छोटे से गांव से होती है।",
            "लेकिन आगे एक बड़ा रहस्य सामने आने वाला था।"
        ]

    scene_files = []

    for index, part in enumerate(story_parts):
        scene = create_cartoon_scene(
            part,
            index,
            len(story_parts),
            width,
            height
        )
        scene_files.append(scene)

    # Video
    video = make_cinematic_video(
        scene_files,
        Path("output/voice.mp3"),
        "output/video.mp4",
        width,
        height
    )

    # Thumbnail
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
            "resolution": f"{width}x{height}"
        },
        "video": video,
        "thumbnail": thumbnail
    }
