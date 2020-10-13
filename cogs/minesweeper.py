from decorators import help
from discord.ext import commands
from enums.help_categories import Category
from functions import checks
import itertools
import random


class Minesweeper(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Don't allow any commands to work when locked
    def cog_check(self, ctx):
        return not self.client.locked

    @commands.command(name="Minesweeper", aliases=["Ms"], usage="[Niveau]*")
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.Games)
    async def minesweeper(self, ctx, difficulty="m"):
        if difficulty[0].lower() not in "emh":
            await ctx.send("Geef een geldige moeilijkheidsgraad op.")
            return

        await ctx.send(self.createGame(difficulty[0].lower()))

    def createGame(self, difficutly):

        # [X, Y, BombCount]
        dimensions = {
            "e": [5, 5, 4],
            "m": [10, 10, 20],
            "h": [13, 13, 35]
        }

        numbers = {
            0: "||:zero:||",
            1: "||:one:||",
            2: "||:two:||",
            3: "||:three:||",
            4: "||:four:||",
            5: "||:five:||",
            6: "||:six:||",
            7: "||:seven:||",
            8: "||:eight:||",
        }

        # Initialize an empty grid
        grid = [[" " for _ in range(dimensions[difficutly][0])] for _ in range(dimensions[difficutly][1])]

        # Generate every possible position on the grid
        positions = set(itertools.product([x for x in range(len(grid))], repeat=2))

        # Place the bombs in the grid randomly
        for i in range(dimensions[difficutly][2]):
            bombPosition = random.choice(list(positions))
            positions.remove(bombPosition)
            grid[bombPosition[0]][bombPosition[1]] = "||:boom:||"

        # Add in the numbers representing the amount of bombs nearby
        for i, row in enumerate(grid):
            for j, cell in enumerate(row):
                if cell == " ":
                    grid[i][j] = numbers[self.countBombs(grid, [i, j])]

        # Reveal the biggest empty space to the player
        self.revealSpaces(grid, self.findBiggestEmptySpace(grid))

        # Join the grid into a string
        li = [" ".join(row) for row in grid]
        return "\n".join(li)

    # Counts the amount of bombs near a given cell
    def countBombs(self, grid, cell):
        positions = [
            [1, -1], [1, 0], [1, 1],
            [0, -1], [0, 1],
            [-1, -1], [-1, 0], [-1, 1]
        ]

        count = 0
        for position in positions:
            if 0 <= cell[0] + position[0] < len(grid) and 0 <= cell[1] + position[1] < len(grid[0]):
                if "boom" in grid[cell[0] + position[0]][cell[1] + position[1]]:
                    count += 1

        return count

    # Finds the biggest spot of 0's on the grid to reveal at the start
    def findBiggestEmptySpace(self, grid):
        spaces = []
        biggest = []

        # Floodfill
        for i, row in enumerate(grid):
            for j, cell in enumerate(row):
                # Only check cells that aren't part of a space yet
                if not any(cell in space for space in spaces) and "zero" in cell:
                    li = [[i, j]]
                    changed = True
                    while changed:
                        changed = False
                        for added in li:
                            neighb = self.neighbours(grid, added)
                            # Add all neighbours that have not yet been added to this space
                            for neighbour in neighb:
                                if neighbour not in li:
                                    li.append(neighbour)
                                    changed = True
                    spaces.append(li)

                    # If it's bigger than the current biggest, make it the new biggest
                    if len(li) > len(biggest):
                        biggest = li
        return biggest

    # Returns all neighbouring cells containing a 0
    def neighbours(self, grid, cell):
        positions = [
            [1, 0],
            [0, -1], [0, 1],
            [-1, 0]
        ]

        neighb = []

        for position in positions:
            if 0 <= cell[0] + position[0] < len(grid) and 0 <= cell[1] + position[1] < len(grid[0]):
                if "zero" in grid[cell[0] + position[0]][cell[1] + position[1]]:
                    neighb.append([cell[0] + position[0], cell[1] + position[1]])
        return neighb

    # Take away the spoiler marks from the biggest empty space to help the player start
    def revealSpaces(self, grid, emptySpaces):
        positions = [
            [1, -1], [1, 0], [1, 1],
            [0, -1], [0, 1],
            [-1, -1], [-1, 0], [-1, 1]
        ]

        for space in emptySpaces:
            grid[space[0]][space[1]] = ":zero:"
            # Reveal all spaces around this one
            for position in positions:
                # Check if the space is not zero & is contained inside the grid & the space hasn't been cut before
                if 0 <= space[0] + position[0] < len(grid) and \
                        0 <= space[1] + position[1] < len(grid[0]) and \
                        "zero" not in grid[space[0] + position[0]][space[1] + position[1]] and \
                        "||" in grid[space[0] + position[0]][space[1] + position[1]]:
                    # Cut the spoiler from this cell
                    grid[space[0] + position[0]][space[1] + position[1]] = grid[space[0] + position[0]][
                                                                               space[1] + position[1]][2:-2]


def setup(client):
    client.add_cog(Minesweeper(client))
