from kannax import Message, get_collection, kannax
from telegraph import upload_file
from pyrogram.errors import MediaEmpty, WebpageCurlFailed

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
    query = message.input_str
    replied = message.reply_to_message
    if replied:
        file = await kannax.download_media(replied)
        iurl = upload_file(file)
        media = f"https://telegra.ph{iurl[0]}"
        await SAVED.update_one(
            {"_id": "ALIVE_MEDIA"}, {"$set": {"link": media}}, upsert=True
        )
        await message.edit("`Alive Media definida com sucesso!`")
    elif query:
        await SAVED.update_one(
                        {"_id": "ALIVE_MEDIA"}, {"$set": {"link": query}}, upsert=True
        )
        await message.edit("`Alive Media definida com sucesso!`")
    else:
        await message.err("Invalid Syntax")


@kannax.on_cmd(
    "vtest",
    about={
        "header": "Alive Media Settings",
    },
)
async def view_del_ani(message: Message):
    _findpma = await SAVED.find_one({"_id": "ALIVE_MEDIA"})
    if _findpma is None:
        return await message.err("`Alive Media não está definida.`")
    media = ""
    msg = "ᴏɪ ᴍᴇsᴛʀᴇ, ᴋᴀɴɴᴀx ɪ'ᴛs ᴀʟɪᴠᴇ"
    async for link in SAVED.find():
        media += f"{link['link']}"
    if media.endswith((".gif", ".mp4")):
        await message.client.send_animation(
            chat_id=message.chat.id,
            animation=media
        )
    else:
        await message.client.send_photo(
            chat_id=message.chat.id, photo=media
        )


@kannax.on_cmd(
    "deltest",
    about={
        "header": "Delete mídia",
        "description": "Voçê pode voltar para a animação padrão com esse comando",
      },
    allow_channels=False,
)
async def ani_del_pm_media(message: Message):
    _findpma = await SAVED.find_one({"_id": "ALIVE_MEDIA"})
    if _findpma is None:
        await message.edit("`Você ainda não definiu uma mídia para Alive`")
    else:
        await SAVED.drop()
        await message.edit("`Alive Media excluida`", del_in=3, log=True)
