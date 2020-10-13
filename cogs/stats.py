from decorators import help
import discord
from discord.ext import commands
from enums.help_categories import Category
from functions import checks
from functions.database import stats
import json


class Stats(commands.Cog):

    def __init__(self, client):
        self.client = client

    # Don't allow any commands to work when locked
    def cog_check(self, ctx):
        return not self.client.locked

    @commands.group(name="Stats", usage="[Categorie]*", case_insensitive=True, invoke_without_command=True)
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.Other)
    async def stats(self, ctx):
        s = stats.getOrAddUser(ctx.author.id)

        # Calculate the percentages
        robAttempts = int(s[2]) + int(s[3]) if int(s[2]) + int(s[3]) != 0 else 1
        robSuccessPercent = round(100 * int(s[2]) / robAttempts, 2)
        robFailedPercent = round(100 * int(s[3]) / robAttempts, 2)

        embed = discord.Embed(colour=discord.Colour.blue())
        embed.set_author(name="{}'s Stats".format(ctx.author.display_name))
        embed.add_field(name="Geslaagde Rob Pogingen", value="{} ({})%".format(s[2], robSuccessPercent))
        embed.add_field(name="Gefaalde Rob Pogingen", value="{} ({})%".format(s[3], robFailedPercent))
        embed.add_field(name="Aantal Dinks Gestolen", value="{:,}".format(round(s[4])))
        embed.add_field(name="Aantal Nightlies", value=str(s[6]))
        embed.add_field(name="Langste Nightly Streak", value=str(s[5]))
        embed.add_field(name="Totale Profit", value="{:,}".format(round(s[7])))
        embed.add_field(name="Aantal keer gepoked", value=str(s[1]))
        embed.add_field(name="Aantal Gewonnen Coinflips", value=str(s[8]))
        embed.add_field(name="Totale winst uit Coinflips", value="{:,}".format(round(s[9])))
        embed.add_field(name="Aantal Bails", value="{:,}".format(int(s[10])))
        await ctx.send(embed=embed)

    @stats.command(aliases=["Coinflip"], hidden=True)
    async def cf(self, ctx):
        with open("files/stats.json", "r") as fp:
            s = json.load(fp)

        embed = discord.Embed(colour=discord.Colour.blue())
        embed.set_author(name="Coinflip Stats")
        embed.description = "**Kop**: {:,} ({}%)\n**Munt**: {:,} ({}%)".format(
            s["cf"]["h"], self.percent(s["cf"], "h"), s["cf"]["t"], self.percent(s["cf"], "t"))
        await ctx.send(embed=embed)

    @stats.command(aliases=["Roll"], hidden=True)
    async def dice(self, ctx):
        with open("files/stats.json", "r") as fp:
            s = json.load(fp)

        embed = discord.Embed(colour=discord.Colour.blue())
        embed.set_author(name="Dice Stats")
        embed.description = "\n".join(["**{}**: {:,} ({}%)".format(
            i, s["dice"][i], self.percent(s["dice"], i)) for i in sorted(s["dice"].keys())])
        await ctx.send(embed=embed)

    @stats.command(hidden=True)
    async def rob(self, ctx):
        with open("files/stats.json", "r") as fp:
            s = json.load(fp)["rob"]
        totalAttempts = s["robs_success"] + s["robs_failed"]
        successPercent = round(100 * s["robs_success"] / totalAttempts, 2)
        failedPercent = round(100 * s["robs_failed"] / totalAttempts, 2)
        embed = discord.Embed(colour=discord.Colour.blue())
        embed.set_author(name="Rob Stats")
        embed.description = "**Geslaagd**: {:,} ({}%)\n**Gefaald**: {:,} ({}%)\n**Borg betaald**: {:,}".format(
            s["robs_success"], successPercent, s["robs_failed"], failedPercent, round(s["bail_paid"])
        )
        await ctx.send(embed=embed)

    @stats.command(name="Channels", aliases=["C", "CA"], usage="[#Channel]*", hidden=True)
    @commands.check(checks.isMod)
    async def channels(self, ctx, channel: discord.TextChannel = None):
        res = stats.channel_activity(channel)

        embed = discord.Embed(colour=discord.Colour.blue())

        if channel:
            embed.set_author(name="Channel Activity - {}".format(channel.name))
            channel_instance = self.client.get_channel(int(res[0][0]))
            embed.add_field(name="Aantal berichten", value="{:,}".format(round(float(res[0][1]), 2)), inline=False)

            try:
                last_message = await channel_instance.fetch_message(channel_instance.last_message_id)
            except discord.NotFound:
                last_message = None

            if last_message is None:
                embed.add_field(name="Laatste bericht", value="[Verwijderd]", inline=False)
            else:
                embed.add_field(name="Laatste bericht", value="[Jump URL]({})".format(last_message.jump_url), inline=False)
        elif ctx.guild:
            embed.set_author(name="Channel Activity - {}".format(ctx.guild))

            description = ""
            for c in sorted(res, key=lambda x: int(x[1]), reverse=True):
                if not any(tc.id == int(c[0]) for tc in ctx.guild.text_channels):
                    continue

                channel_instance = self.client.get_channel(int(c[0]))

                description += "{}: {:,}\n".format(channel_instance.mention, round(float(c[1]), 2))

            embed.description = description
        else:
            return await ctx.send("Dit commando werkt niet in DM's.")

        return await ctx.send(embed=embed)

    async def callStats(self, name, ctx):
        await [command for command in self.stats.commands if command.name == name][0](ctx)

    def percent(self, dic, stat):
        total = sum([int(dic[s]) for s in dic])
        if total == 0:
            total = 1

        return round(100 * int(dic[stat]) / total, 2)


def setup(client):
    client.add_cog(Stats(client))
