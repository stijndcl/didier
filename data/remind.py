from data import schedule
from functions import les, config
from functions.database import remind


class Reminders:
    def __init__(self):
        rows = remind.getAllRows()

        self._nightlyUsers = [int(user[0]) for user in rows if user[1]]
        self._nightlyMessages = ["Dagelijkse herinnering om Didier Nightly te doen.", "Vrees niet, Nightly-streak-liefhebber! 't Zenne kik, Didier, me ne reminder!"]
        self.nightly = {"users": self._nightlyUsers, "messages": self._nightlyMessages, "weekends": True, "disabled": False}

        self._les = [int(user[0]) for user in rows if user[2]]
        self._lesMessages = ["Lessenrooster voor vandaag:"]
        self.les = {"users": self._les, "messages": self._lesMessages, "embed": self.lesEmbed, "weekends": False, "disabled": True}

        self.categories = [self.nightly, self.les]

    def lesEmbed(self):
        dt = les.find_target_date()
        s = schedule.Schedule(dt, int(config.get("year")), int(config.get("semester")))
        return s.create_schedule().to_embed()
