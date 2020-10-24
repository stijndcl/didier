# Creating Commands

The following document shows you how to create new commands, which kwargs to add, and what they do.

Make sure to properly register the appropriate help decorator to each command. More info on help decorators in `readme.md`.

Do _NOT_ create commands outside of `Cogs`!

### Commands

Commands require a set list of kwargs in order to work correctly, and show up in the help page.

- Name: The name of the command, with only the first letter capitalised.
- Aliases: Optional, a list of all aliases the command can have. Make sure to check if the alias already exists (if not, Discord will throw an error when starting the bot.)

    Aliases should only have the first letter capitalised, and be placed in alphabetical order.
- Usage: Optional, only required when the command takes arguments. Show how the command has to be used. Arguments should be placed between \[square brackets\], and optional arguments need an asterisk* after the brackets.
- Hidden: Optional, should only be added when you _don't_ want the command to show up in the help page.
- Ignore_Extra: Optional, should only be used when you don't want the command to be called when too many arguments are passed.

    This defaults to `True`, so if you don't care about extra arguments then adding this is obsolete. Setting this to `False` makes sentences like _Didier Bank is a cool command_ not trigger the `Didier Bank` command.

##### Checks
Further, checks can be added to commands to make sure the function only executes in certain situations. There are already a few [built-in checks](https://discordpy.readthedocs.io/en/latest/ext/commands/api.html?highlight=checks#checks) to do commonly-used  things, but you can easily create your own functions to do this.

New checks should be added to `/functions/checks.py`. Checks are just a basic function that returns `True` or `False`, and takes `ctx` as a parameter.

The example below shows how to create a command that only takes 1 required argument, 1 optional argument, and does not show up in the help page. The `check` makes sure the command does not work in DM's.

```python
def check(ctx):
    return ctx.guild is not None

@commands.command(name="Name", aliases=["N"], usage=["[Arg], [Arg2]*"], hidden=True, ignore_extra=True)
@commands.check(check=check)
async def name(ctx, arg, arg2=None):
    pass
```

### Groups

It's possible that you might want to create subcommands for a certain command. At first glance, you might want to do something like this:

```python
@commands.command()
async def parent_command(ctx, arg):
    if arg == "sub1":
        await sub1()
    elif arg == "sub2":
        await sub2()
    ...

async def sub1():
    pass

async def sub2():
    pass
```

Looking at this you might think that there must be a better way to do this, and there is. The only situation where this type of code will be accepted, is when there are too many possible subcommands to the point where it's not really doable to create all of them (think help & faq categories).
Discord.py has implemented [Command Groups](https://discordpy.readthedocs.io/en/latest/ext/commands/api.html?highlight=group#discord.ext.commands.Group) for this purpose. Groups allow you to register commands to other commands in order to create subcommands (or even subgroups!).

Groups _do_ have a few extra kwargs on top of the usual `Command Kwargs` mentioned above:

- case_insensitive: Indicates whether or not subcommands should be case-insensitive (think `lb dinks` and `lb DINKS`). You are *required* to set this parameter to `True` so Didier will always work case-insensitively.
- invoke_without_command: Indicates whether or not the group command should only execute if no subcommand was found. In most cases, this will be `True`.

The example below shows how to create a group so that `Didier A B D` will execute `b("D")`, but `Didier A C` will execute `a("C")`.

```python
@commands.group(name="A", usage="[Args]", case_insensitive=True, invoke_without_command=True)
async def a(ctx, args):
    print(args)
    # Prints "C"

@a.command(name="B")
async def b(ctx, args):
    print(args)
    # Prints "D"
```

### Unpacking Groups

It's possible that you want to create a group to organise subcommands, but want the subcommands to be listed in the category instead of under the group (or when the Cog and Group have the same name). An example is Didier's `Random` module.

When creating a group without doing anything, the help page will look like this:

    Categories:
        Currency
        ...
        Random (category)
        ...
        
    Help Random (category):
        Random (group)
        
    Help Random (group):
        Random Choice
        ...
        
This requires an unnecessary step to get to the commands (as there's only 1 result), and it would be nicer to have all subcommands list in the category instead. Seeing as the Cog & Group both have the same name, it also feels weird to do this (and would be near impossible to code in a user-friendly way). When the Cog has the same name, you expect all the commands to be right there immediately.

The `Help Decorator` has an optional argument that can do this for you. When registering a group to a category, you can add `unpack=True` in order to accomplish this.

```python
@commands.group(name="Random")
@help.Category(Category.Random, unpack=True)
async def random(self, ctx):
    pass
```

This way, the help page will look like this:

    Random (category):
        Random Choice
        ...

### Testing & Messing Around
In case you want to quickly test 1 line of code, or test a quick idea, you'd have to create an entire Cog just to use once. With the Cog Template this is not _that_ bad, but it's still a bit cumbersome.

For this purpose, there is a Cog called `testCog.py`, with 1 command (`Test()`). Slap your code in there, and use `Didier Test` in Discord. Just remember to never commit these changes (right click in the file manager -> `Git` -> `Rollback`).