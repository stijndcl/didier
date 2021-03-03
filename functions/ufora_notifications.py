import feedparser
from data.constants import BotTesting


# TODO when it works, move to announcements channel
notifications_channel = BotTesting


course_urls = {
    "Algoritmen en Datastructuren 2": "https://ufora.ugent.be/d2l/le/news/rss/222018/course?token=aehhv6utkf46t8cc102e0&ou=222018",
    "Communicatienetwerken": "https://ufora.ugent.be/d2l/le/news/rss/221184/course?token=aehhv6utkf46t8cc102e0&ou=221184",
    "Computerarchitectuur": "https://ufora.ugent.be/d2l/le/news/rss/228912/course?token=aehhv6utkf46t8cc102e0&ou=228912",
    "Functioneel Programmeren": "https://ufora.ugent.be/d2l/le/news/rss/236396/course?token=aehhv6utkf46t8cc102e0&ou=236396",
    "Multimedia": "https://ufora.ugent.be/d2l/le/news/rss/236949/course?token=aehhv6utkf46t8cc102e0&ou=236949",
    "Software Engineering Lab 1": "https://ufora.ugent.be/d2l/le/news/rss/235800/course?token=aehhv6utkf46t8cc102e0&ou=235800",
    "Statistiek en Probabiliteit": "https://ufora.ugent.be/d2l/le/news/rss/236398/course?token=aehhv6utkf46t8cc102e0&ou=236398",
    "Systeemprogrammeren": "https://ufora.ugent.be/d2l/le/news/rss/222035/course?token=aehhv6utkf46t8cc102e0&ou=222035",
    "Webdevelopment": "https://ufora.ugent.be/d2l/le/news/rss/223449/course?token=aehhv6utkf46t8cc102e0&ou=223449",
    "Wetenschappelijk Rekenen": "https://ufora.ugent.be/d2l/le/news/rss/236404/course?token=aehhv6utkf46t8cc102e0&ou=236404"
}