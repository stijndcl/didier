from data import constants
import discord
from discord.ext import commands
from enums.help_categories import categories, getCategory, Category
import json


class HelpCommand(commands.MinimalHelpCommand):
    def __init__(self, **options):
        super().__init__(**options)
        self.ctx = None
        self.target = None
        self.is_mod = False

    # Slightly modifying the original callback in order to
    # allow sending help to DM's & checking for Enums
    # while removing cog help & checking for mentions
    async def command_callback(self, ctx, *, command=None):
        self.ctx = ctx
        self.is_mod = str(ctx.author.id) == constants.myId
        bot = ctx.bot
        if ctx.bot.locked:
            return

        # If mention prefix was used, don't count it as a target
        if ctx.message.content.startswith("<@"):
            ctx.message.mentions = ctx.message.mentions[1:]

        if len(ctx.message.mentions) > 5:
            return await ctx.send("Je kan Help maar naar maximaal 5 mensen doorsturen.")

        # Send help categories
        if command is None:
            return await self.send_bot_help(self.get_bot_mapping())

        # Check if command is a category
        if command.lower() == "mod" and not self.is_mod:
            return await self.send_error_message("Je hebt geen toegang tot deze commando's.")
        category = getCategory(command, self.is_mod)
        if category:
            return await self.send_category_help(category)

        # Cut the mentions out & split based on subcommand
        spl = command.split(" ")
        spl = spl[:len(spl) - len(self.ctx.message.mentions)]

        # A person was mentioned without passing an argument
        if not spl:
            return await self.send_bot_help(self.get_bot_mapping())

        # Turn dic to lowercase to allow proper name searching
        all_commands = dict((k.lower(), v) for k, v in bot.all_commands.items())

        if spl[0].lower() not in all_commands:
            return await self.send_error_message(await self.command_not_found(spl[0]))

        cmd = all_commands[spl[0].lower()]

        # Check if the entered command path exists
        for key in spl[1:]:
            try:
                all_commands = dict((k.lower(), v) for k, v in cmd.all_commands.items())
                if key.lower() not in all_commands:
                    raise AttributeError
                found = all_commands[key.lower()]
            except AttributeError:
                return await self.send_error_message(await self.subcommand_not_found(cmd, key))
            cmd = found

        # Subcommands should have the parent command's category
        temp = cmd
        while temp.parent is not None:
            temp = temp.parent

        # Don't allow non-mods to see mod commands
        try:
            if temp.callback.category == Category.Mod and not self.is_mod:
                return await self.send_error_message("Je hebt geen toegang tot dit commando.")
        except AttributeError:
            return await self.send_error_message("Dit is geen (openbaar) commando.")

        if isinstance(cmd, commands.Group):
            return await self.send_group_help(cmd)
        else:
            return await self.send_command_help(cmd)

    def get_bot_mapping(self):
        return categories(self.is_mod)

    # Sends list of commands in a category
    async def send_category_help(self, category):
        # Get a list of all commands in this category
        category_commands = [command.name if not command.callback.unpack else command
                             for command in self.ctx.bot.commands
                             if hasattr(command.callback, "category") and command.callback.category == category]

        # Unpack any groups that have to be unpacked
        for command in list(category_commands):
            if not isinstance(command, str):
                category_commands.remove(command)
                category_commands.extend([self.get_name(c) for c in self.unpack_group(command)])

        embed = self.create_help_embed(category.value)
        embed.add_field(name="Commands", value="\n".join(sorted(category_commands)))
        for person in await self.get_destination():
            await person.send(embed=embed)

    async def send_bot_help(self, mapping):
        embed = self.create_help_embed("Help")
        embed.add_field(name="Categorieën", value="\n".join(sorted(mapping)))
        await self.ctx.send(embed=embed)

    async def send_command_help(self, command):
        with open("files/help.json", "r") as fp:
            helpFile = json.load(fp)

        try:
            helpDescription = helpFile[self.get_name(command).lower()]
        except KeyError:
            helpDescription = "Indien je dit leest is DJ STIJN vergeten om dit commando in de help page te zetten. Stuur hem een DM om hem eraan te herinneren."

        embed = self.create_help_embed("Help")
        embed.add_field(name=await self.get_command_signature(command),
                        value=await self.add_aliases_formatting(sorted(command.aliases)) + helpDescription)
        for person in await self.get_destination():
            # Can't send to bots
            if person.bot:
                continue

            await person.send(embed=embed)

    async def send_group_help(self, group):
        with open("files/help.json", "r") as fp:
            helpFile = json.load(fp)

        embed = self.create_help_embed(group.name + " Commando's")

        try:
            helpDescription = helpFile[self.get_name(group).lower()]
        except KeyError:
            helpDescription = "Indien je dit leest is DJ STIJN vergeten om dit commando in de help page te zetten. Stuur hem een DM om hem eraan te herinneren."

        embed.add_field(name=await self.get_command_signature(group),
                        value=await self.add_aliases_formatting(sorted(group.aliases)) + helpDescription,
                        inline=False)

        # Signature: Aliases - Usage
        for subcommand in self.unpack_group(group):
            embed.add_field(name=await self.get_command_signature(subcommand),
                            value=await self.add_aliases_formatting(sorted(subcommand.aliases)) +
                                  helpFile[self.get_name(subcommand).lower()], inline=False)

        for person in await self.get_destination():
            # Can't send to bots
            if person.bot:
                continue

            await person.send(embed=embed)

    # Allow mentioning people to send it to them instead
    async def get_destination(self):
        if self.ctx.message.mentions:
            return set(mention for mention in self.ctx.message.mentions if not mention.bot)
        return [self.ctx.author]

    async def command_not_found(self, string):
        return "Er bestaat geen commando met de naam **{}**".format(string)

    async def subcommand_not_found(self, command, string):
        return "**{}** heeft geen subcommando met de naam **{}**.".format(command.name, string)

    async def get_command_signature(self, command):
        return "{} {}".format(self.get_name(command), command.usage if command.usage is not None else "")

    async def add_aliases_formatting(self, aliases):
        return "*Alias: {}*\n".format(", ".join(aliases)) if aliases else ""

    async def send_error_message(self, error):
        embed = discord.Embed(colour=discord.Colour.red())
        embed.set_author(name="Help")
        embed.add_field(name="Error", value=error)
        await self.ctx.author.send(embed=embed)

    def unpack_group(self, group):
        # Create a list of all command objects in this group, in case they aren't hidden, sorted by name
        subcommands = [group.all_commands.get(command) for command in group.all_commands]
        subcommands.sort(key=lambda x: x.name)
        subcommands = filter(lambda x: not x.hidden, subcommands)
        return list(set(subcommands))

    def get_name(self, command):
        return command.qualified_name if command.parents else command.name

    def create_help_embed(self, title):
        embed = discord.Embed(colour=discord.Colour.blue())
        embed.set_author(name=title)
        embed.set_footer(text="Syntax: Didier Help [Categorie] of Didier Help [Commando]")
        return embed


class Help(commands.Cog):
    def __init__(self, client):
        self.client = client
        self._original_help_command = client.help_command
        client.help_command = HelpCommand(command_attrs={"aliases": ["rtfm"]})
        client.help_command.cog = self

    def cog_unload(self):
        self.client.help_command = self._original_help_command


def setup(client):
    client.add_cog(Help(client))
