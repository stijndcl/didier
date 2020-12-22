from functions import xp
from functions.database import utils
import json
import random
import time


def getOrAddUser(userid):
    connection = utils.connect()
    cursor = connection.cursor()
    query = "SELECT * FROM personalstats WHERE userid = %s"
    cursor.execute(
        query, (int(userid),)
    )
    result = cursor.fetchall()
    # User didn't exist yet, so create a new default file
    if len(result) == 0:
        createNewUser(userid, connection)
        return getOrAddUser(userid)
    return result[0]


def createNewUser(userid, connection=None):
    if connection is None:
        connection = utils.connect()
    cursor = connection.cursor()
    query = "INSERT INTO personalstats(userid, poked, robs_success, robs_failed, robs_total, longest_streak) " \
            "VALUES (%s, 0, 0, 0, 0, 0)"
    cursor.execute(query, (int(userid),))
    connection.commit()


def getAllRows():
    connection = utils.connect()
    cursor = connection.cursor()
    cursor.execute(
        """SELECT * FROM personalstats"""
    )

    return cursor.fetchall()


def update(userid, column, value):
    _ = getOrAddUser(userid)
    connection = utils.connect()
    cursor = connection.cursor()
    query = "UPDATE personalstats " \
            "SET {} = %s " \
            "WHERE userid = %s".format(column)
    cursor.execute(query, (value, userid,))
    connection.commit()
    statsTracker(column)


# Automatically change global stats
def statsTracker(column):
    if column in stats()["rob"]:
        with open("files/stats.json", "r") as fp:
            s = json.load(fp)

        s["rob"][column] += 1

        with open("files/stats.json", "w") as fp:
            json.dump(s, fp)


def stats():
    return {"rob": ["robs_failed", "robs_success"]}


# Gets a random person that has been poked before & has not blacklisted themself
def pokeResetCandidate(current, blacklisted):
    connection = utils.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM personalstats WHERE poked != 0 and userid != %s and userid not in %s",
                   (int(current), tuple(blacklisted)))
    return random.choice(cursor.fetchall())[0]


def sentMessage(message):
    user = message.author

    # Ignore bots
    if user.bot:
        return

    # Ignore dm's
    if message.guild is None:
        return

    # Don't give xp for bot commands
    if message.content.lower().startswith(("didier", "owo", "?", "rps", "p!", "-")):
        return

    user_db = getOrAddUser(user.id)

    update(user.id, "messages", user_db[11] + 1)
    update_channel(message.channel.id)

    # Only gain xp every minute
    if round(time.time()) - user_db[13] > 30:
        gainXp(user.id, user_db)


def gainXp(user, user_db):
    update(user, "xp", user_db[12] + random.randint(5, 15) + (xp.calculate_level(user_db[12]) * 3))
    update(user, "last_message", round(time.time()))


def getTotalMessageCount():
    r = getAllRows()

    return sum(user[11] for user in r)


def getOrAddChannel(channelid: int):
    connection = utils.connect()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM channel_activity WHERE channel_id = %s", (channelid,))

    res = cursor.fetchall()

    if not res:
        cursor.execute("INSERT INTO channel_activity(channel_id, message_count) VALUES (%s, 0)", (channelid,))
        connection.commit()

        return getOrAddChannel(channelid)

    return res


def channel_activity(channel=None):
    connection = utils.connect()
    cursor = connection.cursor()

    # All channels
    if channel is None:
        cursor.execute("SELECT * FROM channel_activity")
        return cursor.fetchall()
    return getOrAddChannel(channel.id)


def update_channel(channelid: int):
    connection = utils.connect()
    cursor = connection.cursor()

    channel = getOrAddChannel(channelid)[0]
    cursor.execute("UPDATE channel_activity SET message_count = %s WHERE channel_id = %s",
                   (float(channel[1]) + 1, channelid))
    connection.commit()


def lower_channel(channelid: int, message_count):
    connection = utils.connect()
    cursor = connection.cursor()

    cursor.execute("UPDATE channel_activity SET message_count = %s WHERE channel_id = %s",
                   (float(message_count), channelid,))
    connection.commit()
