import traceback

from discord.ext.commands import Context
from dislash import SlashInteraction


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


def format_slash_command_usage(interaction: SlashInteraction) -> str:
    # Create a string with the options used
    options = " ".join(list(map(
        lambda option: f"{option.name}: \"{option.value}\"",
        interaction.data.options.values()
    )))

    command = f"{interaction.slash_command.name} {options or ''}"
    return f"{interaction.author.display_name} in {_format_error_location(interaction)}: /{command}"
