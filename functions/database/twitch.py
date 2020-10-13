from functions.database import utils


def add(userid, link):
    user = get_user(userid)
    connection = utils.connect()
    cursor = connection.cursor()
    if len(user) == 0:
        cursor.execute("INSERT INTO twitch(userid, link) VALUES (%s, %s)", (int(userid), str(link),))
    else:
        cursor.execute("""UPDATE twitch SET link = %s WHERE userid = %s""", (link, int(userid),))
    connection.commit()


def getAll():
    connection = utils.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM twitch")
    result = cursor.fetchall()
    return result


def get_user(userid):
    connection = utils.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT link FROM twitch WHERE userid = %s", (int(userid),))
    return cursor.fetchall()

