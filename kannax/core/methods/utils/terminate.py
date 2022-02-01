# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Editado por fnixdev

__all__ = ['Terminate']

import asyncio

from ...ext import RawClient


class Terminate(RawClient):  # pylint: disable=missing-class-docstring
    async def terminate(self) -> None:
        """ terminate kannax """
        if not self.no_updates:
            for _ in range(self.workers):
                self.dispatcher.updates_queue.put_nowait(None)
            for task in self.dispatcher.handler_worker_tasks:
                try:
                    await asyncio.wait_for(task, timeout=0.3)
                except asyncio.TimeoutError:
                    task.cancel()
            self.dispatcher.handler_worker_tasks.clear()
        await super().terminate()
