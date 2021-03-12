from data import constants
from data.remind import Reminders
from discord.ext import commands, tasks
from enums.numbers import Numbers
from functions import timeFormatters
from functions.config import config
from functions.database import currency, poke, prison, birthdays, stats
from functions.scraping import getMatchweek
from functions import ufora_notifications
import json
import random
import requests
import time


class Tasks(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.bankInterest.start()
        self.resetPrison.start()
        self.resetLost.start()
        # self.resetPoke.start()
        self.checkBirthdays.start()
        self.updateMessageCounts.start()
        self.sendReminders.start()
        self.updateMatchweek.start()
        self.uforaAnnouncements.start()

    @tasks.loop(hours=1.0)
    async def bankInterest(self):
        """
        Task that gives daily interest
        """
        # Don't do it multiple times a day if bot dc's, ...
        with open("files/lastTasks.json", "r") as fp:
            lastTasks = json.load(fp)
        if int(self.getCurrentHour()) == 0 and int(time.time()) - int(lastTasks["interest"]) > 10000:
            users = currency.getAllRows()
            bitcoinPrice = self.getCurrentBitcoinPrice()
            for user in users:
                # People in prison don't get interest
                if len(prison.getUser(int(user[0]))) != 0:
                    continue

                if float(user[3]) != 0.0:
                    currency.update(user[0], "investeddays", int(user[4]) + 1)
                    profit = ((float(user[3]) + float(user[5])) * (1 + (float(user[2]) * 0.01))) - float(user[3])
                    # Can't exceed 1 quadrillion
                    # Check BC as well so they can't put everything into BC to cheat the system
                    if float(user[1]) + float(user[3]) + float(user[5]) + profit + (float(user[8]) * bitcoinPrice) > Numbers.q.value:
                        # In case adding profit would exceed 1q, only add the difference
                        profit = Numbers.q.value - float(user[1]) - float(user[3]) - float(user[5]) - (float(user[8]) * bitcoinPrice)
                        # Don't reduce the current profit if Dinks were gained some other way (rob, bc, ...)
                        if profit > 0:
                            currency.update(user[0], "profit", float(user[5]) + profit)

                            await self.client.get_user(int(user[0])).send("Je hebt de invest-limiet van 1Q Didier Dinks bereikt.\nIndien je nog meer Didier Dinks wil sparen, kan je 1q Didier Dinks omruilen voor een Platinum Dink in de shop.")

                    else:
                        currency.update(user[0], "profit", float(user[5]) + profit)
            lastTasks["interest"] = int(round(time.time()))
            with open("files/lastTasks.json", "w") as fp:
                json.dump(lastTasks, fp)

    @bankInterest.before_loop
    async def beforeBankInterest(self):
        await self.client.wait_until_ready()

    @tasks.loop(hours=1.0)
    async def resetLost(self):
        """
        Task that resets Lost Today
        """
        # Don't do it multiple times a day if bot dc's, ...
        with open("files/lastTasks.json", "r") as fp:
            lastTasks = json.load(fp)

        if int(self.getCurrentHour()) == 0 and int(time.time()) - int(lastTasks["lost"]) > 10000:
            with open("files/lost.json", "r") as fp:
                fc = json.load(fp)
            fc["today"] = 0
            with open("files/lost.json", "w") as fp:
                json.dump(fc, fp)

            lastTasks["lost"] = round(time.time())
            with open("files/lastTasks.json", "w") as fp:
                json.dump(lastTasks, fp)

    @resetLost.before_loop
    async def beforeResetLost(self):
        await self.client.wait_until_ready()

    @tasks.loop(hours=6.0)
    async def resetPoke(self):
        """
        Task that resets Poke
        """
        if int(time.time()) - int(poke.get()[1]) > 259200:
            await self.client.get_guild(int(self.client.constants.CallOfCode))\
                .get_channel(int(self.client.constants.DidierPosting))\
                .send("Poke is gereset door inactiviteit. <@!{}> is hem!".format(int(poke.reset())))

    @resetPoke.before_loop
    async def beforeResetPoke(self):
        await self.client.wait_until_ready()

    @tasks.loop(hours=1.0)
    async def resetPrison(self):
        """
        Task that lowers prison time daily
        """
        # Don't do it multiple times a day if bot dc's, ...
        with open("files/lastTasks.json", "r") as fp:
            lastTasks = json.load(fp)

        if int(self.getCurrentHour()) == 0 and int(time.time()) - int(lastTasks["prison"]) > 10000:
            prison.dailyLowers()

            with open("files/lastTasks.json", "w") as fp:
                lastTasks["prison"] = round(time.time())
                json.dump(lastTasks, fp)

    @resetPrison.before_loop
    async def beforeResetPrison(self):
        await self.client.wait_until_ready()

    @tasks.loop(hours=1.0)
    async def checkBirthdays(self):
        """
        Task that wishes people a happy birthday
        """
        # Don't do it multiple times a day if bot dc's, ...
        with open("files/lastTasks.json", "r") as fp:
            lastTasks = json.load(fp)
        if int(self.getCurrentHour()) == 6 and int(time.time()) - int(lastTasks["birthdays"]) > 10000:
            dt = timeFormatters.dateTimeNow()
            res = birthdays.get_users_on_date(dt.day, dt.month)

            COC = self.client.get_guild(int(constants.CallOfCode))
            people = [COC.get_member(int(user[0])) for user in res]
            general = COC.get_channel(int(constants.CoCGeneral))

            lastTasks["birthdays"] = round(time.time())
            with open("files/lastTasks.json", "w") as fp:
                json.dump(lastTasks, fp)

            if not people:
                return

            if len(people) == 1:
                return await general.send("Gelukkige verjaardag {}!".format(people[0].mention))
            return await general.send("Gelukkige verjaardag {} en {}!".format(
                ", ".join(user.mention for user in people[:-1]),
                people[-1].mention
            ))

    @checkBirthdays.before_loop
    async def beforecheckBirthdays(self):
        await self.client.wait_until_ready()

    @tasks.loop(hours=1.0)
    async def updateMessageCounts(self):
        """
        Task that updates the activity counter for channels
        """
        # Don't do it multiple times a day if bot dc's, ...
        with open("files/lastTasks.json", "r") as fp:
            lastTasks = json.load(fp)
        if int(self.getCurrentHour()) == 0 and int(time.time()) - int(lastTasks["channels"]) > 10000:
            channels = stats.channel_activity()
            for channel in channels:
                stats.lower_channel(int(channel[0]), 0.95 * float(channel[1]))

            with open("files/lastTasks.json", "w") as fp:
                lastTasks["channels"] = round(time.time())
                json.dump(lastTasks, fp)

    @updateMessageCounts.before_loop
    async def beforeupdateMessageCounts(self):
        await self.client.wait_until_ready()

    @tasks.loop(hours=1.0)
    async def sendReminders(self):
        """
        Task that sends people daily reminders
        """
        # Don't do it multiple times a day if bot dc's, ...
        with open("files/lastTasks.json", "r") as fp:
            lastTasks = json.load(fp)
        if int(self.getCurrentHour()) == 7 and int(time.time()) - int(lastTasks["remind"]) > 10000:
            reminders = Reminders()

            weekday = self.getCurrentWeekday()

            for category in reminders.categories:
                # Check if this reminder is temporarily disabled
                if category["disabled"]:
                    continue

                # Checks if this reminder can be sent on weekdays
                if (not category["weekends"]) and weekday > 4:
                    continue

                for user in category["users"]:
                    userInstance = self.client.get_user(user)

                    # User can't be fetched for whatever reason, ignore instead of crashing
                    if userInstance is None:
                        continue

                    # Check if a special embed has to be attached for this reminder
                    if "embed" not in category:
                        await userInstance.send(random.choice(category["messages"]))
                    else:
                        await userInstance.send(random.choice(category["messages"]), embed=category["embed"])

            with open("files/lastTasks.json", "w") as fp:
                lastTasks["remind"] = round(time.time())
                json.dump(lastTasks, fp)

    @sendReminders.before_loop
    async def beforeSendReminders(self):
        await self.client.wait_until_ready()

    @tasks.loop(hours=2.0)
    async def updateMatchweek(self):
        """
        Task that checks the current JPL matchweek & changes the dict value
        """
        matchweek = getMatchweek()

        if matchweek is None:
            return

        # Change the setting in the config
        config("jpl_day", int(matchweek))

    @updateMatchweek.before_loop
    async def beforeUpdateMatchweek(self):
        await self.client.wait_until_ready()

    @tasks.loop(minutes=10.0)
    async def uforaAnnouncements(self):
        """
        Task that checks for new Ufora announcements every few minutes
        """
        # Get new notifications
        announcements = ufora_notifications.run()

        if announcements:
            announcements_channel = self.client.get_channel(816724500136591380)

            for an in announcements:
                await announcements_channel.send(embed=an.to_embed())

    @uforaAnnouncements.before_loop
    async def beforeUforaAnnouncements(self):
        await self.client.wait_until_ready()

    def getCurrentHour(self):
        return timeFormatters.dateTimeNow().hour

    def getCurrentWeekday(self):
        return timeFormatters.dateTimeNow().weekday()

    def getCurrentBitcoinPrice(self):
        result = requests.get("https://api.coindesk.com/v1/bpi/currentprice.json").json()
        currentPrice = result["bpi"]["EUR"]["rate_float"]
        return float(currentPrice)


def setup(client):
    client.add_cog(Tasks(client))
