from kannax import Message, get_collection, kannax
from telegraph import upload_file

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
        "flags": {"-d": "Delete test", "-v": "Ver test", "-a": "Send Animation"},
    },
)
async def view_del_ani(message: Message):
    """View or Delete Alive Media"""
    try:
        await send_nekos(message, link)
    except (MediaEmpty, WebpageCurlFailed):
        link = download(link)
        await send_nekos(message, link)
        os.remove(link)
    else:
        await message.err("`Alive Media não está definida.`")


@kannax.on_cmd(
    "deltest",
    about={
        "header": "Delete mídia",
        "description": "Voçê pode voltar para a animação padrão com esse comando",
      },
    allow_channels=False,
)
async def ani_del_pm_media(message: Message):
    _findpma = await SAVED_SETTINGS.find_one({"_id": "ALIVE_MEDIA"})
    if _findpma is None:
        await message.edit("`Você ainda não definiu uma mídia para Alive`")
    else:
        await SAVED.drop()
        await message.edit("`Alive Media excluida`", del_in=3, log=True)

async def send_alive_(message: Message, link: str):
    media = ""
    msg = "ᴏɪ ᴍᴇsᴛʀᴇ, ᴋᴀɴɴᴀx ɪ'ᴛs ᴀʟɪᴠᴇ"
    async for link in SAVED.find():
        media += f"{link['link']}"
    if media.endswith(".gif", ".mp4"):
        #  Bots can't use "unsave=True"
        bool_unsave = not message.client.is_bot
        await message.client.send_animation(
            chat_id=message.chat.id,
            animation=link
        )
    else:
        await message.client.send_photo(
            chat_id=message.chat.id, photo=link
        )