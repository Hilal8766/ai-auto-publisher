import feedparser
from urllib.parse import quote


def search_trending_topics(
    language="Hindi",
    country="IN",
    limit=10
):
    """
    Google News RSS से हाल के topics खोजता है.
    """

    query = quote(
        "viral OR trending OR latest news OR interesting"
    )

    url = (
        "https://news.google.com/rss/search?"
        f"q={query}&hl=hi&gl={country}&ceid={country}:hi"
    )

    feed = feedparser.parse(url)

    topics = []

    for entry in feed.entries[:limit]:

        title = getattr(
            entry,
            "title",
            ""
        ).strip()

        link = getattr(
            entry,
            "link",
            ""
        )

        published = getattr(
            entry,
            "published",
            ""
        )

        if not title:
            continue

        topics.append(
            {
                "title": title,
                "url": link,
                "published": published,
                "language": language
            }
        )

    return topics


def choose_topic(
    language="Hindi"
):
    """
    सबसे पहला उपलब्ध topic चुनता है.
    आगे चलकर इसमें AI-based viral scoring जोड़ा जाएगा.
    """

    topics = search_trending_topics(
        language=language,
        limit=10
    )

    if not topics:
        return {
            "title": "आज की रोचक कहानी",
            "url": "",
            "published": "",
            "language": language
        }

    return topics[0]
