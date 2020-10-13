from functions.database import utils


def add(userid, link):
    user = get_user(userid)
    connection = utils.connect()
    cursor = connection.cursor()
    if len(user) == 0:
        cursor.execute("INSERT INTO githubs(userid, githublink) VALUES (%s, %s)", (int(userid), str(link),))
    else:
        cursor.execute("""UPDATE githubs SET githublink = %s WHERE userid = %s""", (user[0][0] + "\n" + link, int(userid),))
    connection.commit()


def getAll():
    connection = utils.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM githubs")
    result = cursor.fetchall()
    return result


def get_user(userid):
    connection = utils.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT githublink FROM githubs WHERE userid = %s", (int(userid),))
    return cursor.fetchall()
