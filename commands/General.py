#!/usr/bin/env python

"""This file holds all the commands that are general to most bots.

TODO
----
* Add invite link command for the bot
"""

__author__ = "Bradon Lodwick"
__credits__ = ["Bradon Lodwick"]
__version__ = "1.0.0"
__maintainer__ = "Bradon Lodwick"
__email__ = "bradonlodwick22@gmail.com"
__status__ = "Production"

from discord.ext import commands

from score_bot.Secrets import invite_link


class General:
    """Commands that every bot should have."""

    def __init__(self, bot):
        """Constructs this file's command class."""

        self.bot = bot

    @commands.command(pass_context=True)
    async def invite(self, ctx):
        """Sends an invite link in the channel the user sent the request in."""

        await ctx.message.channel.send("I wish I could give you a point, but here is an invite link instead!\n{}"
                                       .format(invite_link))


def setup(bot):
    """Used to load this file's commands into the bot.

    Parameters
    ----------
    bot (:obj: discord.ext.commands.Bot): The bot to add the commands to.
    """

    bot.add_cog(General(bot))
