#
#

from kannax import Message, get_collection, kannax
from kannax.utils import media_to_image
from kannax.plugins.utils.telegraph import upload_media_


SAVED = get_collection("TESTE_DB")

async def _init():
    global ALIVE_MEDIA  # pylint: disable=global-statement
    media_alive = await SAVED.find_one({"_id": "ALIVE_MEDIA"})
    if media_alive:
        ALIVE_MEDIA = media_alive["link"]

@kannax.on_cmd(
    "setalive",
    about={
        "header": "apenas teste",
    },
)
async def ani_save_media_alive(message: Message):
    """Set Media DB"""
    replied = message.reply_to_message
    query = message.input_str
    if not link or replied:
        await message.err("Invalid Syntax")
        return 
    if replied.media:
        path = reply.download()
        fk = upload_file(path)
        for x in fk:
          link = "https://telegra.ph" + x
        await SAVED.update_one(
            {"_id": "ALIVE_MEDIA"}, {"$set": {"link": link}}, upsert=True
            )
        await message.edit("Alive Media definida com sucesso")
        return
    else:
      await SAVED.update_one(
            {"_id": "ALIVE_MEDIA"}, {"$set": {"link": query}}, upsert=True
        )
      await message.edit("Alive Media definida com sucesso")
      return


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