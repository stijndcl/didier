from enum import IntEnum

from functions.database import utils
from functions.stringFormatters import leading_zero as lz
import time


class InvocationType(IntEnum):
    TextCommand = 0
    SlashCommand = 1
    ContextMenu = 2


def invoked(inv: InvocationType):
    t = time.localtime()
    day_string: str = f"{t.tm_year}-{lz(t.tm_mon)}-{lz(t.tm_mday)}"
    _update(day_string, inv)


def _is_present(date: str) -> bool:
    """
    Check if a given date is present in the database
    """
    connection = utils.connect()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM command_stats WHERE day = %s", (date,))
    res = cursor.fetchone()

    if res:
        return True

    return False


def _add_date(date: str):
    """
    Add a date into the db
    """
    connection = utils.connect()
    cursor = connection.cursor()

    cursor.execute("INSERT INTO command_stats(day, commands, slash_commands, context_menus) VALUES (%s, 0, 0, 0)", (date,))
    connection.commit()


def _update(date: str, inv: InvocationType):
    """
    Increase the counter for a given day
    """
    # Date wasn't present yet, add it
    if not _is_present(date):
        _add_date(date)

    connection = utils.connect()
    cursor = connection.cursor()

    column_name = ["commands", "slash_commands", "context_menus"][inv.value]

    # String formatting is safe here because the input comes from above ^
    cursor.execute(f"""
                    UPDATE command_stats
                        SET {column_name} = {column_name} + 1
                    WHERE day = %s
                    """, (date,))
    connection.commit()


def _get_all():
    """
    Get all rows
    """
    connection = utils.connect()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM command_stats")
    return cursor.fetchall()
