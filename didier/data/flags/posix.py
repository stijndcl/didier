from discord.ext import commands


class PosixFlags(commands.FlagConverter, delimiter=" ", prefix="--"):
    """Base class to add POSIX-like flags to commands

    Example usage:
        >>> class Flags(PosixFlags):
        >>>     name: str
        >>> async def command(ctx, *, flags: Flags):
        >>>     ...
    This can now be called in Discord as
    command --name here-be-name
    """
