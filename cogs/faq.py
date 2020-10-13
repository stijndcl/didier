from decorators import help
import discord
from discord.ext import commands
from enums.help_categories import Category
from functions import stringFormatters, checks
from functions.database import faq


class Faq(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Don't allow any commands to work when locked
    def cog_check(self, ctx):
        return not self.client.locked

    @commands.group(name="FAQ", usage="[Categorie]* [@Personen]*", case_insensitive=True, invoke_without_command=True)
    @help.Category(category=Category.Other)
    async def faq(self, ctx, *args):
        """
        Command group that controls the FAQ commands.
        When this command is invoked, it sends a list of valid categories.
        :param ctx: Discord Context
        :param args: args passed
        """
        # A category was requested
        # This is not the cleanest but 80 subcommands is a bit much
        if len(args) != 0 and any("@" not in arg for arg in args):
            return await self.faqCategory(ctx, args)

        # List of all categories with the first letter capitalized
        resp = [stringFormatters.titleCase(cat[0]) for cat in faq.getCategories()]

        # Sort alphabetically
        resp.sort()

        # Create an embed with all the categories
        embed = discord.Embed(colour=discord.Colour.blue())
        embed.set_author(name="FAQ Categorieën")
        embed.description = "\n".join(resp)

        # Check if the embed has to be sent to the user
        # or if the user tagged anyone
        if len(ctx.message.mentions) == 0:
            await ctx.author.send(embed=embed)
        else:
            embed.set_footer(text="Doorgestuurd door {}".format(ctx.author.display_name))
            # Send it to everyone that was mentioned
            for person in ctx.message.mentions:
                if not person.bot:
                    await person.send(embed=embed)

    @faq.command(hidden=True, name="Add", usage="[Category] [Question]* [Answer]*")
    @commands.check(checks.isMe)
    async def add(self, ctx, category, question=None, answer=None, answer_markdown=None):
        """
        Command to add a FAQ to the database
        :param ctx: Discord Context
        :param category: the category to add the FAQ to
        :param question: the question
        :param answer: the answer
        :param answer_markdown: a version of the answer with markdown applied
        """
        # Add a new category
        if question is None or answer is None:
            faq.addCategory(category)
            await ctx.send("**{}** is toegevoegd.".format(category))
        else:
            # Add a new question/answer couple to a category
            faq.addQuestion(category, question, answer, answer_markdown)
            await ctx.send("``{}\n{}`` is toegevoegd in {}.".format(question, answer, category))

    # Quotes a specific line of the fac instead of DM'ing the entire thing
    @faq.command(name="Quote", aliases=["Q"], usage="[Categorie] [Index]")
    @help.Category(category=Category.Other)
    async def quote(self, ctx, category, index):
        """
        Command that quotes 1 line of the FAQ into the current channel.
        :param ctx: Discord Context
        :param category: the category of the FAQ
        :param index: the index in the list  to quote
        :return:y
        """
        # Check if a (valid) number was passed
        try:
            index = int(index)
            if index < 1:
                raise ValueError
        except ValueError:
            await ctx.send("Dit is geen geldig getal.")

        # Create a list of categories
        categories = [t[0] for t in faq.getCategories()]

        # Check if a valid category was passed
        if category.lower() not in categories:
            return await ctx.send("Dit is geen geldige categorie.")

        resp = faq.getCategory(category.lower())

        # Check if this index exists in this category
        if len(resp) < index:
            return await ctx.send("Dit is geen geldig getal.")

        # Sort by entry Id
        resp.sort(key=lambda x: int(x[0]))

        await ctx.send("**{}**\n{}".format(resp[index - 1][2], resp[index - 1][3]))

    async def faqCategory(self, ctx, args):
        """
        Function that sends everything from a category.
        :param ctx: Discord Context
        :param args: the args passed
        """

        # Create a list of categories
        categories = [t[0] for t in faq.getCategories()]

        # Random word was passed as a category
        if not any(arg.lower() in categories for arg in args):
            return await self.sendErrorEmbed(ctx, "Dit is geen geldige categorie.")
        elif len(args) - len(ctx.message.mentions) != 1:
            # Multiple categories were requested, which is not allowed
            return await self.sendErrorEmbed(ctx, "Controleer je argumenten.")

        category = ""

        # Find the category the user requested
        for word in args:
            if word.lower() in categories:
                category = word
                break

        resp = faq.getCategory(category.lower())

        # Sort by entry Id
        resp.sort(key=lambda x: int(x[0]))

        embed = discord.Embed(colour=discord.Colour.blue())
        embed.set_author(name="FAQ {}".format(stringFormatters.titleCase(category)))

        # Add everything into the embed
        for i, pair in enumerate(resp):
            # Add custom markdown if it exists
            embed.add_field(name="#{}: {}".format(str(i + 1), pair[2]), value=pair[3] if pair[4] is None else pair[4], inline=False)

        # Check if anyone was tagged to send the embed to
        if len(ctx.message.mentions) == 0:
            await ctx.author.send(embed=embed)
        else:
            embed.set_footer(text="Doorgestuurd door {}".format(ctx.author.display_name))
            # Author tagged some people to send it to
            for person in ctx.message.mentions:
                await person.send(embed=embed)

    async def sendErrorEmbed(self, ctx, message: str):
        """
        Function that sends an error embed.
        :param ctx: Discord Context
        :param message: the message to put in the embed
        """
        embed = discord.Embed(colour=discord.Colour.red())
        embed.set_author(name="Error")
        embed.description = message
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Faq(client))
