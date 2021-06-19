from functions.database import utils
import time


def invoked():
    t = time.localtime()
    day_string: str = f"{t.tm_year}-{_lz(t.tm_mon)}-{_lz(t.tm_mday)}"
    _update(day_string)


def _lz(arg: int) -> str:
    """
    Add leading zeroes if necessary (YYYY-MM-DD)
    """
    arg = str(arg)

    if len(arg) == 1:
        return f"0{arg}"

    return arg


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

    cursor.execute("INSERT INTO command_stats(day, amount) VALUES (%s, 1)", (date,))
    connection.commit()


def _update(date: str):
    """
    Increase the counter for a given day
    """
    # Date wasn't present yet, add it with a value of 1
    if not _is_present(date):
        _add_date(date)
        return

    connection = utils.connect()
    cursor = connection.cursor()

    cursor.execute("""
                    UPDATE command_stats
                        SET amount = amount + 1
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
