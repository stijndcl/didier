from data import constants
from functions.database import utils
import random


def getOrAddUser(userid):
    connection = utils.connect()
    cursor = connection.cursor()
    query = "SELECT * FROM muttn WHERE userid = %s"
    cursor.execute(
        query, (int(userid),)
    )
    result = cursor.fetchall()
    # User didn't exist yet, so create a new default file
    if len(result) == 0:
        createNewUser(userid, connection)
        return getOrAddUser(userid)
    return result[0]


def getAllRows():
    connection = utils.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM muttn")
    return cursor.fetchall()


def createNewUser(userid, connection):
    cursor = connection.cursor()
    cursor.execute("INSERT INTO muttn(userid, stats, count, message) VALUES (%s, %s, %s, %s)", (
        int(userid), random.randint(0, 50) + (random.randint(0, 100)/100), 0, 0,
    ))
    connection.commit()


def muttn(userid, count, messageid):
    if str(userid) == constants.didierId:
        return

    connection = utils.connect()
    cursor = connection.cursor()

    user = getOrAddUser(userid)

    # Dont' allow earlier messages to be spammed to avoid abuse
    if messageid < user[3]:
        return

    # 5 or more = percentage increase
    if count >= 5:
        # React was removed & added again: don't do anything
        # New count is smaller than or equal to old max for this message
        if count <= user[4] and messageid == user[3]:
            return

        cursor.execute("UPDATE muttn SET stats = %s, message = %s, highest = %s WHERE userid = %s",
                       (float(user[1]) + (random.randint(2, 50) * count/1000), int(messageid), count, int(userid)))
        connection.commit()
    cursor.execute("UPDATE muttn SET count = %s WHERE userid = %s",
                   (int(user[2]) + 1, int(userid),))
    connection.commit()


def removeMuttn(message):
    if str(message.author.id) == constants.didierId:
        return

    connection = utils.connect()
    cursor = connection.cursor()

    user = getOrAddUser(message.author.id)

    cursor.execute("UPDATE muttn SET count = %s WHERE userid = %s",
                   (int(user[2]) - 1, int(message.author.id),))
    connection.commit()

