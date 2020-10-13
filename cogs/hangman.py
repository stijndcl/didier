from decorators import help
from discord.ext import commands
from enums.help_categories import Category
from functions import checks
import json
import os
import random


def randomWord():
    lineb = random.randrange(os.stat("files/words-dutch.txt").st_size)
    with open("files/words-dutch.txt", encoding="latin-1") as file:
        file.seek(lineb)
        file.readline()
        return file.readline().rstrip().upper()


class Hangman(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Don't allow any commands to work when locked
    def cog_check(self, ctx):
        return not self.client.locked

    @commands.group(name="Hangman", aliases=["Hm"], usage="[Letter]*", case_insensitive=True, invoke_without_command=True)
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.Games)
    async def hangman(self, ctx, letter=None):
        if letter and letter.strip():
            greek = "αβΓγΔδεζηΘθικΛλμνΞξΠπρΣσςτυΦφχΨψΩω"
            if len(letter) == 1 and (letter.isalpha() or letter.isdigit()) and letter not in greek:
                await self.guessLetter(ctx, letter)
            else:
                await ctx.send("Dit is geen geldige letter.")
            return
        await self.gameStatus(ctx)

    async def guessLetter(self, ctx, letter):
        with open("files/hangman.json", "r") as fp:
            file = json.load(fp)

        if letter.upper() in file["guessed"]:
            await ctx.send("Deze letter is al eens geprobeerd.")
            return

        file["guessed"] += letter.upper()

        if letter.upper() not in file["word"]:
            file["guesses"] += 1

        if int(file["guesses"] >= 9):
            await ctx.send(self.endGame(file["word"]))
            return

        with open("files/hangman.json", "w") as fp:
            json.dump(file, fp)

        await self.gameStatus(ctx)

    @hangman.command(name="Start", usage="[Woord]*")
    async def start(self, ctx, *, word=None):
        with open("files/hangman.json", "r") as fp:
            file = json.load(fp)

        # Can't play two games at once
        if file["word"]:
            await ctx.send("Er is al een spel bezig.")
            return

        if word:
            if not all(letter.isalpha() or letter.isdigit() or letter in [" "] for letter in word):
                await ctx.send("Dit is geen geldig woord.")
                return

            # Can only supply your own words in DM
            if str(ctx.channel.type) != "private":
                await ctx.message.delete()
                await ctx.author.send("Het is niet slim om hangman games aan te maken waar iedereen het kan zien."
                                      "\nGebruik dit commando hier zodat niemand het woord op voorhand weet.")
                return

        # Choose a random word when none were passed
        if not word:
            word = randomWord()

        with open("files/hangman.json", "w") as fp:
            json.dump({"guessed": [], "guesses": 0, "word": word}, fp)

        await self.gameStatus(ctx)

    async def gameStatus(self, ctx):
        with open("files/hangman.json", "r") as fp:
            file = json.load(fp)

        if not file["word"]:
            await ctx.send("Er is geen spel bezig.")
            return

        guessed = " ".join(letter for letter in file["guessed"] if letter not in file["word"])
        filled = self.fillWord(file)

        if filled.replace(" ", "") == file["word"]:
            self.clearGame()
            await ctx.send("**Het woord is geraden.**")
            await ctx.message.add_reaction("✅")
            return

        await ctx.send("{}\n{}\nFoute letters: {}".format(filled, self.hangManString(file["guesses"]), guessed))

    @hangman.command(name="Guess", usage="[Woord]")
    async def guess(self, ctx, *, word=None):
        if not word:
            await ctx.send("Geef een woord op.")
            return

        with open("files/hangman.json", "r") as fp:
            file = json.load(fp)

        if not file["word"]:
            await ctx.send("Er is geen spel bezig.")
            return

        if word.upper() == file["word"].upper():
            self.clearGame()
            await ctx.send("**Het woord is geraden**")
            await ctx.message.add_reaction("✅")
        else:
            file["guesses"] += 1
            await ctx.send("**{}** is een foute gok.".format(word))
            await ctx.message.add_reaction("❌")
            if file["guesses"] >= 9:
                await ctx.send(self.endGame(file["word"]))
            else:
                with open("files/hangman.json", "w") as fp:
                    json.dump(file, fp)
                await self.gameStatus(ctx)

    # Create a representation of the word by filling in letters that have been guessed, and dots otherwise
    def fillWord(self, file):
        return "**" + " ".join(
            letter if letter in file["guessed"] else "." if letter.isalpha() or letter.isdigit() else letter for letter
            in file["word"]) + "**"

    def endGame(self, word):
        self.clearGame()
        return self.hangManString(9) + "\nHet woord was **{}**.".format(word)

    def clearGame(self):
        with open("files/hangman.json", "w") as fp:
            json.dump({"guessed": [], "guesses": 0, "word": ""}, fp)

    def hangManString(self, number):
        dic = {
            0: "\n    \n    \n    \n",
            1: "\n    \n    \n    \n ===",
            2: "\n    |\n    |\n    |\n ===",
            3: "--+---+\n    |\n    |\n    |\n ===",
            4: "--+---+\n    |     O\n    |\n    |\n ===",
            5: "--+---+\n    |     O\n    |      |\n    |\n ===",
            6: "--+---+\n    |     O\n    |    /|\n    |\n ===",
            7: "--+---+\n    |     O\n    |    /|\\\n    |\n ===",
            8: "--+---+\n    |     O\n    |    /|\\\n    |    /\n ===",
            9: "--+---+\n    |     O\n    |    /|\\\n    |    / \\\n ===",
        }
        return dic[number]


def setup(client):
    client.add_cog(Hangman(client))
