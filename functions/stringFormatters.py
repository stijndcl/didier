import traceback

from discord import Interaction
from discord.ext.commands import Context


def title_case(string):
    return " ".join(capitalize(word) for word in string.split(" "))


def capitalize(string):
    if len(string) > 1:
        return string[0].upper() + string[1:].lower()
    return string[0].upper()


def leading_zero(string, size=2):
    string = str(string)
    while len(string) < size:
        string = "0" + string
    return string


def format_error_tb(err: Exception) -> str:
    # Remove the InvokeCommandError because it's useless information
    x = traceback.format_exception(type(err), err, err.__traceback__)
    error_string = ""
    for line in x:
        if "direct cause of the following" in line:
            break
        error_string += line.replace("*", "") + "\n" if line.strip() != "" else ""

    return error_string


def _format_error_location(src) -> str:
    DM = src.guild is None
    return "DM" if DM else f"{src.channel.name} ({src.guild.name})"


def format_command_usage(ctx: Context) -> str:
    return f"{ctx.author.display_name} in {_format_error_location(ctx)}: {ctx.message.content}"


def format_slash_command_usage(interaction: Interaction) -> str:
    # Create a string with the options used
    options = " ".join(list(map(
        lambda o: f"{o['name']}: \"{o['value']}\"" if "value" in o else o["name"],
        interaction.data.get("options", [])
    )))

    command = f"{interaction.data['name']} {options or ''}"
    return f"{interaction.user.display_name} in {_format_error_location(interaction)}: /{command}"


def get_edu_year(index: int) -> str:
    return ["1ste Bachelor", "2de Bachelor", "3de Bachelor", "1ste Master", "2de Master"][index - 1]
