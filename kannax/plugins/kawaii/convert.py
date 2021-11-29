# image convert by @fnixdev

from PIL import Image
from kannax import kannax, Message, Config
import os

@kannax.on_cmd(
    "png",
    about={
        "header": "Convert telegram files",
        "usage": "reply {tr}png em alguma foto/sticker",
    },
)
async def convert_(message: Message):
    """convert telegram files"""
    replied = message.reply_to_message
    await message.edit("`Processando...`")
    if not replied:
        return await message.err("`Responda a alguma mídia.`")
    media = await message.reply_to_message.download()
    if not media.endswith((".jpg", ".png", ".bmp", ".tif", ".webp")):
        os.remove(media)
        return await message.err("`Formato não suportado`")
    try:
        await message.edit("`Convertendo...`")
        img = Image.open(media).convert('RGB')
        img.save('converted.png', 'png')
        await message.delete()
        msg = "__Made by [KannaX](https://t.me/fnixsup)__"
        await kannax.send_document(chat_id=message.chat.id, document="converted.png", caption=msg)
    except Exception as e:
        return message.err(e)
    os.remove(media)
    os.remove("converted.png")