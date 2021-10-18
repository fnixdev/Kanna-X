#

from pyrogram.errors import YouBlockedUser

from kannax import Message, kannax


@kannax.on_cmd(
    "tss",
    about={
        "header": "Twitter screenshot",
        "description": "Obtenha screenshot de um link twitter",
        "usage": "{tr}tss [link]",
    },
)
async def tss_(message: Message):
    """tss print"""
    link_ = message.input_str 
    bot_ = "TweetShotBot"
    await message.edit("`Processando...`")
    async with kannax.conversation(bot_, timeout=1000) as conv:
        try:
            await conv.send_message(f"{link_}")
        except YouBlockedUser:
            await message.err("Desbloqueie @TweetShotBot primeiro...", del_in=5)
            return
        response = await conv.get_response(mark_read=True)
    file_id = response.photo.file_id
    await message.delete()
    await message.client.send_photo(
                    chat_id=message.chat.id,
                    photo=file_id)