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
    {
        _id: discord_guild_id (str)
        admin_role: discord_role_id (str)
        judge_role: discord_role_id (str)
        members:
        [
            {
                member_id: discord_member_id (str)
                received_total: int
                sender_total: int
                category:
                [
                    {
                        name: str
                        received_points: int
                        sent_points: int
                    }
                ]
            }
        ]
    }
    """

    # CONSTANTS START
    DB_NAME = "scoredb"
    # COLLECTION CONSTANTS START
    GUILDS_COLLECTION = "guilds"
    GUILDS_ID = "_id"
    GUILDS_ADMIN = "admin_role"
    GUILDS_JUDGE = "judge_role"
    GUILDS_MEMBERS = "members"
    MEMBERS_ID = "member_id"
    MEMBERS_RECEIVED_TOTAL = "received_total"
    MEMBERS_SENDER_TOTAL = "sender_total"
    MEMBERS_CATEGORY = "category"
    CATEGORY_NAME = "name"
    CATEGORY_RECEIVED_POINTS = "received_points"
    CATEGORY_SENT_POINTS = "sent_points"
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
        self.guilds_coll = self.db[self.GUILDS_COLLECTION]

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

        # Check if member has necessary privileges to perform the setup
        if not self.check_admin(guild, member):
            return Results.UNAUTHORIZED

        else:
            # Create the dictionary object to insert/update in the database
            guild_dict = dict()
            # Sets the admin role
            if admin_role is not None:
                guild_dict[self.GUILDS_ADMIN] = admin_role.id
            # Sets the point giver role
            if judge_role is not None:
                guild_dict[self.GUILDS_JUDGE] = judge_role.id

            # Upsert the guild values in the database
            self.guilds_coll.update_one({self.GUILDS_ID: guild.id}, {'$set': guild_dict}, upsert=True)
            return Results.SUCCESS

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
            guild_query = self.guilds_coll.find_one(
                {self.GUILDS_ID: guild.id}, {self.GUILDS_ADMIN: 1, self.GUILDS_ID: 0})
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
            guild_query = self.guilds_coll.find_one(
                {self.GUILDS_ID: guild.id}, {self.GUILDS_JUDGE: 1, self.GUILDS_ID: 0})
            if guild_query is not None:
                # If the judge role is set, then check to see if it is in the member's role list
                if guild_query[self.GUILDS_JUDGE] is not None:
                    # Loop through the users roles, and check to see if they match the role id
                    for role in member.roles:
                        # Return True if the member is apart of the judge role
                        if role.id == guild_query[self.GUILDS_JUDGE]:
                            return True
                # If no judge is set, then anyone can give a point
                else:
                    return True
            # If the server hasn't been setup, then a user shouldn't be able to give points
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

        # Checks to see if the member can give a point
        if not self.check_judge(guild, sender):
            return Results.UNAUTHORIZED
        # Give the member the point
        else:
            # Overall point increment
            receiver_overall_update = {"$inc": {"{}.$.{}".format(self.GUILDS_MEMBERS, self.MEMBERS_RECEIVED_TOTAL)}}
            self.guilds_coll.update({self.MEMBERS_ID: receiver.id}, receiver_overall_update)
            sender_overall_update = {"$inc": {"{}.$.{}".format(self.GUILDS_MEMBERS, self.MEMBERS_SENDER_TOTAL)}}
            self.guilds_coll.update({self.MEMBERS_ID: sender.id}, sender_overall_update)
            # Category increments if the category was given
            if category is not None:
                receiver_category_update = {
                    "$inc": {"{}.$.{}.{}".format(
                        self.GUILDS_MEMBERS, self.MEMBERS_CATEGORY, self.CATEGORY_RECEIVED_POINTS)}
                }
                self.guilds_coll.update({self.MEMBERS_ID: receiver.id}, receiver_category_update)
                sender_category_update = {
                    "$inc": {"{}.$.{}.{}".format(
                        self.GUILDS_MEMBERS, self.MEMBERS_CATEGORY, self.CATEGORY_SENT_POINTS)}
                }
                self.guilds_coll.update({self.MEMBERS_ID: receiver.id}, sender_category_update)

            return Results.SUCCESS

    def check_score(self, guild, member, category=None):
        """Checks for the member's score in a given category, or their overall score if the category is not given.

        Parameters
        ----------
        guild (:obj: discord.Guild): The guild the member is checking their score from.
        member (:obj: discord.Member): The member to check the score of.
        category (str): The name of the category to check the score of. If None, then the overall score is checked.

        Returns
        -------
        int: The score of the member
        """

        # Perform different queries based on category, but you need to specify the member and server each time
        filter = {
            self.GUILDS_ID: guild.id,
            "{}.$.{}".format(self.GUILDS_MEMBERS, self.MEMBERS_ID): member.id
        }
        if category is not None:
            filter["{}.$.{}.$.{}".format(self.GUILDS_MEMBERS, self.MEMBERS_CATEGORY, self.CATEGORY_NAME)] = category
            return_params = {
                self.GUILDS_ID: 0,
                "{}.$.{}.$.{}".format(self.GUILDS_MEMBERS, self.MEMBERS_CATEGORY, self.CATEGORY_RECEIVED_POINTS): 1
            }
        else:
            return_params = {
                self.GUILDS_ID: 0,
                "{}.$.{}".format(self.GUILDS_MEMBERS, self.MEMBERS_RECEIVED_TOTAL): 1
            }
        # Perform the query
        query = self.guilds_coll.find_one(filter, return_params)

        # TODO change the return value
        return "TODO"
