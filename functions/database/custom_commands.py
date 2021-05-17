from data.database_classes.custom_commands import CustomCommand
from functions.database import utils


def is_custom_command(message: str) -> CustomCommand:
    """
    Check if a message triggers a custom command
    These use "?" as a prefix
    """
    # Message didn't call a custom command
    if not message.startswith("?"):
        return CustomCommand()

    # Ignore capitals & spaces, strip off prefix
    message = message.lower().replace(" ", "")[1:]

    by_name = _find_by_name(message)

    # Command was found by its name
    if by_name:
        return CustomCommand(*by_name)

    # Check if a command exists with this alias instead
    return CustomCommand(*_find_by_alias(message), alias_used=message)


def _find_by_name(message):
    """
    Find a command by its name
    """
    connection = utils.connect()
    cursor = connection.cursor()

    cursor.execute("SELECT response FROM custom_commands WHERE name = %s", message)

    return cursor.fetchone()


def _find_by_alias(message):
    """
    Find a command by one of its aliases
    """
    connection = utils.connect()
    cursor = connection.cursor()

    cursor.execute("SELECT command FROM custom_command_aliases WHERE alias = %s", message)

    res = cursor.fetchone()

    # No command matched this alias
    if not res:
        return ()

    cursor.execute("SELECT response FROM custom_commands WHERE id = %s", res)

    return cursor.fetchone()


def is_name_free(name) -> bool:
    """
    Check if a name is already in use by a command
    Includes aliases
    """
    connection = utils.connect()
    cursor = connection.cursor()

    cursor.execute("SELECT id from custom_commands WHERE name = %s", name)

    if cursor.fetchone():
        return False

    cursor.execute("SELECT command FROM custom_command_aliases WHERE alias = %s", name)

    return len(cursor.fetchone()) != 0
