# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Editado por fnixdev

__all__ = ['Utils']

from .get_logger import GetLogger
from .get_channel_logger import GetCLogger
from .restart import Restart
from .terminate import Terminate


class Utils(GetLogger, GetCLogger, Restart, Terminate):
    """ methods.utils """
