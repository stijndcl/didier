from functions import checks
from functions.database import utils, currency


def buy(ctx, userid, itemid, amount):
    connection = utils.connect()
    cursor = connection.cursor()
    dinks = currency.dinks(userid)
    cursor.execute("SELECT * FROM store WHERE itemid = %s", (int(itemid),))
    result = cursor.fetchall()
    if not result:
        return False, "Er is geen item met dit id."

    # Not an empty list, no IndexError.
    result = result[0]

    cursor.execute("SELECT amount FROM inventory WHERE userid = %s AND itemid = %s", (int(userid), int(itemid),))
    inv = cursor.fetchall()
    # Check if user already owns this
    limit = result[3]
    if limit is not None \
            and inv \
            and inv[0][0] + amount > limit:
        return False, "Je kan dit item maar {} keer kopen.".format(limit)

    isValid = checks.isValidAmount(ctx, result[2] * amount)

    if not isValid[0]:
        return isValid

    currency.update(userid, "dinks", dinks - (result[2] * amount))
    addItem(userid, itemid, amount, inv)
    return True, {"id": result[0], "name": result[1], "price": result[2] * amount}


def addItem(userid, itemid, amount, inv):
    connection = utils.connect()
    cursor = connection.cursor()

    # It's already in there, add more to the counter
    if inv:
        amount += inv[0][0]
        cursor.execute("UPDATE inventory SET amount = %s WHERE userid = %s AND itemid = %s", (amount, userid, itemid))
        connection.commit()
        return

    # Doesn't own this item yet, add a new row
    cursor.execute("INSERT INTO inventory(userid, itemid, amount) VALUES (%s, %s, %s)", (userid, itemid, amount))
    connection.commit()


def getAllItems():
    connection = utils.connect()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM store")
    return cursor.fetchall()


def getItemPrice(itemid):
    connection = utils.connect()
    cursor = connection.cursor()

    cursor.execute("SELECT price FROM store WHERE itemid = %s", (itemid,))
    return cursor.fetchone()


def inventory(userid):
    connection = utils.connect()
    cursor = connection.cursor()

    cursor.execute("SELECT inventory.itemid, name, amount FROM inventory INNER JOIN store on inventory.itemid = store.itemid WHERE userid = %s", (int(userid),))
    return cursor.fetchall()


# Amount = amount of item before sell
def sell(userid, itemid, sold, amount):
    connection = utils.connect()
    cursor = connection.cursor()

    # Don't store amount: 0
    if sold == amount:
        cursor.execute("DELETE FROM inventory WHERE userid = %s AND itemid = %s", (userid, itemid,))
        return connection.commit()

    cursor.execute("UPDATE inventory SET amount = %s WHERE userid = %s AND itemid = %s", (amount - sold, userid, itemid))
    return connection.commit()
