#!/usr/bin/env python

"""This file is to be ran in order to start the bot."""

__author__ = "Bradon Lodwick"
__credits__ = ["Bradon Lodwick"]
__version__ = "1.0.0"
__maintainer__ = "Bradon Lodwick"
__email__ = "bradonlodwick22@gmail.com"
__status__ = "Production"

from discord.ext import commands
import glob

from score_bot import Secrets

# Setup the bot
bot = commands.Bot(command_prefix="s!", description="A bot made to keep track of points given to users")


@bot.event
async def on_ready():
    """Prints out information when the bot is started."""

    # Prints out bot information
    print('--------------------')
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('--------------------')

if __name__ == "__main__":
    print("START COMMAND SETUP\n-------------------")
    # Load all of the command extensions from the commands folder by looping through .py files
    commands_path = "commands/"
    for file in glob.glob("{}*.py".format(commands_path)):
        # Ignore the __init__.py file
        if not file.endswith("__init__.py"):
            # Converts the file name to the acceptable string for the load_extension method
            file = file.rstrip('.py')  # Strips the .py extension
            file = file.replace('/', '.')  # Replaces the /'s in the path with .'s
            file = file.replace('\\', '.')  # Replaces the \'s in the path with .'s
            # Tries to load the given extension
            try:
                bot.load_extension(file)
                print("Loaded the {} extension".format(file))
            # Handles errors loading the extension
            except ModuleNotFoundError as e:
                exc = '{}: {}'.format(type(e).__name__, e)
                print('Failed to load extension {}.\n{}'.format(file, exc))
    print("Command setup phase complete.\n")

    # Runs the bot
    bot.run(Secrets.token)
