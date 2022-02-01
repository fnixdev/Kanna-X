# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Editado por fnixdev

__all__ = ["ROOT", "get_all_plugins"]

import sys
from os.path import dirname
from typing import List

from kannax import logging
from kannax.utils import get_import_path

_LOG = logging.getLogger(__name__)
ROOT = dirname(__file__)


def get_all_plugins() -> List[str]:
    """list all plugins"""
    plugins = get_import_path(
        ROOT, "/dev/" if len(sys.argv) == 2 and sys.argv[1] == "dev" else "/**/"
    )
    _LOG.debug("Todos os plug-ins disponíveis: %s", plugins)
    return list(plugins)

