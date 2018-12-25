#!/usr/bin/env python

__author__ = "Bradon Lodwick"
__credits__ = ["Bradon Lodwick"]
__version__ = "1.0.0"
__maintainer__ = "Bradon Lodwick"
__email__ = "bradonlodwick22@gmail.com"
__status__ = "Production"

from datetime import datetime
from enum import Enum
from pymongo import MongoClient


class Results(Enum):
    """Used to define the results of the various methods within DatabaseHelper.

    Attributes
    ----------
    SUCCESS (int): Used to signal the method executed successfully as expected.
    UNAUTHORIZED (int): Used to signal the method was unable to complete due to a member not having the needed
    permissions.
    ERROR (int): used to signal the method was unable to complete due to an unexpected error.
    """
    SUCCESS = 1
    UNAUTHORIZED = 2
    ERROR = 3


class DatabaseHelper:
    """
    Database Helper
    ***************
    Controls all of the functions that interact with the database. Changes to the database should occur through this
    class.

    Attributes:
        client (:obj: `pymongo.MongoClient`): The client connection to the database.
        db: The database that holds the scores.
        points_col: The collection that holds all points.
        guild_col: The collection that holds all the guilds and the members within them.

    Data Structure
    ==============

    Points Example
    --------------

    Below is an example of the json you can expect from a single point object. Point objects are not really meant to be
    ever edited. They are stored in order to perform analytics later if it becomes needed.

    {
        _id: unique identifier for the point
        category: a string to represent the category of the point
        guild_id: the discord id of the guild the point was given in
        sender_id: the discord id of the point sender
        receiver_id: the discord id of the point receiver
        value: the integer value of the given point
        date: the date that the point was given
    }

    Guild Example
    --------------

    Below is an example of the json you can expect from a single guild object. The guild contains a list of members with
    an overall score for the members, but for more detailed scores using categories the points collection will be
    needed.

    {
        _id: the discord id of the guild
        admin_role: the discord id of the role that is allowed to make changes, alongside those with admin in the guild
        judge_role: the discord id of the role that is allowed to give points
        members:
            [
                {
                    member_id: the discord id of the member
                    overall_score: the overall score of the member in the guild, or the sum of all category scores
                },
                {
                    member_id: the discord id of the member
                    overall_score: the overall score of the member in the guild, or the sum of all category scores
                }
            ]
    }
    """

    # CONSTANTS START
    DB_NAME = "scoredb"
    # COLLECTION CONSTANTS START
    # GUILD COLLECTION CONSTANT START
    GUILDS_COLLECTION = "guilds"
    GUILDS_ID = "_id"
    GUILDS_ADMIN = "admin_role"
    GUILDS_JUDGE = "judge_role"
    GUILDS_MEMBERS = "members"
    GUILDS_MEMBERS_ID = "member_id"
    GUILDS_MEMBERS_OVERALL_SCORE = "overall_score"
    # GUILD COLLECTION CONSTANT END
    # POINTS COLLECTION CONSTANT START
    POINTS_COLLECTION = "points"
    POINTS_ID = "_id"
    POINTS_CATEGORY = "category"
    POINTS_GUILD_ID = "guild_id"
    POINTS_SENDER_ID = "sender_id"
    POINTS_RECEIVER_ID = "receiver_id"
    POINTS_VALUE = "value"
    POINTS_DATE = "date"
    # POINTS COLLECTION CONSTANT END
    # COLLECTION CONSTANTS END
    # CONSTANTS END

    def __init__(self, host="127.0.0.1", port=27017):
        """Creates a new database helper. Sets all the database and collection information.
        Parameters:
            host (str): The host ip to connect to. Defaults to localhost.
            port (int): The port to connect to. Defaults to mongodb's typical port, 27017.
        """

        self.client = MongoClient(host, port)
        self.db = self.client[self.DB_NAME]
        self.points_col = self.db[self.POINTS_COLLECTION]
        self.guild_col = self.db[self.GUILDS_COLLECTION]

    def setup_guild(self, member, guild, admin_role, judge_role):
        """Sets up a guild by providing it with the the role that will have admin rights for the bot and the role
        members must have to give people points.

        Parameters
        ----------
        member (:obj: discord.Member): The member who gave the command.
        guild (:obj: discord.Guild): The guild to change the settings for.
        admin_role (:obj: discord.Role): The role that is allowed to make changes to the bot. By default if members have
        admin they are able to make changes, this is for if a guild wants to have people manage the bot but not have
        guild admin rights. Use None if you want admins only.
        judge_role (:obj: discord.Role): The role that is allowed to give points. By default only admins can give
        points, but a specific role can be set to be allowed to give points. Use None if you want admins only.
        """

        # TODO Check if member has necessary privileges to perform the setup
        #   (guild admin, or admin role for the score bot)

        # Create the dictionary object to insert/update in the database
        guild_dict = dict()
        # Sets the admin role
        if admin_role is not None:
            guild_dict[self.GUILDS_ADMIN] = admin_role.id
        else:
            guild_dict[self.GUILDS_ADMIN] = None
        # Sets the point giver role
        if judge_role is not None:
            guild_dict[self.GUILDS_JUDGE] = judge_role.id
        else:
            guild_dict[self.GUILDS_JUDGE] = None

        # Upsert the guild values in the database
        self.guild_col.update_one({self.GUILDS_ID: guild.id}, {'$set': guild_dict}, upsert=True)

    def check_admin(self, guild, member):
        """Checks if a member has either admin privileges, or is an admin for the purposes of the score bot.

        Parameters
        ----------
        guild (:obj: discord.Guild): The guild to check the admin role for.
        member (:obj: discord.Member): The member to check privileges for.

        Returns
        -------
        bool True: The member has admin rights for the score bot's purposes.
        bool False: The member does not have admin rights for the score bot's purposes.
        """

        # Check if the member has admin
        if member.guild_permissions.administrator:
            return True
        # Check if user is apart of the admin role
        else:
            # Get the guild's admin role
            guild_query = self.guild_col.find_one({self.GUILDS_ID: guild.id}, {self.GUILDS_ADMIN: 1, self.GUILDS_ID: 0})
            # If the admin role is set, then check to see if it is in the member's role list
            if guild_query is not None and guild_query[self.GUILDS_ADMIN] is not None:
                # Loop through the users roles, and check to see if they match the role id
                for role in member.roles:
                    # Return True if the member is apart of the admin role
                    if role.id == guild_query[self.GUILDS_ADMIN]:
                        return True
            # All checks have failed, they are not authorized
            else:
                return False

    def check_judge(self, guild, member):
        """Checks if a member has judge privileges, or is an admin of the guild.

        Parameters
        ----------
        guild (:obj: discord.Guild): The guild to check the judge role for.
        member (:obj: discord.Member): The member to check privileges for.

        Returns
        -------
        bool True: The member has judge rights.
        bool False: The member does not have judge rights.
        """

        # Check if the member has admin
        if member.guild_permissions.administrator:
            return True
        # Check if user is apart of the judge role
        else:
            # Get the guild's admin role
            guild_query = self.guild_col.find_one({self.GUILDS_ID: guild.id}, {self.GUILDS_ADMIN: 1, self.GUILDS_ID: 0})
            # If the admin role is set, then check to see if it is in the member's role list
            if guild_query is not None and guild_query[self.GUILDS_ADMIN] is not None:
                # Loop through the users roles, and check to see if they match the role id
                for role in member.roles:
                    # Return True if the member is apart of the admin role
                    if role.id == guild_query[self.GUILDS_ADMIN]:
                        return True
            # All checks have failed, they are not authorized
            else:
                return False

    def give_point(self, guild, sender, receiver, category=None, value=1):
        """Gives a point to a member.

        Parameters
        ----------
        guild (:obj: discord.Guild): The guild the point was given in.
        sender (:obj: discord.Member): The member who sent the point.
        receiver (:obj: discord.Member): The member who is to receive the point.
        category (str): The category of the point, if any. Defaults to None.
        value (int): The value associated with the point.

        Returns
        -------
        Returns a Results object that defines the results of the method.
        """

        # Checks who can give points in the guild
        if not self.check_judge(guild, sender):
            return Results.UNAUTHORIZED
        # Give the user the points
        else:
            # Create the point to insert into the points collection
            new_point = dict()
            new_point[self.POINTS_SENDER_ID] = sender.id
            new_point[self.POINTS_RECEIVER_ID] = receiver.id
            new_point[self.POINTS_CATEGORY] = category
            new_point[self.POINTS_VALUE] = value
            new_point[self.POINTS_GUILD_ID] = guild.id
            new_point[self.POINTS_DATE] = datetime.now()
            self.points_col.insert()
            # Go to the user in the server and update their total value that is used for easy reference
            # TODO
            return Results.SUCCESS
