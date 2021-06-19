# Didier

You bet. The time has come.

### Discord Documentation

[Link to the Discord API docs](https://discordpy.readthedocs.io/en/latest/index.html). When making a command, make sure to check to docs to see if what you're doing is even possible, and if you're providing the right (amount of) parameters. Ask questions in De Zandbak Discord all you want, but at least make an attempt at looking it up first.

### Running Didier

In order to run Didier, simply run `python3 didier.py` in your terminal, or click `run` in PyCharm (green arrow @ top-right, or right-click the file). Make sure you have installed all the required packages in `requirements.txt`.

### Databases

`databases.md` contains info on every database. Using this file you can find out which tables exist, which columns those tables have, and which types of values those columns contain. This should be enough for you to set up a local Postgresql database in order to mess around with & test functions before committing them (guilty).

### Cog Template

When using PyCharm, you can configure [file templates](https://www.jetbrains.com/help/pycharm/using-file-and-code-templates.html) to create blueprints for files. This speeds up the process of creating `Cogs` as you don't have to write the same exact code every single time.

Below is the Cog template you are expected to use when creating new Cogs for Didier, providing both essential and commonly-used imports & functionality. It's possible that you don't need all of the imports, in which case you can obviously remove the obsolete ones.

```python
from data import constants
import discord
from discord.ext import commands
from decorators import help
from enums.help_categories import Category
from functions import checks


class Cog(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Don't allow any commands to work when locked
    def cog_check(self, ctx):
        return not self.client.locked

def setup(client):
    client.add_cog(Cog(client))
```

Replacing the classname `Cog` with the name of your cog.

### Help Categories

Didier uses a custom help command, which classifies certain commands into categories. Discord's default help does this based on `Cogs`, but this would mean some Cogs would be thousands of lines long, defeating the purpose of using them in the first place.

When creating a new Didier command, you can add it to a `Category` by adding a decorator above the function. The example below shows how to add a command to the `Currency` category.

```python
from decorators import help
from discord.ext import commands
from enums.help_categories import Category
from functions import checks

@commands.command(name="Command Name", aliases=["Cn"])
@commands.check(checks.allowedChannels)
@help.Category(Category.Currency)
async def command_name(self, ctx):
    # Command code
    await ctx.send("Command response")
```

This allows commands across multiple Cogs to be classified under the same category in the help page.

### Python Version
Didier uses `Python 3.6.9`. Seeing as updating Python on a Raspberry Pi is a _huge pain_, this will not change. As a result, you are expected to write code that is compatible with this version. When initially creating the PyCharm project, set `3.6.9` as your project interpreter.

### Ignored Files
`ignored.md` contains a list of all ignored files, and what they look like. This way, you can recreate these files locally to test commands that use them. API keys should be stored in `environment variables`. To do so, create a file called `.env` in the root of this repository (which has already been added to `.gitignore`) and make sure the names match.

### FAQ
`faq.md` is always worth taking a look at when you've got a question. Right now this doesn't contain much, as I don't have any questions for myself, but over time this will be expanded upon.

### Useful Links
- [Embed Visualizer](https://leovoel.github.io/embed-visualizer/): Allows for easy creation of embeds, and can generate the code for them (bottom: "Generate Code" -> "discord.py (Python)"). This is helpful when starting out so you can see what you're doing, when you don't really know how Embeds work yet.