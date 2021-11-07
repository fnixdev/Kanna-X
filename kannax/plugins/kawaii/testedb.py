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


@kannax.on_cmd(
    "vtest",
    about={
        "header": "Anime Media Settings",
        "flags": {"-d": "Delete test", "-v": "Ver test"},
        "usage": "{tr}anitemp [A valid flag]",
    },
)
async def view_del_ani(message: Message):
    """View or Delete Alive Media"""
    if not message.flags:
        await message.err("Flag Required")
        return
    template = await SAVED.find_one({"_id": "ALIVE_MEDIA"})
    if not template:
        await message.err("`Nenhuma media salva`")
        return
    if "-d" in message.flags:
        await SAVED.delete_one({"_id": "ALIVE_MEDIA"})
        await message.edit("`Alive Media excluida com sucesso`")
    if "-v" in message.flags:
        media = media_alive["alive_data"]
        texto = f"testando"
        await message.reply_animation(animation=media,
                                          caption=texto)