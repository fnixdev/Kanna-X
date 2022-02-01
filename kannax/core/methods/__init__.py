# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Editado por fnixdev

__all__ = ['Methods']

from .chats import Chats
from .decorators import Decorators
from .messages import Messages
from .users import Users
from .utils import Utils


class Methods(Chats, Decorators, Messages, Users, Utils):
    """ kannax.methods """
