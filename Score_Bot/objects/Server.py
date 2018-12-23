#!/usr/bin/env python

__author__ = "Bradon Lodwick"
__credits__ = ["Bradon Lodwick"]
__version__ = "1.0.0"
__maintainer__ = "Bradon Lodwick"
__email__ = "bradonlodwick22@gmail.com"
__status__ = "Production"


class Server:
    """Represents a server, holding all of it's settings and a list of users within it.

    Attributes:
        server_id (int): The discord id of the server.
        admin_role (int): The discord id of the admin role that is allowed to change the settings of the server.
        If the value is None, then only users with admin are able to make changes.
        point_role (int): The discord id of the role that is allowed to give points. If the value is None, then any user
        may give points.
        users (:obj:`list` of :obj:`User`): The list of users that have scores recorded.
    """

    def __init__(self, server_id, admin_role, point_role, users):
        """Constructs a new server object with all given information.

        Parameters:
              server_id (int): The discord id of the server to be created.
              admin_role (int): The discord id of the admin role in the new server. If set to None, only users who have
              admin may change settings.
              point_role (int): The discord id of the role that is allowed to give points. If the value is None, then
              any user may give points.
              users (:obj:`list` of :obj:`User`): The list of users that have scores recorded.
        """
        self.server_id = server_id
        self.admin_role = admin_role
        self.point_role = point_role
        self.users = users
