import psycopg2
from settings import DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD


connection = None


def connect():
    global connection

    if connection is None:
        create_connection()
    return connection


def create_connection():
    global connection

    connection = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USERNAME,
        password=DB_PASSWORD
    )


def reconnect():
    global connection

    connection.close()
    create_connection()
