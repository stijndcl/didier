from data.database_classes.custom_commands import CustomCommand
import discord
from functions.database import utils


def is_custom_command(message: discord.Message) -> CustomCommand:
    """
    Check if a message triggers a custom command
    These use "?" as a prefix
    """
    content = message.content
    # Message didn't call a custom command
    if not content.startswith("?"):
        return CustomCommand()

    # Can't be invoked by bots to prevent spam (@RPS)
    if message.author.bot:
        return CustomCommand()

    # Ignore capitals & spaces, strip off prefix
    content = content.lower().replace(" ", "")[1:]

    by_name = _find_by_name(content)

    # Command was found by its name
    if by_name:
        return CustomCommand(*by_name)

    # Check if a command exists with this alias instead
    return CustomCommand(*_find_by_alias(content), alias_used=content)


def _find_by_name(message):
    """
    Find a command by its name
    """
    connection = utils.connect()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM custom_commands WHERE name = %s", (message,))

    return cursor.fetchone()


def _find_by_alias(message):
    """
    Find a command by one of its aliases
    """
    connection = utils.connect()
    cursor = connection.cursor()

    cursor.execute("SELECT command FROM custom_command_aliases WHERE alias = %s", (message,))

    res = cursor.fetchone()

    # No command matched this alias
    if not res:
        return ()

    cursor.execute("SELECT * FROM custom_commands WHERE id = %s", (res,))

    return cursor.fetchone()


def is_name_free(name) -> bool:
    """
    Check if a name is already in use by a command
    Includes aliases
    """
    connection = utils.connect()
    cursor = connection.cursor()

    cursor.execute("SELECT id from custom_commands WHERE name = %s", (name,))

    if cursor.fetchone():
        return False

    cursor.execute("SELECT id FROM custom_command_aliases WHERE alias = %s", (name,))

    return cursor.fetchone() is None


def _clean(inp: str):
    """
    Strip markdown and other stuff out of a command name
    """
    return "".join(filter(lambda x: x.isalnum(), inp))


def add_command(name: str, response: str):
    """
    Add a new custom command
    """
    name = _clean(name.lower())

    if not is_name_free(name):
        return "Er is al een commando met deze naam."

    connection = utils.connect()
    cursor = connection.cursor()

    cursor.execute("INSERT INTO custom_commands(name, response) VALUES (%s, E%s)", (name, response,))
    connection.commit()


def add_alias(command: str, alias: str):
    """
    Add an alias for a command
    Assumes the command exists
    """
    command = _clean(command.lower())
    alias = _clean(alias.lower())

    # Base command doesn't exist
    if is_name_free(command):
        return "Er is geen commando met deze naam."

    # Alias already exists
    if not is_name_free(alias):
        return "Er is al een commando met deze naam."

    # Find the id of the base command
    command_id = CustomCommand(*_find_by_name(command)).id

    connection = utils.connect()
    cursor = connection.cursor()

    cursor.execute("INSERT INTO custom_command_aliases(command, alias) VALUES(%s, %s)", (command_id, alias,))
    connection.commit()
