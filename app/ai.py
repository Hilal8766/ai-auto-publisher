import json
import requests
from typing import Dict

from .config import settings


SYSTEM_PROMPT = """
You are a professional Hindi YouTube video script writer.

Create ORIGINAL, natural and engaging Hindi content.

The script must be long enough for the requested video duration.

Approximate narration speed:
130 Hindi words per minute.

The script must:
- have a strong opening hook
- be easy to understand
- have a natural storytelling flow
- contain multiple sections
- avoid unnecessary repetition
- end with a natural conclusion
- not copy articles word-for-word
- avoid unsupported claims

Return ONLY valid JSON.

Required JSON keys:
title
script
description
keywords
tags
hashtags
thumbnail_text
"""


def generate_content(
    topic: str,
    language: str = "Hindi",
    duration_minutes: int = 10
) -> Dict:

    if not topic:
        topic = "आज की रोचक कहानी"

    duration_minutes = max(1, int(duration_minutes))

    # लगभग 130 शब्द प्रति मिनट
    target_words = duration_minutes * 130

    api_key = settings.ai_api_key

    # API key नहीं है
    if not api_key:

        return {
            "title": topic,
            "script": (
                f"{topic}\n\n"
                "AI API key अभी connect नहीं की गई है।\n\n"
                f"जब AI API key connect होगी, "
                f"तब लगभग {target_words} शब्दों की "
                f"{duration_minutes} मिनट की पूरी Hindi script "
                "automatically generate होगी।"
            ),
            "description": (
                f"{topic} पर Hindi long-form video."
            ),
            "keywords": [
                "Hindi video",
                "Hindi story",
                "trending",
                "viral video"
            ],
            "tags": [
                "hindi",
                "trending",
                "viral",
                "long video"
            ],
            "hashtags": [
                "#Hindi",
                "#Trending",
                "#Viral",
                "#LongVideo"
            ],
            "thumbnail_text": topic[:45],
            "word_target": target_words,
            "duration_minutes": duration_minutes,
            "api_connected": False
        }

    try:

        user_prompt = f"""
Topic:
{topic}

Language:
{language}

Target duration:
{duration_minutes} minutes

Target script length:
approximately {target_words} Hindi words.

Create the COMPLETE narration script.

Do not give an outline.

Do not give a short summary.

Write the actual narration that can be converted directly into voice.

Structure it with:
1. Strong opening hook
2. Introduction
3. Main story/information
4. Several interesting sections
5. Important details
6. Smooth transitions
7. Conclusion

The final script should be approximately
{target_words} words.
"""

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",

            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },

            json={
                "model": (
                    settings.ai_model
                    or "gpt-5.6-luna"
                ),

                "messages": [
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],

                "temperature": 0.8,

                "max_tokens": min(
                    24000,
                    max(
                        4000,
                        target_words * 3
                    )
                )
            },

            timeout=300
        )

        response.raise_for_status()

        data = response.json()

        content = (
            data["choices"][0]
            ["message"]
            ["content"]
        )

        # कभी-कभी model JSON को ```json ... ``` में देता है
        content = content.strip()

        if content.startswith("```"):
            content = content.replace(
                "```json",
                "",
                1
            )

            if content.endswith("```"):
                content = content[:-3]

            content = content.strip()

        result = json.loads(content)

        # जरूरी fields सुनिश्चित करें
        result.setdefault(
            "title",
            topic
        )

        result.setdefault(
            "script",
            ""
        )

        result.setdefault(
            "description",
            ""
        )

        result.setdefault(
            "keywords",
            []
        )

        result.setdefault(
            "tags",
            []
        )

        result.setdefault(
            "hashtags",
            []
        )

        result.setdefault(
            "thumbnail_text",
            topic[:45]
        )

        result["duration_minutes"] = (
            duration_minutes
        )

        result["target_words"] = (
            target_words
        )

        result["api_connected"] = True

        return result

    except Exception as error:

        return {
            "title": topic,

            "script": (
                f"{topic}\n\n"
                "AI script generation में "
                "temporary error आया है।"
            ),

            "description": "",

            "keywords": [],

            "tags": [],

            "hashtags": [],

            "thumbnail_text": topic[:45],

            "duration_minutes": duration_minutes,

            "target_words": target_words,

            "api_connected": True,

            "error": str(error)
        }
