import datetime
from functions.database import utils, stats
import time


def dinks(userid):
    return getOrAddUser(userid)[1]


def dinksAll(userid):
    platinumDinks = 0

    connection = utils.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT amount FROM inventory WHERE userid = %s AND itemid = %s", (int(userid), 1,))
    result = cursor.fetchall()

    if result:
        platinumDinks = result[0][0]

    return {"dinks": dinks(userid), "platinum": platinumDinks}


def getAllRows():
    connection = utils.connect()
    cursor = connection.cursor()
    cursor.execute(
        """SELECT * FROM currencytable"""
    )

    return cursor.fetchall()


def getAllPlatDinks():
    connection = utils.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT userid, amount FROM inventory WHERE itemid = 1")
    result = cursor.fetchall()
    dic = {}
    for user in result:
        dic[str(user[0])] = user[1]
    return dic


def getOrAddUser(userid):
    connection = utils.connect()
    cursor = connection.cursor()
    query = "SELECT * FROM currencytable WHERE userid = %s"
    cursor.execute(
        query, (int(userid),)
    )
    result = cursor.fetchall()
    # User didn't exist yet, so create a new default file
    if len(result) == 0:
        createNewUser(userid, connection)
        return getOrAddUser(userid)
    return result[0]


# TODO check for nightly bonus & add+return that instead of 420
def nightly(userid):
    user = getOrAddUser(userid)
    today = datetime.datetime.today().date()
    lastNightly = datetime.datetime.fromtimestamp(user[9]).date()
    streak = int(user[10])
    if lastNightly < today:
        update(userid, "dinks", float(user[1]) + 420.0)
        update(userid, "nightly", int(time.time()))

        # Update the streak
        if (today - lastNightly).days > 1:
            update(userid, "nightly_streak", 1)
            streak = 1
        else:
            update(userid, "nightly_streak", streak + 1)
            streak += 1

        s = stats.getOrAddUser(userid)

        if streak > int(s[5]):
            stats.update(userid, "longest_streak", streak)

        stats.update(userid, "nightlies_count", int(s[6]) + 1)

        return [True, 420, streak]
    return [False, 0, -1]


def createNewUser(userid, connection=None):
    if connection is None:
        connection = utils.connect()
    cursor = connection.cursor()
    query = "INSERT INTO currencytable(userid, dinks, banklevel, investedamount, investeddays, profit, defense, offense, bitcoins, nightly) " \
            "VALUES (%s, 0.0, 1, 0.0, 0, 0, 1, 1, 0.0, 0)"
    cursor.execute(query, (int(userid),))
    connection.commit()


def update(userid, column, value):
    _ = getOrAddUser(userid)
    connection = utils.connect()
    cursor = connection.cursor()
    query = "UPDATE currencytable " \
            "SET {} = %s " \
            "WHERE userid = %s".format(column)
    cursor.execute(query, (value, userid,))
    connection.commit()
