#!/usr/bin/env python

__author__ = "Bradon Lodwick"
__credits__ = ["Bradon Lodwick"]
__version__ = "1.0.0"
__maintainer__ = "Bradon Lodwick"
__email__ = "bradonlodwick22@gmail.com"
__status__ = "Production"


class Point:
    """A point that has been given to a user. The point may be of any value, given from one user to another.

    Attributes:
        point_id (int): The arbitrary id of the point used for storage in the database.
        value (int): The value the point holds.
        category (str): The category of the point.
        giver_id (int): The discord id of the user that gave the point.
        receiver_id (int): The discord id of the user that received the point.
    """

    def __init__(self, point_id, value, category, giver_id, receiver_id):
        """Creates a new point object.

        Parameters:
            point_id (int): The arbitrary id of the point used for storage in the database.
            value (int): The value the point holds.
            category (str): The category of the point.
            giver_id (int): The discord id of the user that gave the point.
            receiver_id (int): The discord id of the user that received the point.
        """
        self.point_id = point_id
        self.value = value
        self.category = category
        self.giver_id = giver_id
        self.receiver_id = receiver_id
