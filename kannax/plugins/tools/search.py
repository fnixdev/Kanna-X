# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Editado por fnixdev

from kannax import Message, kannax


@kannax.on_cmd(
    "s",
    about={"header": "procure comandos no KannaX", "examples": "{tr}s wel"},
    allow_channels=False,
)
async def search(message: Message):
    cmd = message.input_str
    if not cmd:
        await message.err(text="Insira uma palavra para procurar um comando")
        return
    found = [i for i in sorted(list(kannax.manager.enabled_commands)) if cmd in i]
    out_str = "    ".join(found)
    if found:
        out = f"**--Eu encontrei ({len(found)}) comandos para-- : `{cmd}`**\n\n`{out_str}`"
    else:
        out = f"__nenhum comando encontrado para__ : `{cmd}`"
    await message.edit(text=out, del_in=0)
