# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Editado por fnixdev

import asyncio
import random

from pyrogram.errors.exceptions import FloodWait

from kannax import Message, kannax


@kannax.on_cmd(
    "type", about={"header": "Simule uma máquina de escrever", "usage": "{tr}type [texto]"}
)
async def type_(message: Message):
    text = message.input_str
    if not text:
        await message.err("entrada não encontrada")
        return
    s_time = 0.1
    typing_symbol = "|"
    old_text = ""
    await message.edit(typing_symbol)
    await asyncio.sleep(s_time)
    for character in text:
        s_t = s_time / random.randint(1, 100)
        old_text += character
        typing_text = old_text + typing_symbol
        try:
            await asyncio.gather(
                message.try_to_edit(typing_text, sudo=False),
                asyncio.sleep(s_t),
                message.try_to_edit(old_text, sudo=False),
                asyncio.sleep(s_t),
            )
        except FloodWait as x_e:
            await asyncio.sleep(x_e.x)
