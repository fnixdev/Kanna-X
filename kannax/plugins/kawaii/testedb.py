#
#

from kannax import Message, get_collection, kannax
from kannax.utils import media_to_image

SAVED = get_collection("TESTE_DB")

async def _init():
    global ALIVE_MEDIA  # pylint: disable=global-statement
    media_alive = await SAVED.find_one({"_id": "ALIVE_MEDIA"})
    if media_alive:
        ALIVE_MEDIA = media_alive["media_data"]

@kannax.on_cmd(
    "settest",
    about={
        "header": "apenas teste",
    },
)
async def ani_save_template(message: Message):
    """Set Media DB"""
    text = message.input_or_reply_str
    if not text:
        await message.err("Invalid Syntax")
        return
    await SAVED.update_one(
        {"_id": "ALIVE_MEDIA"}, {"$set": {"media_data": text}}, upsert=True
    )
    await message.edit("Alive Media definido com sucesso")
