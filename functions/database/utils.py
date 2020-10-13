import psycopg2
import json
import os


connection = None


def connect():
    global connection

    if connection is None:
        create_connection()
    return connection


def create_connection():
    global connection

    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path, "../../files/database.json"), "r") as fp:
        db = json.load(fp)

    connection = psycopg2.connect(
        host=db["host"],
        database=db["database"],
        user=db["username"],
        password=db["password"]
    )


def reconnect():
    global connection

    connection.close()
    create_connection()
