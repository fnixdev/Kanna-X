# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Editado por fnixdev

__all__ = ['AddTask']

from typing import Callable, Any

from . import RawDecorator


class AddTask(RawDecorator):  # pylint: disable=missing-class-docstring
    def add_task(self, func: Callable[[], Any]) -> Callable[[], Any]:
        """ add tasks """
        self._tasks.append(func)
        return func
