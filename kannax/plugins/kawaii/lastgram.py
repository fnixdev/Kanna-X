# by @fnixdev

"""se você não gosta do plugin lastfm pode usar este daqui"""

from pyrogram.errors import YouBlockedUser

from kannax import Message, kannax


@kannax.on_cmd(
    "reg",
    about={
        "header": "SetUser Lastfm",
        "description": "Define seu usuario lastfm (faça primeiro antes de usar ln)",
        "usage": "{tr}reg [username]",
    },
)
async def ln_user_(message: Message):
    """registrar usuario"""
    lguser_ = message.input_str 
    bot_ = "@lastgramrobot"
    async with kannax.conversation(bot_, timeout=1000) as conv:
        try:
            await conv.send_message(f"/reg {lguser_}")
        except YouBlockedUser:
            await message.err("Desbloqueie @@lastgramrobot primeiro...", del_in=5)
            return
        response = await conv.get_response(mark_read=True)
    resp = response.text
    await message.edit(resp.html, parse_mode="html")

@kannax.on_cmd(
    "ln",
    about={
        "header": "Scrobble Lastfm",
        "description": "Oque você esta ouvindo agora",
        "usage": "{tr}ln",
    },
)
async def ln_last_(message: Message):
    """scrobbles lastgram"""
    bot_ = "lastgramrobot"
    async with kannax.conversation(bot_, timeout=1000) as conv:
        try:
            await conv.send_message(f"/ln")
        except YouBlockedUser:
            await message.err("Desbloqueie @lastgramrobot primeiro...", del_in=5)
            return
        response = await conv.get_response(mark_read=True)
    resp = response.text
    await message.edit(resp.html, parse_mode="html")
