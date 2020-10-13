from functions.database import utils, stats
import time


def get():
    connection = utils.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM poke")
    return cursor.fetchall()[0]


def update(user, new):
    connection = utils.connect()
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE poke "
        "SET current = %s, poketime = %s, previous = %s",
        (int(new), int(time.time()), int(user))
    )
    connection.commit()


def blacklisted(user):
    connection = utils.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT poke_blacklist FROM info WHERE userid = %s", (int(user),))
    res = cursor.fetchall()
    if len(res) == 0:
        connection = utils.connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO info(userid, poke_blacklist) VALUES(%s, False)", (int(user),))
        connection.commit()
        return False
    return res[0][0]


# Changes the poke blacklist state to true or false
def blacklist(user, bl=True):
    connection = utils.connect()
    cursor = connection.cursor()
    cursor.execute("UPDATE info "
                   "SET poke_blacklist = %s WHERE userid = %s", (bl, int(user),))
    connection.commit()


# Returns a list of all blacklisted users
def getAllBlacklistedUsers():
    connection = utils.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT userid FROM info WHERE poke_blacklist = True")
    return [str(user[0]) for user in cursor.fetchall()]


def reset():
    current = get()[0]
    new = stats.pokeResetCandidate(current, [int(user) for user in getAllBlacklistedUsers()])
    update(current, new)
    return new
