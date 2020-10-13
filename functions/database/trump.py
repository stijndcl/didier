from functions.database import utils
import random


def add(quote, date, location):
    connection = utils.connect()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO trump(quote, date, location) VALUES (%s, %s, %s)", (str(quote), str(date), str(location),))
    connection.commit()


def getRandomQuote():
    connection = utils.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM trump")
    result = cursor.fetchall()
    return random.choice(result)
