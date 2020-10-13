from decorators import help
from discord.ext import commands
from enums.help_categories import Category
import requests


class Words(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Don't allow any commands to work when locked
    def cog_check(self, ctx):
        return not self.client.locked

    @commands.command(name="Adjective", aliases=["Adj", "Adjectives"], usage="[Woord]")
    @help.Category(category=Category.Words)
    async def adjective(self, ctx, word=None):
        await self.getData(ctx, word, "rel_jjb")

    @commands.command(name="Synonym", aliases=["Syn", "Synonyms"], usage="[Woord]")
    @help.Category(category=Category.Words)
    async def synonym(self, ctx, word=None):
        await self.getData(ctx, word, "rel_syn")

    @commands.command(name="Antonym", aliases=["Ant", "Antonyms", "Opp", "Opposite"], usage="[Woord]")
    @help.Category(category=Category.Words)
    async def antonym(self, ctx, word=None):
        await self.getData(ctx, word, "rel_ant")

    @commands.command(name="Rhyme", aliases=["Rhymes"], usage="[Woord]")
    @help.Category(category=Category.Words)
    async def rhyme(self, ctx, word=None):
        await self.getData(ctx, word, "rel_rhy")

    # Contacts the API & returns the response, as these commands all do the same anyways
    async def getData(self, ctx, word, relation):
        if not word:
            await ctx.send("Geef een woord op.")
            return

        res = requests.get("https://api.datamuse.com/words?{}={}".format(relation, word)).json()

        # Only show top 20 results
        res = res if len(res) <= 15 else res[:15]

        # Pull the words out of the dicts
        res = [word["word"] for word in res]
        await ctx.send(", ".join(res) if len(res) > 0 else "Geen resultaten gevonden.")


def setup(client):
    client.add_cog(Words(client))
