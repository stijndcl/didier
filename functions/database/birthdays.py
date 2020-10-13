from functions.database import utils


def get_user(userid):
    connection = utils.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT day, month, year FROM birthdays WHERE userid = %s", (int(userid),))
    return cursor.fetchall()


def get_users_on_date(day, month):
    connection = utils.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT userid FROM birthdays WHERE day = %s AND month = %s", (int(day), int(month),))
    return cursor.fetchall()


def add_user(userid, day, month, year):
    connection = utils.connect()
    cursor = connection.cursor()
    if get_user(userid):
        cursor.execute("UPDATE birthdays SET day = %s, month = %s, year = %s WHERE userid = %s",
                       (int(day), int(month), int(year), int(userid),))
    else:
        cursor.execute("INSERT INTO birthdays(userid, day, month, year) VALUES (%s, %s, %s, %s)",
                       (int(userid), int(day), int(month), int(year),))
    connection.commit()
