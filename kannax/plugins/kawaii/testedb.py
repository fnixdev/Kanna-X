from kannax import Message, get_collection, kannax
from kannax.utils import media_to_image

SAVED = get_collection("TESTE_DB")

async def _init():
    global ALIVE_MEDIA  # pylint: disable=global-statement
    link = await SAVED.find_one({"_id": "ALIVE_MEDIA"})
    if link:
        ALIVE_MEDIA = link["link"]


@kannax.on_cmd(
    "settest",
    about={
        "header": "apenas teste",
    },
)
async def ani_save_media_alive(message: Message):
    """Set Media DB"""
    link = message.input_or_reply_str
    if not link:
        await message.err("Invalid Syntax")
        return
    try:
        await SAVED.update_one(
            {"_id": "ALIVE_MEDIA"}, {"$set": {"link": link}}, upsert=True
        )
    except Exception as e:
        await message.edit(f"Ocorre um erro\n\n{e}")
    else:
        await message.edit("Alive Media definida com sucesso")


@kannax.on_cmd(
    "vtest",
    about={
        "header": "Alive Media Settings",
        "flags": {"-d": "Delete test", "-v": "Ver test", "-a": "Send Animation"},
    },
)
async def view_del_ani(message: Message):
    """View or Delete Alive Media"""
    if not message.flags:
        await message.err("Flag Required")
        return
    media = ""
    async for link in SAVED.find():
        media += f"{link['link']}"
    if media:
        if "-d" in message.flags:
            await SAVED.drop()
            await message.edit("`Alive Media excluída!`")
        if "-v" in message.flags:
            await message.edit(media)
        if "-a" in message.flags:
            await message.client.send_animation(
                  chat_id=message.chat.id,
                  animation=media)
    else:
        await message.err("`Alive Media não está definida.`")