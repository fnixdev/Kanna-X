# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Editado por fnixdev

__all__ = ['Messages']

from .send_message import SendMessage
from .edit_message_text import EditMessageText
from .send_as_file import SendAsFile


class Messages(SendMessage, EditMessageText, SendAsFile):
    """ methods.messages """
