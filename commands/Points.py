#!/usr/bin/env python

"""This file holds all the commands that are relevant for giving and checking a user's points."""

__author__ = "Bradon Lodwick"
__credits__ = ["Bradon Lodwick"]
__version__ = "1.0.0"
__maintainer__ = "Bradon Lodwick"
__email__ = "bradonlodwick22@gmail.com"
__status__ = "Production"

from discord.ext import commands

from score_bot.DatabaseHelper import DatabaseHelper, Results


class Points:
    """Commands that focus on giving and checking members points/scores."""

    def __init__(self, bot):
        """Constructs this file's command class."""

        self.bot = bot
        # Also constructs a database helper for the class
        self.db = DatabaseHelper()

    @commands.command(pass_context=True)
    async def give_point(self, ctx, value, category, receiver_mention):
        """Gives a point to the specified user.
        Example use: s!give_point 3 meme @Score Bot"""

        # Check to make sure only 1 member was mentioned
        if len(ctx.message.mentions) != 1:
            await ctx.message.channel.send("You must specify 1 and only 1 person to receive the message by mentioning "
                                           "them.")
            return
        # Set the receiver to the mentioned member
        else:
            receiver = ctx.message.mentions[0]

        result = self.db.give_point(ctx.guild, ctx.author, receiver, category=category, value=value)
        if result == Results.UNAUTHORIZED:
            await ctx.message.channel.send("You are unauthorized to give users points! You must be an admin or apart "
                                           "of the server's judge role.")
        elif result == Results.ERROR:
            await ctx.message.channel.send("There was an error giving your point.")
        elif result == Results.SUCCESS:
            await ctx.message.channel.send("Congrats {}, you got {} points in the {} category!"
                                           .format(receiver.mention, value, category))


def setup(bot):
    """Used to load this file's commands into the bot.

    Parameters
    ----------
    bot (:obj: discord.ext.commands.Bot): The bot to add the commands to.
    """

    bot.add_cog(Points(bot))
