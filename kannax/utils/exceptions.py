# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Editado por fnixdev


class StopConversation(Exception):
    """raise if conversation has terminated"""


class ProcessCanceled(Exception):
    """raise if thread has terminated"""


class KannaXBotNotFound(Exception):
    """raise if kannax bot not found"""
