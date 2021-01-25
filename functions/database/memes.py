from functions.database import utils


def insert(id, name, fields):
    if getMeme(name) is not None:
        return "Deze meme staat al in de database."

    connection = utils.connect()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO memes(id, name, fields) VALUES (%s, %s, %s)", [int(id), name.lower(), int(fields)])
    connection.commit()

    return "{} is toegevoegd aan de database.".format(name[0].upper() + name[1:].lower())


def getMeme(name):
    connection = utils.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM memes WHERE name like %s", ["%" + name.lower() + "%"])
    result = cursor.fetchall()
    if len(result) == 0:
        return None
    return result[0]


def getAllMemes():
    connection = utils.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM memes")
    result = cursor.fetchall()
    return result
