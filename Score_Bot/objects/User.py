#!/usr/bin/env python

__author__ = "Bradon Lodwick"
__credits__ = ["Bradon Lodwick"]
__version__ = "1.0.0"
__maintainer__ = "Bradon Lodwick"
__email__ = "bradonlodwick22@gmail.com"
__status__ = "Production"


class User:
    """Represents a User by holding their id and a list of scores they have given and received, as well as a total
    overall score.

    Attributes:
        user_id (int): The discord id of the user.
        score (int): The number of points the user has received overall.
        points_given (:obj:`list` of :obj:`Point`): A list of points that the user has given to other users.
        points_received (:obj:`list` of :obj:`Point`): A list of points that have been given to the user by others.
    """

    def __init__(self, user_id, score, points_given, points_received):
        """Creates a new user.

        Parameters:
            user_id (int): The discord id of the new user.
            score (int): The number of points the user has received overall.
            points_given (:obj:`list` of :obj:`Point`): A list of points that the user has given to other users.
            points_received (:obj:`list` of :obj:`Point`): A list of points that have been given to the user by others.
        """
        self.user_id = user_id
        self.score = score
        self.points_given = points_given
        self.points_received = points_received
