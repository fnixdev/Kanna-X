# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Editado por fnixdev

__all__ = ['GetCLogger']

import inspect

from kannax import logging
from ...ext import RawClient
from ... import types

_LOG = logging.getLogger(__name__)
_LOG_STR = "<<<!  #####  %s  #####  !>>>"


class GetCLogger(RawClient):  # pylint: disable=missing-class-docstring
    # pylint: disable=invalid-name
    def getCLogger(self, name: str = '') -> 'types.new.ChannelLogger':
        """ This returns new channel logger object """
        if not name:
            name = inspect.currentframe().f_back.f_globals['__name__']
        _LOG.debug(_LOG_STR, f"Creating CLogger => {name}")
        return types.new.ChannelLogger(self, name)
