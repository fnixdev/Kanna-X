# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Editado por fnixdev

__all__ = ['get_collection']

import asyncio
from typing import List

from motor.motor_asyncio import AsyncIOMotorClient
from motor.core import AgnosticClient, AgnosticDatabase, AgnosticCollection

from kannax import logging, Config, logbot

_LOG = logging.getLogger(__name__)
_LOG_STR = "$$$>>> %s <<<$$$"

logbot.edit_last_msg("Conectando-se a Database ...", _LOG.info, _LOG_STR)

_MGCLIENT: AgnosticClient = AsyncIOMotorClient(Config.DB_URI)
_RUN = asyncio.get_event_loop().run_until_complete

if "KannaX" in _RUN(_MGCLIENT.list_database_names()):
    _LOG.info(_LOG_STR, "Banco de dados KannaX encontrado :) => Agora logando nele...")
else:
    _LOG.info(_LOG_STR, "Banco de dados KannaX não encontrado :( => Criando nova Database...")

_DATABASE: AgnosticDatabase = _MGCLIENT["KannaX"]
_COL_LIST: List[str] = _RUN(_DATABASE.list_collection_names())


def get_collection(name: str) -> AgnosticCollection:
    """ Criar ou obter coleção de seu banco de dados """
    if name in _COL_LIST:
        _LOG.debug(_LOG_STR, f"{name} Coleção encontrada :) => Agora logando nela...")
    else:
        _LOG.debug(_LOG_STR, f"{name} Coleção não encontrada :( => Criando nova coleção...")
    return _DATABASE[name]


def _close_db() -> None:
    _MGCLIENT.close()


logbot.del_last_msg()
