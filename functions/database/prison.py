from functions.database import utils


def getUser(userId):
    connection = utils.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM prison WHERE userid = %s", (int(userId),))
    return cursor.fetchall()


def remove(userId):
    connection = utils.connect()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM prison WHERE userid = %s", (int(userId),))
    connection.commit()


def imprison(userid, bailsum, days, daily):
    connection = utils.connect()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO prison(userid, bail, days, daily) VALUES (%s, %s, %s, %s)",
                   (int(userid), float(bailsum), int(days), float(daily),))
    connection.commit()


def dailyLowers():
    connection = utils.connect()
    cursor = connection.cursor()

    # Release people from prison on their last day
    cursor.execute("DELETE FROM prison WHERE days = 1")
    connection.commit()

    # Get all remaining users
    cursor.execute("SELECT * FROM prison")
    prisoners = cursor.fetchall()

    for prisoner in prisoners:
        cursor.execute("UPDATE prison "
                       "SET bail = %s, days = %s "
                       "WHERE userid = %s",
                       (float(prisoner[1]) - float(prisoner[3]), int(prisoner[2]) - 1,
                        int(prisoner[0]),))
        connection.commit()
