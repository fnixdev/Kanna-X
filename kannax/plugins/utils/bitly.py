""" Url encurtador """

# By @Krishna_Singhal
#
#editado por @fnixdev

import gdshortener

from pyrogram.errors import YouBlockedUser
from kannax import kannax, Message
from kannax.utils.exceptions import StopConversation


@kannax.on_cmd("bitly", about={
    'header': "Encurtador de links usando bit.ly",
    'usage': "{tr}bitly [link ou responda a um link]"}, allow_via_bot=False)
async def bitly(msg: Message):
    url = msg.input_or_reply_str
    if not url:
        await msg.err("Bruh, preciso de um URL para encurtar")
        return
    try:
        async with kannax.conversation("Sl_BitlyBot") as conv:
            await conv.send_message("/start")
            await conv.get_response(mark_read=True)
            await conv.send_message(url)
            shorten_url = (
                await conv.get_response(mark_read=True)
            ).text.split('\n', maxsplit=1)[-1]
            await msg.edit(f"`{shorten_url}`", disable_web_page_preview=True)
    except YouBlockedUser:
        await msg.edit("desbloqueie **@Sl_BitlyBot** para encurtar URLs.")
    except StopConversation:
        await msg.err("bot is down")


@kannax.on_cmd("isgd", about={
    'header': "Encurtador de links usando is.gd",
    'usage': "{tr}isgd [link ou responda a um link]"})
async def is_gd(msg: Message):
    url = msg.input_or_reply_str
    if not url:
        await msg.err("Bruh, preciso de um URL para encurtar")
        return
    s = gdshortener.ISGDShortener()
    try:
        s_url, stats = s.shorten(url, log_stat=True)
    except Exception as er:
        await msg.err(str(er))
    else:
        await msg.edit(
            f"**URL Encurtado:**\n`{s_url}`\n\n**Status:** `{stats}`",
            disable_web_page_preview=True
        )
