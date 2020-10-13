from functions.database import utils
import random


def getRandomJoke():
    connection = utils.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM dad_jokes")
    return random.choice(cursor.fetchall())[1]


def addJoke(joke):
    connection = utils.connect()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO dad_jokes(joke) VALUES (%s)", (str(joke),))
    connection.commit()
