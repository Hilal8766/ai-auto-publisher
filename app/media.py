def make_cinematic_video(
    scene_files,
    audio_file,
    output_file,
    width,
    height
):
    """
    Create a cinematic animated-cartoon montage from scene images.

    Each scene gets:
    - slow camera movement
    - zoom in / zoom out
    - left/right pan
    - fade in/out
    - cinematic transitions

    Hindi narration is added as the final audio.
    """

    import subprocess
    import math
    from pathlib import Path

    if not scene_files:
        return {
            "status": "error",
            "message": "No cartoon scenes found."
        }

    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    temp_dir = Path("output/animated_clips")
    temp_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------
    # Get narration duration
    # -------------------------------------------------

    duration_cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio_file)
    ]

    try:
        result = subprocess.run(
            duration_cmd,
            capture_output=True,
            text=True,
            check=True
        )

        total_duration = float(result.stdout.strip())

    except Exception:
        total_duration = max(
            8,
            len(scene_files) * 7
        )

    # -------------------------------------------------
    # Repeat scenes if story is long
    # -------------------------------------------------

    minimum_scene_time = 6.0

    scene_count = max(
        len(scene_files),
        math.ceil(total_duration / minimum_scene_time)
    )

    selected_scenes = []

    for i in range(scene_count):
        selected_scenes.append(
            scene_files[i % len(scene_files)]
        )

    scene_duration = total_duration / len(selected_scenes)

    clip_files = []

    # -------------------------------------------------
    # Create animated clip for every scene
    # -------------------------------------------------

    for index, scene_file in enumerate(selected_scenes):

        clip_file = temp_dir / f"scene_{index:03d}.mp4"

        # Alternate camera directions
        if index % 4 == 0:
            zoom_expr = (
                "zoom+0.0007"
            )
            x_expr = (
                "iw/2-(iw/zoom/2)"
            )
            y_expr = (
                "ih/2-(ih/zoom/2)"
            )

        elif index % 4 == 1:
            zoom_expr = (
                "zoom-0.0005"
            )
            x_expr = (
                "(iw-iw/zoom)*on/FRAME"
            )
            y_expr = (
                "ih/2-(ih/zoom/2)"
            )

        elif index % 4 == 2:
            zoom_expr = (
                "zoom+0.0006"
            )
            x_expr = (
                "(iw-iw/zoom)*(1-on/FRAME)"
            )
            y_expr = (
                "(ih-ih/zoom)/2"
            )

        else:
            zoom_expr = (
                "zoom-0.0004"
            )
            x_expr = (
                "iw/2-(iw/zoom/2)"
            )
            y_expr = (
                "(ih-ih/zoom)*on/FRAME"
            )

        frames = max(
            1,
            int(scene_duration * 30)
        )

        fade_time = min(
            0.7,
            scene_duration / 4
        )

        filter_complex = (
            f"scale={width}:{height}:"
            f"force_original_aspect_ratio=increase,"
            f"crop={width}:{height},"
            f"zoompan="
            f"z='{zoom_expr}':"
            f"x='{x_expr}':"
            f"y='{y_expr}':"
            f"d={frames}:"
            f"s={width}x{height}:"
            f"fps=30,"
            f"fade=t=in:st=0:d={fade_time},"
            f"fade=t=out:"
            f"st={max(0, scene_duration-fade_time)}:"
            f"d={fade_time}"
        )

        command = [
            "ffmpeg",
            "-y",
            "-loop", "1",
            "-i", str(scene_file),

            "-t", str(scene_duration),

            "-vf", filter_complex,

            "-an",

            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "20",
            "-pix_fmt", "yuv420p",

            str(clip_file)
        ]

        try:
            subprocess.run(
                command,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE
            )

            clip_files.append(
                str(clip_file)
            )

        except subprocess.CalledProcessError as error:
            return {
                "status": "error",
                "message": (
                    "Failed to create animated scene."
                ),
                "scene": index,
                "error": error.stderr.decode(
                    "utf-8",
                    errors="ignore"
                )[-2000:]
            }

    # -------------------------------------------------
    # Create concat list
    # -------------------------------------------------

    concat_file = temp_dir / "concat.txt"

    with open(
        concat_file,
        "w",
        encoding="utf-8"
    ) as file:

        for clip in clip_files:
            safe_path = str(
                Path(clip).resolve()
            ).replace("'", "'\\''")

            file.write(
                f"file '{safe_path}'\n"
            )

    # -------------------------------------------------
    # Join all animated scenes
    # -------------------------------------------------

    silent_video = temp_dir / "silent_video.mp4"

    concat_command = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),

        "-c", "copy",

        str(silent_video)
    ]

    try:
        subprocess.run(
            concat_command,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE
        )

    except subprocess.CalledProcessError as error:
        return {
            "status": "error",
            "message": "Failed to join cartoon scenes.",
            "error": error.stderr.decode(
                "utf-8",
                errors="ignore"
            )[-2000:]
        }

    # -------------------------------------------------
    # Add Hindi narration
    # -------------------------------------------------

    final_command = [
        "ffmpeg",
        "-y",

        "-i", str(silent_video),
        "-i", str(audio_file),

        "-map", "0:v:0",
        "-map", "1:a:0",

        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "20",

        "-c:a", "aac",
        "-b:a", "192k",

        "-shortest",

        "-movflags", "+faststart",

        str(output_file)
    ]

    try:
        subprocess.run(
            final_command,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE
        )

    except subprocess.CalledProcessError as error:
        return {
            "status": "error",
            "message": "Failed to add Hindi voice.",
            "error": error.stderr.decode(
                "utf-8",
                errors="ignore"
            )[-2000:]
        }

    return {
        "status": "success",
        "file": output_file,
        "duration": round(total_duration, 2),
        "scenes": len(selected_scenes),
        "resolution": f"{width}x{height}",
        "animation": "cinematic_camera_motion"
    }
