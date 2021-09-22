import re

from data.embeds import UforaNotification
import feedparser
import json
from settings import UFORA_TOKEN


course_urls = {
    "Algoritmen en Datastructuren 3": "https://ufora.ugent.be/d2l/le/news/rss/437923/course?token=",
    "Artificiële Intelligentie": "https://ufora.ugent.be/d2l/le/news/rss/439739/course?token=",
    "Automaten, Berekenbaarheid en Complexiteit": "https://ufora.ugent.be/d2l/le/news/rss/439079/course?token=",
    "Besturingssystemen": "https://ufora.ugent.be/d2l/le/news/rss/442814/course?token=",
    "Communicatienetwerken": "https://ufora.ugent.be/d2l/le/news/rss/447014/course?token=",
    "Computationele Biologie": "https://ufora.ugent.be/d2l/le/news/rss/448904/course?token=",
    "Computerarchitectuur": "https://ufora.ugent.be/d2l/le/news/rss/439172/course?token=",
    "Informatiebeveiliging": "https://ufora.ugent.be/d2l/le/news/rss/444476/course?token=",
    "Inleiding tot Telecommunicatie": "https://ufora.ugent.be/d2l/le/news/rss/450232/course?token=",
    "Logisch Programmeren": "https://ufora.ugent.be/d2l/le/news/rss/443368/course?token=",
    "Modelleren en Simuleren": "https://ufora.ugent.be/d2l/le/news/rss/439235/course?token=",
    "Parallelle Computersystemen": "https://ufora.ugent.be/d2l/le/news/rss/449671/course?token=",
    "Software Engineering Lab 2": "https://ufora.ugent.be/d2l/le/news/rss/445170/course?token=",
    "Statistiek en Probabiliteit": "https://ufora.ugent.be/d2l/le/news/rss/445169/course?token=",
    "Wetenschappelijk Rekenen": "https://ufora.ugent.be/d2l/le/news/rss/445174/course?token=",
    "Wiskundige Modellering": "https://ufora.ugent.be/d2l/le/news/rss/446530/course?token="
}


def run():
    """
    Check for new notifications
    """
    # List of new notifications
    new_notifications = []

    # List of old notifications
    with open("files/ufora_notifications.json", "r") as fp:
        notifications = json.load(fp)

    for course, url in course_urls.items():
        # Automatically append new/missing courses
        if course not in notifications:
            notifications[course] = []

        # Get the updated feed
        feed = feedparser.parse(f"{url}{UFORA_TOKEN}")

        # Filter out old notifications
        feed = list(filter(lambda f: _parse_ids(f["id"])[0] not in notifications[course], feed.entries))

        if feed:
            for item in feed:
                notif_id, course_id = _parse_ids(item["id"])
                new_notifications.append(UforaNotification(item, course, notif_id, course_id))

                notifications[course].append(notif_id)

    # Update list of notifications
    if new_notifications:
        with open("files/ufora_notifications.json", "w") as fp:
            json.dump(notifications, fp)

    return new_notifications


def _parse_ids(url: str):
    match = re.search(r"[0-9]+-[0-9]+$", url)

    if not match:
        return None, None

    spl = match[0].split("-")

    return spl[0], spl[1]
