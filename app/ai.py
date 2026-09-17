import json
import os
from typing import Dict

from .config import settings


SYSTEM_PROMPT = """
You are an AI content production assistant.

Create original Hindi video content.

The output must include:
1. Video title
2. Full Hindi script
3. Description
4. Keywords
5. Tags
6. Hashtags
7. Thumbnail text

Write naturally and clearly.
Do not copy articles word-for-word.
Avoid unsupported claims.
"""


def generate_content(
    topic: str,
    language: str = "Hindi",
    duration_minutes: int = 10
) -> Dict:

    if not topic:
        topic = "आज की रोचक कहानी"

    # API key is added later through environment variables.
    api_key = settings.ai_api_key

    if not api_key:
        return {
            "title": topic,
            "script": (
                f"{topic}\n\n"
                "यह एक प्रारंभिक स्क्रिप्ट है। "
                "AI API connect करने के बाद "
                "पूरा long-form script automatically "
                "generate होगा।"
            ),
            "description": (
                f"{topic} पर यह वीडियो "
                "जानकारी और मनोरंजन के लिए तैयार किया गया है।"
            ),
            "keywords": [
                "Hindi video",
                "Hindi story",
                "trending",
                "viral video"
            ],
            "tags": [
                "hindi",
                "viral",
                "trending",
                "shorts"
            ],
            "hashtags": [
                "#Hindi",
                "#Trending",
                "#Viral",
                "#Shorts"
            ],
            "thumbnail_text": topic[:45]
        }

    # -----------------------------------------
    # AI provider integration
    # -----------------------------------------
    #
    # यहां actual AI API बाद में connect होगा.
    #
    # अभी हम provider-neutral structure रखते हैं
    # ताकि API key को GitHub code में hard-code
    # न करना पड़े.
    #

    try:

        import requests

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": settings.ai_model or "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Topic: {topic}\n"
                            f"Language: {language}\n"
                            f"Duration: "
                            f"{duration_minutes} minutes\n\n"
                            "Return valid JSON with these keys: "
                            "title, script, description, keywords, "
                            "tags, hashtags, thumbnail_text."
                        )
                    }
                ],
                "temperature": 0.8
            },
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        content = (
            data["choices"][0]
            ["message"]
            ["content"]
        )

        return json.loads(content)

    except Exception as error:

        return {
            "title": topic,
            "script": (
                f"{topic}\n\n"
                "AI generation failed temporarily."
            ),
            "description": "",
            "keywords": [],
            "tags": [],
            "hashtags": [],
            "thumbnail_text": topic[:45],
            "error": str(error)
              }
