from decorators import help
import discord
from discord.ext import commands
from enums.help_categories import Category
from functions import checks
import requests
import urllib.parse


class QR(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Don't allow any commands to work when locked
    def cog_check(self, ctx):
        return not self.client.locked

    @commands.command(name="QR", usage="[Tekst]")
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.Other)
    async def QR(self, ctx, *link):
        if len(link) != 1:
            await ctx.send(file=discord.File("files/images/ngguuqr.png"))
            await self.client.get_cog("Utils").removeMessage(ctx.message)
        else:
            self.generate("".join(link))
            await ctx.send(file=discord.File("files/images/qrcode.png"))
            self.remove()
            await self.client.get_cog("Utils").removeMessage(ctx.message)

    def generate(self, link):
        fileContent = requests.get(
            "https://image-charts.com/chart?chs=999x999&cht=qr&chl={}&choe=UTF-8&chof=.png".format(
                urllib.parse.quote(link))).content
        with open("files/images/qrcode.png", "wb+") as fp:
            fp.write(fileContent)

    def remove(self):
        import os
        os.remove("files/images/qrcode.png")


def setup(client):
    client.add_cog(QR(client))
