import os
from dataclasses import dataclass


@dataclass
class Settings:

    app_name: str = os.getenv(
        "APP_NAME",
        "AI Auto Publisher"
    )

    host: str = os.getenv(
        "HOST",
        "0.0.0.0"
    )

    port: int = int(
        os.getenv(
            "PORT",
            "8000"
        )
    )

    timezone: str = os.getenv(
        "TIMEZONE",
        "Asia/Kolkata"
    )

    daily_hour: int = int(
        os.getenv(
            "DAILY_HOUR",
            "10"
        )
    )

    daily_minute: int = int(
        os.getenv(
            "DAILY_MINUTE",
            "0"
        )
    )

    ai_api_key: str = os.getenv(
        "AI_API_KEY",
        ""
    )

    ai_model: str = os.getenv(
        "AI_MODEL",
        ""
    )

    tts_api_key: str = os.getenv(
        "TTS_API_KEY",
        ""
    )

    media_api_key: str = os.getenv(
        "MEDIA_API_KEY",
        ""
    )

    youtube_client_id: str = os.getenv(
        "YOUTUBE_CLIENT_ID",
        ""
    )

    youtube_client_secret: str = os.getenv(
        "YOUTUBE_CLIENT_SECRET",
        ""
    )

    facebook_page_id: str = os.getenv(
        "FACEBOOK_PAGE_ID",
        ""
    )

    facebook_access_token: str = os.getenv(
        "FACEBOOK_ACCESS_TOKEN",
        ""
    )

    instagram_account_id: str = os.getenv(
        "INSTAGRAM_ACCOUNT_ID",
        ""
    )

    publish_mode: str = os.getenv(
        "PUBLISH_MODE",
        "dry_run"
    )


settings = Settings()
