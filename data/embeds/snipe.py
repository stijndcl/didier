from data.snipe import Snipe
import discord
from startup.didier import Didier


class EditSnipe:
    """
    Creates an Embed to snipe people that edited a message
    """
    def __init__(self, snipe: Snipe):
        self.snipe = snipe

    def to_embed(self, client: Didier) -> discord.Embed:
        guild: discord.Guild = client.get_guild(self.snipe.guild)
        member: discord.Member = guild.get_member(self.snipe.user)

        embed = discord.Embed(title="Edit Snipe", colour=discord.Colour.blue())
        embed.set_author(name=member.display_name, icon_url=member.avatar_url)
        embed.add_field(name="Voor", value=self.snipe.old, inline=False)
        embed.add_field(name="Na", value=self.snipe.new, inline=False)

        return embed


class DeleteSnipe:
    """
    Creates an Embed to snipe people that removed a message
    """
    def __init__(self, snipe: Snipe):
        self.snipe = snipe

    def to_embed(self, client: Didier) -> discord.Embed:
        guild: discord.Guild = client.get_guild(self.snipe.guild)
        member: discord.Member = guild.get_member(self.snipe.user)

        embed = discord.Embed(title="Delete Snipe", colour=discord.Colour.blue())
        embed.set_author(name=member.display_name, icon_url=member.avatar_url)
        embed.add_field(name="Message", value=self.snipe.old)

        return embed
