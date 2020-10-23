from functions.database import remind


class Reminders:
    def __init__(self):
        rows = remind.getAllRows()

        self._nightlyUsers = [int(user[0]) for user in rows if user[1]]
        self._nightlyMessages = ["Dagelijkse herinnering om Didier Nightly te doen.", "Vrees niet, Nightly-streak-liefhebber! 't Zenne kik, Didier, me ne reminder!"]
        self.nightly = {"users": self._nightlyUsers, "messages": self._nightlyMessages}

        self._les = [int(user[0]) for user in rows if user[2]]
        self._lesMessages = ["Lessenrooster voor vandaag:"]
        self.les = {"users": self._les, "messages": self._lesMessages, "embed": None}

        self.categories = [self.nightly, self.les]
