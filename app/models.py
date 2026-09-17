from pydantic import BaseModel, Field
from typing import Optional


class VideoJob(BaseModel):

    topic: Optional[str] = Field(
        default=None,
        description="Video topic. If empty, the AI will research a topic."
    )

    profile: str = Field(
        default="long",
        description="Video type: long or short"
    )

    language: str = Field(
        default="Hindi",
        description="Video language"
    )

    duration_minutes: int = Field(
        default=10,
        ge=1,
        le=180,
        description="Target video duration in minutes"
    )
