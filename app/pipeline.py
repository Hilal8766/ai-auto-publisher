from .research import choose_topic
from .ai import generate_content
from .media import prepare_media


def run_pipeline(
    topic=None,
    profile="long",
    language="Hindi",
    duration_minutes=10
):
    """
    Complete AI video production pipeline.

    Flow:
    Research
       ↓
    Topic
       ↓
    AI Script + SEO
       ↓
    Voice
       ↓
    Thumbnail
       ↓
    Video preparation
    """

    # 1. Research topic
    if not topic:
        selected_topic = choose_topic(
            language=language
        )

        topic = selected_topic["title"]

    else:
        selected_topic = {
            "title": topic,
            "url": "",
            "published": "",
            "language": language
        }

    # 2. Generate AI content
    content = generate_content(
        topic=topic,
        language=language,
        duration_minutes=duration_minutes
    )

    # 3. Prepare media
    media = prepare_media(
        script=content.get("script", ""),
        title=content.get("title", topic)
    )

    # 4. Return complete job result
    return {
        "status": "success",

        "topic": selected_topic,

        "content": content,

        "media": media,

        "profile": profile,

        "language": language,

        "duration_minutes": duration_minutes
  }
