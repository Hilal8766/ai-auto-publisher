import json
import requests
from typing import Dict

from .config import settings


SYSTEM_PROMPT = """
You are a professional Hindi YouTube video script writer.

Create original, natural and engaging Hindi content.

The script must be long enough for the requested video duration.

Approximate narration speed:
130 Hindi words per minute.

The script must:
- start with a strong hook
- be easy to understand
- have a natural storytelling flow
- contain multiple sections
- avoid unnecessary repetition
- end naturally
- avoid unsupported claims
- not copy articles word-for-word

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
    target_words = duration_minutes * 130

    api_key = settings.ai_api_key

    if not api_key:
        return {
            "title": topic,
            "script": (
                f"{topic}\n\n"
                "AI API key अभी connect नहीं की गई है।"
            ),
            "description": f"{topic} पर Hindi video.",
            "keywords": ["Hindi video", "trending", "viral"],
            "tags": ["hindi", "trending", "viral"],
            "hashtags": ["#Hindi", "#Trending", "#Viral"],
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

Write the COMPLETE narration script.

Do not give an outline.
Do not give a short summary.

Write the actual narration that can be converted directly into voice.

Structure:
1. Strong opening hook
2. Introduction
3. Main story/information
4. Several interesting sections
5. Important details
6. Smooth transitions
7. Conclusion

Return ONLY valid JSON with these keys:
title
script
description
keywords
tags
hashtags
thumbnail_text

The script should be approximately {target_words} Hindi words.
"""

        response = requests.post(
            "https://api.openai.com/v1/responses",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": settings.ai_model or "gpt-5.6-luna",
                "instructions": SYSTEM_PROMPT,
                "input": user_prompt,
                "max_output_tokens": min(
                    24000,
                    max(4000, target_words * 3)
                )
            },
            timeout=300
        )

        response.raise_for_status()

        data = response.json()

        content = data.get("output_text", "")

        if not content:
            for item in data.get("output", []):
                for part in item.get("content", []):
                    if part.get("type") == "output_text":
                        content += part.get("text", "")

        content = content.strip()

        if content.startswith("```"):
            content = content.replace("```json", "", 1)

            if content.endswith("```"):
                content = content[:-3]

            content = content.strip()

        result = json.loads(content)

        result.setdefault("title", topic)
        result.setdefault("script", "")
        result.setdefault("description", "")
        result.setdefault("keywords", [])
        result.setdefault("tags", [])
        result.setdefault("hashtags", [])
        result.setdefault("thumbnail_text", topic[:45])

        result["duration_minutes"] = duration_minutes
        result["target_words"] = target_words
        result["api_connected"] = True

        return result

    except Exception as error:
        return {
            "title": topic,
            "script": f"{topic}\n\nAI script generation में temporary error आया है।",
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
