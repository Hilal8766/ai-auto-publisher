from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from apscheduler.schedulers.background import BackgroundScheduler

from .config import settings
from .models import VideoJob
from .pipeline import run_pipeline


app = FastAPI(
    title="AI Auto Publisher",
    description="Personal AI video automation system"
)

scheduler = BackgroundScheduler(
    timezone=settings.timezone
)


# -----------------------------------
# DAILY AUTOMATION
# -----------------------------------

def daily_video_job():
    print("Starting daily AI video job...")

    result = run_pipeline(
        topic=None,
        profile="long",
        language="Hindi",
        duration_minutes=10
    )

    print("Daily job finished:", result)


# -----------------------------------
# START APPLICATION
# -----------------------------------

@app.on_event("startup")
def startup_event():

    scheduler.add_job(
        daily_video_job,
        "cron",
        hour=settings.daily_hour,
        minute=settings.daily_minute,
        id="daily_ai_video",
        replace_existing=True
    )

    scheduler.start()

    print("AI Auto Publisher started")
    print(
        f"Daily video time: "
        f"{settings.daily_hour:02d}:"
        f"{settings.daily_minute:02d}"
    )


# -----------------------------------
# STOP APPLICATION
# -----------------------------------

@app.on_event("shutdown")
def shutdown_event():

    if scheduler.running:
        scheduler.shutdown(wait=False)


# -----------------------------------
# DASHBOARD
# -----------------------------------

@app.get("/", response_class=HTMLResponse)
def dashboard():

    return """
    <!DOCTYPE html>

    <html>
    <head>

        <meta name="viewport"
              content="width=device-width, initial-scale=1">

        <title>AI Auto Publisher</title>

        <style>

            body {
                font-family: Arial, sans-serif;
                background: #f5f5f5;
                margin: 0;
                padding: 20px;
            }

            .container {
                max-width: 900px;
                margin: auto;
            }

            .card {
                background: white;
                padding: 20px;
                margin-bottom: 15px;
                border-radius: 15px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            }

            h1 {
                margin-top: 0;
            }

            .status {
                font-size: 18px;
                font-weight: bold;
            }

        </style>

    </head>

    <body>

        <div class="container">

            <div class="card">

                <h1>
                    🤖 AI Auto Publisher
                </h1>

                <p>
                    Personal automatic video system
                </p>

            </div>


            <div class="card">

                <h2>⚙️ Automation</h2>

                <p>
                    🔎 Trending Topic Research
                </p>

                <p>
                    📝 AI Script
                </p>

                <p>
                    🎙️ AI Voice
                </p>

                <p>
                    🎬 Long Video + Shorts
                </p>

                <p>
                    🖼️ Automatic Thumbnail
                </p>

                <p>
                    ✍️ Title + Description + Keywords + Tags
                </p>

                <p>
                    📤 YouTube + Facebook + Instagram
                </p>

                <p>
                    📊 Analytics
                </p>

            </div>


            <div class="card">

                <h2>⏰ Daily Schedule</h2>

                <p>
                    The automatic daily job is configured
                    in the application settings.
                </p>

            </div>


            <div class="card">

                <h2>📹 Production Flow</h2>

                <p class="status">
                    Research →
                    Script →
                    Voice →
                    Video →
                    Thumbnail →
                    SEO →
                    Publish
                </p>

            </div>

        </div>

    </body>

    </html>
    """


# -----------------------------------
# MANUAL JOB
# -----------------------------------

@app.post("/jobs/run")
def run_video(job: VideoJob):

    result = run_pipeline(
        topic=job.topic,
        profile=job.profile,
        language=job.language,
        duration_minutes=job.duration_minutes
    )

    return result


# -----------------------------------
# RUN SERVER
# -----------------------------------

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port
    )
