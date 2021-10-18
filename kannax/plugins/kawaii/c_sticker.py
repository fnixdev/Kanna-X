# import from oub-remix to ux by Itachi_HTK/ashwinstr

import os

from kannax import Config, Message, kannax
from kannax.utils import media_to_image


@kannax.on_cmd(
    "imgs",
    about={
        "header": "Converta para imagem",
        "description": "Converta GIF/sticker/vídeo/thumbnail de música em imagem no formato jpg",
        "usage": "{tr}imgs [responda a uma mídia]",
    },
)
async def img(message: Message):
    if not message.reply_to_message:
        await message.edit("Responda a uma mídia...", del_in=5)
        return
    reply_to = message.reply_to_message.message_id
    await message.edit("Convertendo...", del_in=5)
    file_name = "kanna_convert.jpg"
    down_file = os.path.join(Config.DOWN_PATH, file_name)
    if os.path.isfile(down_file):
        os.remove(down_file)
    image = await media_to_image(message)
    await message.reply_photo(image, reply_to_message_id=reply_to)