from typing import Dict

from .config import settings


def publish_to_youtube(
    video_file: str,
    title: str,
    description: str = "",
    tags=None
) -> Dict:

    tags = tags or []

    if settings.publish_mode != "live":
        return {
            "platform": "youtube",
            "status": "dry_run",
            "message": "YouTube publishing is not enabled yet.",
            "video_file": video_file,
            "title": title
        }

    # YouTube OAuth/API integration will be connected here.
    return {
        "platform": "youtube",
        "status": "pending",
        "message": "YouTube API integration required."
    }


def publish_to_facebook(
    video_file: str,
    title: str,
    description: str = ""
) -> Dict:

    if settings.publish_mode != "live":
        return {
            "platform": "facebook",
            "status": "dry_run",
            "message": "Facebook publishing is not enabled yet.",
            "video_file": video_file,
            "title": title
        }

    # Meta Graph API integration will be connected here.
    return {
        "platform": "facebook",
        "status": "pending",
        "message": "Facebook API integration required."
    }


def publish_to_instagram(
    video_file: str,
    caption: str = ""
) -> Dict:

    if settings.publish_mode != "live":
        return {
            "platform": "instagram",
            "status": "dry_run",
            "message": "Instagram publishing is not enabled yet.",
            "video_file": video_file,
            "caption": caption
        }

    # Instagram Graph API integration will be connected here.
    return {
        "platform": "instagram",
        "status": "pending",
        "message": "Instagram API integration
